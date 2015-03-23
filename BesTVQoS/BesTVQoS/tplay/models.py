from django.db import models

# Create your models here.

class playinfo(models.Model):
    ServiceType=models.CharField(max_length=30)
    DeviceType=models.CharField(max_length=255)
    ISP=models.CharField(max_length=255)
    Area=models.CharField(max_length=255)
    ViewType=models.IntegerField()
    Date=models.DateField()
    Hour=models.IntegerField()    
    Records=models.IntegerField()
    Users=models.IntegerField()
    AverageTime=models.IntegerField()

    class Meta:
        db_table="playinfo"
        unique_together=('ServiceType', 'DeviceType', 'ISP', 'Area', 'ViewType', 'Date', 'Hour')