from django.db import models

# Create your models here.
class VersionInfo(models.Model):
    ServiceType = models.CharField(max_length=30)
    DeviceType = models.CharField(max_length=100)
    VersionType = models.CharField(max_length=50)

    class Meta:
        db_table = "version_info"
        unique_together = ("ServiceType", "DeviceType", "VersionType")

    @classmethod
    def get_version(cls, service_type, device_type, version):
        q = cls.objects.get(ServiceType=service_type, DeviceType=device_type, VersionType=version)
        return q

class TPlayloadingTitle(models.Model):
    VersionId = models.ForeignKey(VersionInfo, on_delete=models.CASCADE)
    Date = models.DateField()
    Records = models.IntegerField()

    class Meta:
        db_table = "tplayloading_title"
        unique_together = ("VersionId", "Date")

class TPlayloadingInfo(models.Model):
    VersionId = models.ForeignKey(VersionInfo, on_delete=models.CASCADE)
    ISP = models.CharField(max_length=255)
    Area = models.CharField(max_length=255)
    ChokeType = models.SmallIntegerField()
    ViewType = models.SmallIntegerField()
    Date = models.DateField()
    Hour = models.SmallIntegerField()
    P25 = models.SmallIntegerField()
    P50 = models.SmallIntegerField()
    P75 = models.SmallIntegerField()
    P90 = models.SmallIntegerField()
    P95 = models.SmallIntegerField()
    Records = models.IntegerField()

    class Meta:
        db_table = "tplayloading_info"
        unique_together = ("VersionId", "ISP", "Area", "ChokeType", "ViewType", "Date", "Hour")