from django.db import models

# Create your models here.


class BestvPlayprofile(models.Model):
    ServiceType = models.CharField(max_length=30)
    DeviceType = models.CharField(max_length=255)
    ISP = models.CharField(max_length=255)
    Area = models.CharField(max_length=255)
    Date = models.DateField()
    Records = models.IntegerField()
    Users = models.IntegerField()
    AverageTime = models.IntegerField()

    class Meta:
        db_table = "playprofile"
        unique_together = ('ServiceType', 'DeviceType', 'ISP', 'Area', 'Date')

    def __str__(self):
        return "BestvPlayprofile"


class BestvPlayinfo(models.Model):
    ServiceType = models.CharField(max_length=30)
    DeviceType = models.CharField(max_length=255)
    ISP = models.CharField(max_length=255)
    Area = models.CharField(max_length=255)
    ViewType = models.IntegerField()
    Date = models.DateField()
    Hour = models.IntegerField()
    Records = models.IntegerField()

    class Meta:
        db_table = "playinfo"
        unique_together = (
            'ServiceType', 'DeviceType', 'ISP',
            'Area', 'ViewType', 'Date', 'Hour')

    def __str__(self):
        return "BestvPlayinfo"


class BestvPlaytime(models.Model):
    ServiceType = models.CharField(max_length=30)
    DeviceType = models.CharField(max_length=255)
    ISP = models.CharField(max_length=255)
    Area = models.CharField(max_length=255)
    ViewType = models.IntegerField()
    Date = models.DateField()
    Hour = models.IntegerField()
    P25 = models.IntegerField()
    P50 = models.IntegerField()
    P75 = models.IntegerField()
    P90 = models.IntegerField()
    P95 = models.IntegerField()
    AverageTime = models.IntegerField()

    class Meta:
        db_table = "playtime"
        unique_together = (
            'ServiceType', 'DeviceType', 'ISP',
            'Area', 'ViewType', 'Date', 'Hour')

    def __str__(self):
        return "BestvPlaytime"

class Title(models.Model):
    ServiceType = models.CharField(max_length=30)
    DeviceType = models.CharField(max_length=255)
    Date = models.DateField()
    class Meta:
        unique_together = (
            'ServiceType', 'DeviceType', 'Date',)

class BestvFbuffer(models.Model):
    ServiceType = models.CharField(max_length=30)
    DeviceType = models.CharField(max_length=255)
    ISP = models.CharField(max_length=255)
    Area = models.CharField(max_length=255)
    ViewType = models.IntegerField()
    Date = models.DateField()
    Hour = models.IntegerField()
    SucRatio = models.FloatField()
    P25 = models.IntegerField()
    P50 = models.IntegerField()
    P75 = models.IntegerField()
    P90 = models.IntegerField()
    P95 = models.IntegerField()
    AverageTime = models.IntegerField()

    class Meta:
        db_table = "fbuffer"
        unique_together = (
            'ServiceType', 'DeviceType', 'ISP',
            'Area', 'ViewType', 'Date', 'Hour')

    def __str__(self):
        return "BestvFbuffer"


class BestvFluency(models.Model):
    ServiceType = models.CharField(max_length=30)
    DeviceType = models.CharField(max_length=255)
    ISP = models.CharField(max_length=255)
    Area = models.CharField(max_length=255)
    ViewType = models.IntegerField()
    Date = models.DateField()
    Hour = models.IntegerField()
    Fluency = models.FloatField()
    PRatio = models.FloatField()
    AllPRatio = models.FloatField()
    AvgCount = models.FloatField()

    class Meta:
        db_table = "fluency"
        unique_together = (
            'ServiceType', 'DeviceType', 'ISP',
            'Area', 'ViewType', 'Date', 'Hour')

    def __str__(self):
        return "BestvFluency"

class Bestv3SRatio(models.Model):
    ServiceType = models.CharField(max_length=30)
    DeviceType = models.CharField(max_length=255)
    ISP = models.CharField(max_length=255)
    Area = models.CharField(max_length=255)
    Date = models.DateField()
    Ratio = models.FloatField()

    class Meta:
        db_table = "bestv3sratio"  #Bestv3SRatio
        unique_together = ('ServiceType', 'DeviceType', 'ISP', 'Area', 'Date')

    def __str__(self):
        return "Bestv3SRatio"

class BestvAvgPchoke(models.Model):
    ServiceType = models.CharField(max_length=30)
    DeviceType = models.CharField(max_length=255)
    ISP = models.CharField(max_length=255)
    Area = models.CharField(max_length=255)
    Date = models.DateField()
    AvgCount = models.IntegerField()
    AvgTime = models.IntegerField()

    class Meta:
        db_table = "bestvavgpchoke"  #BestvAvgPchoke
        unique_together = ('ServiceType', 'DeviceType', 'ISP', 'Area', 'Date')

    def __str__(self):
        return "BestvAvgPchoke"