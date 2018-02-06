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
    worker_name = models.CharField(
        verbose_name=u"Worker Name",
        blank=True,
        max_length=25
    )
    worker_teamviewer = models.CharField(
        verbose_name=u"Worker TeamViewerID",
        blank=True,
        max_length=25
    )
    pool = models.ForeignKey(u'PoolModel', verbose_name=u"Works For Pool", on_delete=models.DO_NOTHING)

    first_check_passed = models.BooleanField(verbose_name=u"First Check", default=True)
    second_check_passed = models.BooleanField(verbose_name=u"Second Check", default=True)
    third_check_passed = models.BooleanField(verbose_name=u"Third Check", default=True)

    possible_reboot_condition = models.BooleanField(verbose_name=u"In reboot", default=False)
    reboot_count = models.IntegerField(verbose_name=u"Reboot Count", default=0)
    last_reboot_time = models.DateTimeField(verbose_name=u"Last Reboot Time", blank=True, null=True)
    worker_is_down = models.BooleanField(verbose_name=u"Down Status", default=False)
    down_time_started = models.DateTimeField(verbose_name=u"Last Downtime started", blank=True, null=True)


    def __str__(self):
        return  u"Worker: %s" % self.worker_name


class WorkerStats(models.Model):

    worker = models.ForeignKey(u'WorkerModel',  verbose_name=u"Worker", on_delete=models.CASCADE)
    last_share = models.DateTimeField(verbose_name=u"Last Share Time")
    hashrate = models.FloatField(verbose_name=u"HashRate", default=0.0)
    avg_h1 = models.FloatField(verbose_name=u"Average hour rate", default=0.0)
    avg_h3 = models.FloatField(verbose_name=u"Average 3h rate", default=0.0)
    avg_h6 = models.FloatField(verbose_name=u"Average 6h rate", default=0.0)
    avg_h12 = models.FloatField(verbose_name=u"Average 12h rate", default=0.0)
    avg_h24 = models.FloatField(verbose_name=u"Average daily rate", default=0.0)

    def __str__(self):
        return u"Worker: %s" % self.worker.worker_name



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
    users = models.ManyToManyField(User, verbose_name="Allowed Users")

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
            print("after super")
        else:
            super().save(*args, **kwargs)


    def __str__(self):
        return "Pool: %s" % self.name



def create_workers(worker_list, pool):

    for worker in worker_list:
        hashrate = float(worker['hashrate'])
        new_worker = WorkerModel(
            active=hashrate>0,
            worker_name=worker['id'],
            pool=PoolModel.objects.get(address=pool),
        )
        new_worker.save()
        id = worker['id']
        print(f"adding worker {id}")
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
    print(f"adding stats for {worker_obj.worker_name}")