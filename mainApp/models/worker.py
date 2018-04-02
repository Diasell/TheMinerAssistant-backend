import requests, datetime

from django.db import models
from django.contrib.auth.models import User

from mainApp.utils.helperfunctions import get_pool_avg_hashrate


class WorkerModel(models.Model):
    """
    Worker Model.
    """

    nano_id = models.CharField(verbose_name=u"NanoID", max_length=100)
    ideal_hashrate = models.FloatField(verbose_name=u"IdealHashRate", default=0.0)

    active = models.BooleanField(verbose_name=u"IsActive", default=True)
    name = models.CharField(
        verbose_name=u"Worker Name",
        blank=True,
        max_length=25
    )
    teamviewer = models.CharField(
        verbose_name=u"Worker TeamViewerID",
        blank=True,
        max_length=25
    )
    pool = models.ForeignKey(u'PoolModel', verbose_name=u"Works For Pool", on_delete=models.CASCADE)


    possible_reboot_condition = models.BooleanField(verbose_name=u"In reboot", default=False)
    reboot_count = models.IntegerField(verbose_name=u"Reboot Count", default=0)
    last_reboot_time = models.DateTimeField(verbose_name=u"Last Reboot Time", blank=True, null=True)


    is_down = models.BooleanField(verbose_name=u"Down Status", default=False)


    def __str__(self):
        return  u"Worker: %s" % self.name


class WorkerDownTime(models.Model):

    worker = models.ForeignKey(u"WorkerModel", verbose_name=u"worker", on_delete=models.CASCADE)
    started = models.DateTimeField(verbose_name=u"Downtime started")
    ended = models.DateTimeField(verbose_name=u"Downtime ended", blank=True, null=True)
    active = models.BooleanField(verbose_name="Active", default=True)


class WorkerStats(models.Model):

    worker = models.ForeignKey(u'WorkerModel',  verbose_name=u"Worker", on_delete=models.CASCADE)
    last_share = models.DateTimeField(verbose_name=u"Last Share Time")
    hashrate = models.FloatField(verbose_name=u"HashRate", default=0.0)
    avg_h1 = models.FloatField(verbose_name=u"Average hour rate", default=0.0)
    avg_h3 = models.FloatField(verbose_name=u"Average 3h rate", default=0.0)
    avg_h6 = models.FloatField(verbose_name=u"Average 6h rate", default=0.0)
    avg_h12 = models.FloatField(verbose_name=u"Average 12h rate", default=0.0)
    avg_h24 = models.FloatField(verbose_name=u"Average daily rate", default=0.0)

    def save(self, *args, **kwargs):

        if self.id:
            if self.hashrate == 0:
                worker_is_down_check(self)
            elif self.hashrate < self.worker.ideal_hashrate/2:
                worker_low_hashrate_check(self)
            else:
                worker_is_fine(self)
            super().save(*args, **kwargs)
        else:
            # Fisrt time object created only worker id and pool passed to constructor
            # so no need to check for hashrate
            super().save(*args, **kwargs)

    def __str__(self):
        return u"Worker: %s" % self.worker.name



class PoolModel(models.Model):
    """
    Pool Model
    """

    address = models.CharField(
        verbose_name=u"NanoPool Address",
        blank=False,
        max_length=100
    )
    name = models.CharField(
        verbose_name=u"Pool Name",
        max_length=100
    )
    hashrate = models.FloatField(verbose_name=u"Pool HashRate", default=0.0)
    avg_hasrate = models.FloatField(verbose_name=u"Pool Avg Rate", default=0.0)
    balance = models.FloatField(verbose_name=u"Pool Balance", default=0.0)
    unconfirmed_balance = models.FloatField(verbose_name=u"Unconfirmed Balance", default=0.0)
    users = models.ManyToManyField(User, related_name='pool', verbose_name="Allowed Users")

    def save(self, *args, **kwargs):

        if  not self.id:
            r = requests.get(f"https://api.nanopool.org/v1/eth/user/{self.address}")
            reply = r.json()
            if reply['status']:
                self.hashrate = reply['data']['hashrate']
                self.balance = reply['data']['balance']
                self.unconfirmed_balance = reply['data']['unconfirmed_balance']
                self.avg_hasrate = get_pool_avg_hashrate(reply['data']["avgHashrate"])
            super().save(*args, **kwargs)

            workers_list = reply['data']['workers']
            create_workers(workers_list, self.address)
        else:
            super().save(*args, **kwargs)


    def __str__(self):
        return "Pool: %s" % self.name



def create_workers(worker_list, pool):

    for worker in worker_list:
        hashrate = float(worker['hashrate'])
        new_worker = WorkerModel(
            active=hashrate>0,
            name=worker['id'],
            nano_id=worker['uid'],
            pool=PoolModel.objects.get(address=pool),
        )
        new_worker.save()
        create_worker_stats(worker, new_worker)

def create_worker_stats(worker_stats, worker_obj):

    stats = WorkerStats(
        worker=worker_obj,
        last_share=datetime.datetime.fromtimestamp(worker_stats['lastshare']),
        hashrate=float(worker_stats['hashrate']),
        avg_h1=float(worker_stats['h1']),
        avg_h3=float(worker_stats['h3']),
        avg_h6=float(worker_stats['h6']),
        avg_h12=float(worker_stats['h12']),
        avg_h24=float(worker_stats['h24'])
    )
    stats.save()


def worker_is_down_check(worker_stats_obj):
    worker = worker_stats_obj.worker
    worker_stats = WorkerStats.objects.filter(worker=worker)
    if len(worker_stats) >= 2:
        latest = WorkerStats.objects.filter(worker=worker).order_by('-last_share')[1]
        if latest.hashrate == 0:
            # worker seems to be down user should be notified
            # TODO: implement user notification
            print(worker.name + " is down")
            worker.is_down = True
            worker.possible_reboot_condition = False
            down_time = WorkerDownTime(worker=worker, started=latest.last_share)
            down_time.save()
        else:
            # worker in possible reboot state
            print(worker.name + " in possible reboot")
            worker.possible_reboot_condition = True
            worker.reboot_count += 1
            worker.last_reboot_time = worker_stats_obj.last_share

        worker.save()
    else:
        pass


def worker_low_hashrate_check(worker_stats_obj):
    worker = worker_stats_obj.worker
    print("checking low hashrate for " + worker.name)


def worker_is_fine(worker_stats_obj):
    worker = worker_stats_obj.worker
    worker.is_down = False
    worker.possible_reboot_condition = False
    down_time = WorkerDownTime.objects.filter(worker = worker, active=True)
    if down_time:
        down_time[0].ended = worker_stats_obj.last_share
        down_time[0].active = False
        down_time[0].save()
    worker.save()



