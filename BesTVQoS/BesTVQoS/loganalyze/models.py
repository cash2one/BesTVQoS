from django.db import models

class ServerInfo(models.Model):
    ServerID = models.AutoField(primary_key=True)
    IP = models.CharField(max_length=15)
    ServiceType = models.CharField(max_length=8)
    ISP = models.CharField(max_length=32, null=True)
    Area = models.CharField(max_length=64, null=True)
    Type = models.CharField(max_length=64, null=True)

    class Meta:
        db_table = 'serverinfo'
        unique_together = ('IP', 'ServiceType', 'ISP', 'Area')

    def __unicode__(self):
        return u'ServiceInfo'

class CodeInfo(models.Model):
    CodeID = models.AutoField(primary_key=True)
    ServerID = models.ForeignKey(ServerInfo, db_column='ServerID')
    Date = models.DateField()
    Hour = models.SmallIntegerField()
    Code = models.SmallIntegerField()
    Records = models.IntegerField(default=0)
    Ratio = models.FloatField(null=True, default=0)

    class Meta:
        db_table = 'codeinfo'
        unique_together = ('ServerID', 'Date', 'Hour', 'Code')

    def __unicode__(self):
        return u'CodeInfo'

class UrlInfo(models.Model):
    URLID = models.AutoField(primary_key=True)
    CodeID = models.ForeignKey(CodeInfo, db_column='CodeID')
    URL = models.CharField(max_length=512)
    Records = models.IntegerField(default=0)
    Ratio = models.FloatField(null=True, default=0)

    class Meta:
        db_table = 'urlinfo'
        unique_together = ('CodeID', 'URL')

    def __unicode__(self):
        return u'UrlInfo'

class RespDelayInfo(models.Model):
    URLID = models.ForeignKey(UrlInfo, primary_key=True, db_column='URLID')
    P25 = models.IntegerField()
    P50 = models.IntegerField()
    P75 = models.IntegerField()
    P90 = models.IntegerField()
    P95 = models.IntegerField()
    AvgTime = models.IntegerField()

    class Meta:
        db_table = 'respdelayinfo'

    def __unicode__(self):
        return u'RespDelayInfo'

class ReqDelayInfo(models.Model):
    URLID = models.ForeignKey(UrlInfo, primary_key=True, db_column='URLID')
    P25 = models.IntegerField()
    P50 = models.IntegerField()
    P75 = models.IntegerField()
    P90 = models.IntegerField()
    P95 = models.IntegerField()
    AvgTime = models.IntegerField()

    class Meta:
        db_table = 'reqdelayinfo'

    def __unicode__(self):
        return u'ReqDelayInfo'
