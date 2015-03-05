# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Tag'
        db.create_table('sharebackend_tag', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('text', self.gf('django.db.models.fields.CharField')(max_length=150, null=True)),
        ))
        db.send_create_signal('sharebackend', ['Tag'])

        # Adding model 'PatientTag'
        db.create_table('sharebackend_patienttag', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('tag', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sharebackend.Tag'])),
            ('patient_id', self.gf('django.db.models.fields.CharField')(max_length=150, null=True)),
        ))
        db.send_create_signal('sharebackend', ['PatientTag'])

        # Adding model 'File'
        db.create_table('sharebackend_file', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('file_name', self.gf('django.db.models.fields.CharField')(max_length=150, null=True)),
            ('shared_file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
        ))
        db.send_create_signal('sharebackend', ['File'])

        # Adding model 'TagFileShare'
        db.create_table('sharebackend_tagfileshare', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('file_share', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sharebackend.File'])),
            ('tag', self.gf('django.db.models.fields.CharField')(max_length=150, null=True)),
        ))
        db.send_create_signal('sharebackend', ['TagFileShare'])


    def backwards(self, orm):
        # Deleting model 'Tag'
        db.delete_table('sharebackend_tag')

        # Deleting model 'PatientTag'
        db.delete_table('sharebackend_patienttag')

        # Deleting model 'File'
        db.delete_table('sharebackend_file')

        # Deleting model 'TagFileShare'
        db.delete_table('sharebackend_tagfileshare')


    models = {
        'sharebackend.file': {
            'Meta': {'object_name': 'File'},
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'file_name': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'shared_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'})
        },
        'sharebackend.patienttag': {
            'Meta': {'object_name': 'PatientTag'},
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'patient_id': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sharebackend.Tag']"})
        },
        'sharebackend.tag': {
            'Meta': {'object_name': 'Tag'},
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True'})
        },
        'sharebackend.tagfileshare': {
            'Meta': {'object_name': 'TagFileShare'},
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'file_share': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sharebackend.File']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'tag': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True'})
        }
    }

    complete_apps = ['sharebackend']