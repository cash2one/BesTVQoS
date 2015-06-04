# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'BestvPlayprofile'
        db.create_table('playprofile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ServiceType', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('DeviceType', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('ISP', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('Area', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('Date', self.gf('django.db.models.fields.DateField')()),
            ('Records', self.gf('django.db.models.fields.IntegerField')()),
            ('Users', self.gf('django.db.models.fields.IntegerField')()),
            ('AverageTime', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'tplay', ['BestvPlayprofile'])

        # Adding unique constraint on 'BestvPlayprofile', fields ['ServiceType', 'DeviceType', 'ISP', 'Area', 'Date']
        db.create_unique('playprofile', ['ServiceType', 'DeviceType', 'ISP', 'Area', 'Date'])

        # Adding model 'BestvPlayinfo'
        db.create_table('playinfo', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ServiceType', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('DeviceType', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('ISP', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('Area', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('ViewType', self.gf('django.db.models.fields.IntegerField')()),
            ('Date', self.gf('django.db.models.fields.DateField')()),
            ('Hour', self.gf('django.db.models.fields.IntegerField')()),
            ('Records', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'tplay', ['BestvPlayinfo'])

        # Adding unique constraint on 'BestvPlayinfo', fields ['ServiceType', 'DeviceType', 'ISP', 'Area', 'ViewType', 'Date', 'Hour']
        db.create_unique('playinfo', ['ServiceType', 'DeviceType', 'ISP', 'Area', 'ViewType', 'Date', 'Hour'])

        # Adding model 'BestvPlaytime'
        db.create_table('playtime', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ServiceType', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('DeviceType', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('ISP', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('Area', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('ViewType', self.gf('django.db.models.fields.IntegerField')()),
            ('Date', self.gf('django.db.models.fields.DateField')()),
            ('Hour', self.gf('django.db.models.fields.IntegerField')()),
            ('P25', self.gf('django.db.models.fields.IntegerField')()),
            ('P50', self.gf('django.db.models.fields.IntegerField')()),
            ('P75', self.gf('django.db.models.fields.IntegerField')()),
            ('P90', self.gf('django.db.models.fields.IntegerField')()),
            ('P95', self.gf('django.db.models.fields.IntegerField')()),
            ('AverageTime', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'tplay', ['BestvPlaytime'])

        # Adding unique constraint on 'BestvPlaytime', fields ['ServiceType', 'DeviceType', 'ISP', 'Area', 'ViewType', 'Date', 'Hour']
        db.create_unique('playtime', ['ServiceType', 'DeviceType', 'ISP', 'Area', 'ViewType', 'Date', 'Hour'])

        # Adding model 'Title'
        db.create_table(u'tplay_title', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ServiceType', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('DeviceType', self.gf('django.db.models.fields.CharField')(max_length=60)),
            ('Version', self.gf('django.db.models.fields.CharField')(max_length=40)),
        ))
        db.send_create_signal(u'tplay', ['Title'])

        # Adding unique constraint on 'Title', fields ['ServiceType', 'DeviceType', 'Version']
        db.create_unique(u'tplay_title', ['ServiceType', 'DeviceType', 'Version'])

        # Adding model 'BestvFbuffer'
        db.create_table('fbuffer', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ServiceType', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('DeviceType', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('ISP', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('Area', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('ViewType', self.gf('django.db.models.fields.IntegerField')()),
            ('Date', self.gf('django.db.models.fields.DateField')()),
            ('Hour', self.gf('django.db.models.fields.IntegerField')()),
            ('SucRatio', self.gf('django.db.models.fields.FloatField')()),
            ('P25', self.gf('django.db.models.fields.IntegerField')()),
            ('P50', self.gf('django.db.models.fields.IntegerField')()),
            ('P75', self.gf('django.db.models.fields.IntegerField')()),
            ('P90', self.gf('django.db.models.fields.IntegerField')()),
            ('P95', self.gf('django.db.models.fields.IntegerField')()),
            ('AverageTime', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'tplay', ['BestvFbuffer'])

        # Adding unique constraint on 'BestvFbuffer', fields ['ServiceType', 'DeviceType', 'ISP', 'Area', 'ViewType', 'Date', 'Hour']
        db.create_unique('fbuffer', ['ServiceType', 'DeviceType', 'ISP', 'Area', 'ViewType', 'Date', 'Hour'])

        # Adding model 'BestvFluency'
        db.create_table('fluency', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ServiceType', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('DeviceType', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('ISP', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('Area', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('ViewType', self.gf('django.db.models.fields.IntegerField')()),
            ('Date', self.gf('django.db.models.fields.DateField')()),
            ('Hour', self.gf('django.db.models.fields.IntegerField')()),
            ('Fluency', self.gf('django.db.models.fields.FloatField')()),
            ('PRatio', self.gf('django.db.models.fields.FloatField')()),
            ('AllPRatio', self.gf('django.db.models.fields.FloatField')()),
            ('AvgCount', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal(u'tplay', ['BestvFluency'])

        # Adding unique constraint on 'BestvFluency', fields ['ServiceType', 'DeviceType', 'ISP', 'Area', 'ViewType', 'Date', 'Hour']
        db.create_unique('fluency', ['ServiceType', 'DeviceType', 'ISP', 'Area', 'ViewType', 'Date', 'Hour'])

        # Adding model 'Bestv3SRatio'
        db.create_table('bestv3sratio', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ServiceType', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('DeviceType', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('ISP', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('Area', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('Date', self.gf('django.db.models.fields.DateField')()),
            ('Ratio', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal(u'tplay', ['Bestv3SRatio'])

        # Adding unique constraint on 'Bestv3SRatio', fields ['ServiceType', 'DeviceType', 'ISP', 'Area', 'Date']
        db.create_unique('bestv3sratio', ['ServiceType', 'DeviceType', 'ISP', 'Area', 'Date'])

        # Adding model 'BestvAvgPchoke'
        db.create_table('bestvavgpchoke', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ServiceType', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('DeviceType', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('ISP', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('Area', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('Date', self.gf('django.db.models.fields.DateField')()),
            ('AvgCount', self.gf('django.db.models.fields.IntegerField')()),
            ('AvgTime', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'tplay', ['BestvAvgPchoke'])

        # Adding unique constraint on 'BestvAvgPchoke', fields ['ServiceType', 'DeviceType', 'ISP', 'Area', 'Date']
        db.create_unique('bestvavgpchoke', ['ServiceType', 'DeviceType', 'ISP', 'Area', 'Date'])


    def backwards(self, orm):
        # Removing unique constraint on 'BestvAvgPchoke', fields ['ServiceType', 'DeviceType', 'ISP', 'Area', 'Date']
        db.delete_unique('bestvavgpchoke', ['ServiceType', 'DeviceType', 'ISP', 'Area', 'Date'])

        # Removing unique constraint on 'Bestv3SRatio', fields ['ServiceType', 'DeviceType', 'ISP', 'Area', 'Date']
        db.delete_unique('bestv3sratio', ['ServiceType', 'DeviceType', 'ISP', 'Area', 'Date'])

        # Removing unique constraint on 'BestvFluency', fields ['ServiceType', 'DeviceType', 'ISP', 'Area', 'ViewType', 'Date', 'Hour']
        db.delete_unique('fluency', ['ServiceType', 'DeviceType', 'ISP', 'Area', 'ViewType', 'Date', 'Hour'])

        # Removing unique constraint on 'BestvFbuffer', fields ['ServiceType', 'DeviceType', 'ISP', 'Area', 'ViewType', 'Date', 'Hour']
        db.delete_unique('fbuffer', ['ServiceType', 'DeviceType', 'ISP', 'Area', 'ViewType', 'Date', 'Hour'])

        # Removing unique constraint on 'Title', fields ['ServiceType', 'DeviceType', 'Version']
        db.delete_unique(u'tplay_title', ['ServiceType', 'DeviceType', 'Version'])

        # Removing unique constraint on 'BestvPlaytime', fields ['ServiceType', 'DeviceType', 'ISP', 'Area', 'ViewType', 'Date', 'Hour']
        db.delete_unique('playtime', ['ServiceType', 'DeviceType', 'ISP', 'Area', 'ViewType', 'Date', 'Hour'])

        # Removing unique constraint on 'BestvPlayinfo', fields ['ServiceType', 'DeviceType', 'ISP', 'Area', 'ViewType', 'Date', 'Hour']
        db.delete_unique('playinfo', ['ServiceType', 'DeviceType', 'ISP', 'Area', 'ViewType', 'Date', 'Hour'])

        # Removing unique constraint on 'BestvPlayprofile', fields ['ServiceType', 'DeviceType', 'ISP', 'Area', 'Date']
        db.delete_unique('playprofile', ['ServiceType', 'DeviceType', 'ISP', 'Area', 'Date'])

        # Deleting model 'BestvPlayprofile'
        db.delete_table('playprofile')

        # Deleting model 'BestvPlayinfo'
        db.delete_table('playinfo')

        # Deleting model 'BestvPlaytime'
        db.delete_table('playtime')

        # Deleting model 'Title'
        db.delete_table(u'tplay_title')

        # Deleting model 'BestvFbuffer'
        db.delete_table('fbuffer')

        # Deleting model 'BestvFluency'
        db.delete_table('fluency')

        # Deleting model 'Bestv3SRatio'
        db.delete_table('bestv3sratio')

        # Deleting model 'BestvAvgPchoke'
        db.delete_table('bestvavgpchoke')


    models = {
        u'tplay.bestv3sratio': {
            'Area': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'Date': ('django.db.models.fields.DateField', [], {}),
            'DeviceType': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'ISP': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'Meta': {'unique_together': "(('ServiceType', 'DeviceType', 'ISP', 'Area', 'Date'),)", 'object_name': 'Bestv3SRatio', 'db_table': "'bestv3sratio'"},
            'Ratio': ('django.db.models.fields.FloatField', [], {}),
            'ServiceType': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'tplay.bestvavgpchoke': {
            'Area': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'AvgCount': ('django.db.models.fields.IntegerField', [], {}),
            'AvgTime': ('django.db.models.fields.IntegerField', [], {}),
            'Date': ('django.db.models.fields.DateField', [], {}),
            'DeviceType': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'ISP': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'Meta': {'unique_together': "(('ServiceType', 'DeviceType', 'ISP', 'Area', 'Date'),)", 'object_name': 'BestvAvgPchoke', 'db_table': "'bestvavgpchoke'"},
            'ServiceType': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'tplay.bestvfbuffer': {
            'Area': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'AverageTime': ('django.db.models.fields.IntegerField', [], {}),
            'Date': ('django.db.models.fields.DateField', [], {}),
            'DeviceType': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'Hour': ('django.db.models.fields.IntegerField', [], {}),
            'ISP': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'Meta': {'unique_together': "(('ServiceType', 'DeviceType', 'ISP', 'Area', 'ViewType', 'Date', 'Hour'),)", 'object_name': 'BestvFbuffer', 'db_table': "'fbuffer'"},
            'P25': ('django.db.models.fields.IntegerField', [], {}),
            'P50': ('django.db.models.fields.IntegerField', [], {}),
            'P75': ('django.db.models.fields.IntegerField', [], {}),
            'P90': ('django.db.models.fields.IntegerField', [], {}),
            'P95': ('django.db.models.fields.IntegerField', [], {}),
            'ServiceType': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'SucRatio': ('django.db.models.fields.FloatField', [], {}),
            'ViewType': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'tplay.bestvfluency': {
            'AllPRatio': ('django.db.models.fields.FloatField', [], {}),
            'Area': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'AvgCount': ('django.db.models.fields.FloatField', [], {}),
            'Date': ('django.db.models.fields.DateField', [], {}),
            'DeviceType': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'Fluency': ('django.db.models.fields.FloatField', [], {}),
            'Hour': ('django.db.models.fields.IntegerField', [], {}),
            'ISP': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'Meta': {'unique_together': "(('ServiceType', 'DeviceType', 'ISP', 'Area', 'ViewType', 'Date', 'Hour'),)", 'object_name': 'BestvFluency', 'db_table': "'fluency'"},
            'PRatio': ('django.db.models.fields.FloatField', [], {}),
            'ServiceType': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'ViewType': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'tplay.bestvplayinfo': {
            'Area': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'Date': ('django.db.models.fields.DateField', [], {}),
            'DeviceType': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'Hour': ('django.db.models.fields.IntegerField', [], {}),
            'ISP': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'Meta': {'unique_together': "(('ServiceType', 'DeviceType', 'ISP', 'Area', 'ViewType', 'Date', 'Hour'),)", 'object_name': 'BestvPlayinfo', 'db_table': "'playinfo'"},
            'Records': ('django.db.models.fields.IntegerField', [], {}),
            'ServiceType': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'ViewType': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'tplay.bestvplayprofile': {
            'Area': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'AverageTime': ('django.db.models.fields.IntegerField', [], {}),
            'Date': ('django.db.models.fields.DateField', [], {}),
            'DeviceType': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'ISP': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'Meta': {'unique_together': "(('ServiceType', 'DeviceType', 'ISP', 'Area', 'Date'),)", 'object_name': 'BestvPlayprofile', 'db_table': "'playprofile'"},
            'Records': ('django.db.models.fields.IntegerField', [], {}),
            'ServiceType': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'Users': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'tplay.bestvplaytime': {
            'Area': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'AverageTime': ('django.db.models.fields.IntegerField', [], {}),
            'Date': ('django.db.models.fields.DateField', [], {}),
            'DeviceType': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'Hour': ('django.db.models.fields.IntegerField', [], {}),
            'ISP': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'Meta': {'unique_together': "(('ServiceType', 'DeviceType', 'ISP', 'Area', 'ViewType', 'Date', 'Hour'),)", 'object_name': 'BestvPlaytime', 'db_table': "'playtime'"},
            'P25': ('django.db.models.fields.IntegerField', [], {}),
            'P50': ('django.db.models.fields.IntegerField', [], {}),
            'P75': ('django.db.models.fields.IntegerField', [], {}),
            'P90': ('django.db.models.fields.IntegerField', [], {}),
            'P95': ('django.db.models.fields.IntegerField', [], {}),
            'ServiceType': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'ViewType': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'tplay.title': {
            'DeviceType': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'Meta': {'unique_together': "(('ServiceType', 'DeviceType', 'Version'),)", 'object_name': 'Title'},
            'ServiceType': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'Version': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['tplay']