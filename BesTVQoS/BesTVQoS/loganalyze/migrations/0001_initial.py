# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ServerInfo'
        db.create_table('serverinfo', (
            ('ServerID', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('IP', self.gf('django.db.models.fields.CharField')(max_length=15)),
            ('ServiceType', self.gf('django.db.models.fields.CharField')(max_length=8)),
            ('ISP', self.gf('django.db.models.fields.CharField')(max_length=32, null=True)),
            ('Area', self.gf('django.db.models.fields.CharField')(max_length=64, null=True)),
            ('Type', self.gf('django.db.models.fields.CharField')(max_length=64, null=True)),
        ))
        db.send_create_signal(u'loganalyze', ['ServerInfo'])

        # Adding unique constraint on 'ServerInfo', fields ['IP', 'ServiceType', 'ISP', 'Area']
        db.create_unique('serverinfo', ['IP', 'ServiceType', 'ISP', 'Area'])

        # Adding model 'CodeInfo'
        db.create_table('codeinfo', (
            ('CodeID', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ServerID', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['loganalyze.ServerInfo'], db_column='ServerID')),
            ('Date', self.gf('django.db.models.fields.DateField')()),
            ('Hour', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('Code', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('Records', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('Ratio', self.gf('django.db.models.fields.FloatField')(default=0, null=True)),
        ))
        db.send_create_signal(u'loganalyze', ['CodeInfo'])

        # Adding unique constraint on 'CodeInfo', fields ['ServerID', 'Date', 'Hour', 'Code']
        db.create_unique('codeinfo', ['ServerID', 'Date', 'Hour', 'Code'])

        # Adding model 'UrlInfo'
        db.create_table('urlinfo', (
            ('URLID', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('CodeID', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['loganalyze.CodeInfo'], db_column='CodeID')),
            ('URL', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('Records', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('Ratio', self.gf('django.db.models.fields.FloatField')(default=0, null=True)),
        ))
        db.send_create_signal(u'loganalyze', ['UrlInfo'])

        # Adding unique constraint on 'UrlInfo', fields ['CodeID', 'URL']
        db.create_unique('urlinfo', ['CodeID', 'URL'])

        # Adding model 'RespDelayInfo'
        db.create_table('respdelayinfo', (
            ('URLID', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['loganalyze.UrlInfo'], primary_key=True, db_column='URLID')),
            ('P25', self.gf('django.db.models.fields.IntegerField')()),
            ('P50', self.gf('django.db.models.fields.IntegerField')()),
            ('P75', self.gf('django.db.models.fields.IntegerField')()),
            ('P90', self.gf('django.db.models.fields.IntegerField')()),
            ('P95', self.gf('django.db.models.fields.IntegerField')()),
            ('AvgTime', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'loganalyze', ['RespDelayInfo'])

        # Adding model 'ReqDelayInfo'
        db.create_table('reqdelayinfo', (
            ('URLID', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['loganalyze.UrlInfo'], primary_key=True, db_column='URLID')),
            ('P25', self.gf('django.db.models.fields.IntegerField')()),
            ('P50', self.gf('django.db.models.fields.IntegerField')()),
            ('P75', self.gf('django.db.models.fields.IntegerField')()),
            ('P90', self.gf('django.db.models.fields.IntegerField')()),
            ('P95', self.gf('django.db.models.fields.IntegerField')()),
            ('AvgTime', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'loganalyze', ['ReqDelayInfo'])


    def backwards(self, orm):
        # Removing unique constraint on 'UrlInfo', fields ['CodeID', 'URL']
        db.delete_unique('urlinfo', ['CodeID', 'URL'])

        # Removing unique constraint on 'CodeInfo', fields ['ServerID', 'Date', 'Hour', 'Code']
        db.delete_unique('codeinfo', ['ServerID', 'Date', 'Hour', 'Code'])

        # Removing unique constraint on 'ServerInfo', fields ['IP', 'ServiceType', 'ISP', 'Area']
        db.delete_unique('serverinfo', ['IP', 'ServiceType', 'ISP', 'Area'])

        # Deleting model 'ServerInfo'
        db.delete_table('serverinfo')

        # Deleting model 'CodeInfo'
        db.delete_table('codeinfo')

        # Deleting model 'UrlInfo'
        db.delete_table('urlinfo')

        # Deleting model 'RespDelayInfo'
        db.delete_table('respdelayinfo')

        # Deleting model 'ReqDelayInfo'
        db.delete_table('reqdelayinfo')


    models = {
        u'loganalyze.codeinfo': {
            'Code': ('django.db.models.fields.SmallIntegerField', [], {}),
            'CodeID': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'Date': ('django.db.models.fields.DateField', [], {}),
            'Hour': ('django.db.models.fields.SmallIntegerField', [], {}),
            'Meta': {'unique_together': "(('ServerID', 'Date', 'Hour', 'Code'),)", 'object_name': 'CodeInfo', 'db_table': "'codeinfo'"},
            'Ratio': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True'}),
            'Records': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'ServerID': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['loganalyze.ServerInfo']", 'db_column': "'ServerID'"})
        },
        u'loganalyze.reqdelayinfo': {
            'AvgTime': ('django.db.models.fields.IntegerField', [], {}),
            'Meta': {'object_name': 'ReqDelayInfo', 'db_table': "'reqdelayinfo'"},
            'P25': ('django.db.models.fields.IntegerField', [], {}),
            'P50': ('django.db.models.fields.IntegerField', [], {}),
            'P75': ('django.db.models.fields.IntegerField', [], {}),
            'P90': ('django.db.models.fields.IntegerField', [], {}),
            'P95': ('django.db.models.fields.IntegerField', [], {}),
            'URLID': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['loganalyze.UrlInfo']", 'primary_key': 'True', 'db_column': "'URLID'"})
        },
        u'loganalyze.respdelayinfo': {
            'AvgTime': ('django.db.models.fields.IntegerField', [], {}),
            'Meta': {'object_name': 'RespDelayInfo', 'db_table': "'respdelayinfo'"},
            'P25': ('django.db.models.fields.IntegerField', [], {}),
            'P50': ('django.db.models.fields.IntegerField', [], {}),
            'P75': ('django.db.models.fields.IntegerField', [], {}),
            'P90': ('django.db.models.fields.IntegerField', [], {}),
            'P95': ('django.db.models.fields.IntegerField', [], {}),
            'URLID': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['loganalyze.UrlInfo']", 'primary_key': 'True', 'db_column': "'URLID'"})
        },
        u'loganalyze.serverinfo': {
            'Area': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True'}),
            'IP': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'ISP': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True'}),
            'Meta': {'unique_together': "(('IP', 'ServiceType', 'ISP', 'Area'),)", 'object_name': 'ServerInfo', 'db_table': "'serverinfo'"},
            'ServerID': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ServiceType': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'Type': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True'})
        },
        u'loganalyze.urlinfo': {
            'CodeID': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['loganalyze.CodeInfo']", 'db_column': "'CodeID'"}),
            'Meta': {'unique_together': "(('CodeID', 'URL'),)", 'object_name': 'UrlInfo', 'db_table': "'urlinfo'"},
            'Ratio': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True'}),
            'Records': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'URL': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'URLID': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['loganalyze']