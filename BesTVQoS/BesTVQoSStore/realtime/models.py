from django.db import models


class RealtimeBaseInfo(models.Model):
    Time = models.CharField(max_length=15)
    ServiceType = models.CharField(max_length=30)
    DeviceType = models.CharField(max_length=255)
    ViewType = models.IntegerField()
    SucRate = models.FloatField()
    Fluency = models.FloatField()
    Records = models.IntegerField()

    class Meta:
        db_table = "realtimebase"
        unique_together = ('Time', 'ServiceType', 'DeviceType', 'ViewType')

    def __str__(self):
        return "RealtimeBaseInfo"
