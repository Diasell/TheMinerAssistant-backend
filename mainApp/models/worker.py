from django.db import models
from django.contrib.auth.models import User


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

    worker = models.ForeignKey(u'WorkerModel',  verbose_name=u"Worker", on_delete=models.DO_NOTHING)
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

    def __str__(self):
        return "Pool: %s" % self.name

