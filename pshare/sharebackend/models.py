# std lib imports
import datetime
import md5

# django imports
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.conf import settings

# third-party app imports
# app imports
from .tasks import email_group, update_patients


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)


def upload_file(instance, file_name):
    return '{0}{1}_{2}'.format(
        settings.UPLOAD_DIR,
        md5.new(str(datetime.datetime.now())).hexdigest(), file_name)


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    access_token = models.CharField('access_token', max_length=200, null=True)
    refresh_token = models.CharField('refresh_token', max_length=200, null=True)


class BaseModel(models.Model):
    """
    Base model for the created and modified date time

    """
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Tag(BaseModel):
    """
    Tags to group patients

    """
    user = models.ForeignKey(User)
    text = models.CharField('tag', max_length=150, null=True)

    def tag_patients(self, patient_ids, callback=None, args=None):
        PatientTag.objects.bulk_create([PatientTag(
            tag=self, patient_id=patient_id) for patient_id in patient_ids])
        if callback is not None and args is not None:
            callback(*args)

    def update_patients(self, user_id, patient_ids):
        if len(patient_ids) > 0:
            update_patients.apply_async(args=[self.id, user_id, patient_ids])


class PatientTag(BaseModel):
    """
    Relating patients to certain tags

    """
    tag = models.ForeignKey('Tag')
    patient_id = models.IntegerField(null=True)

    class Meta:
        verbose_name = _('Patient Tag')
        verbose_name_plural = _('Patient Tags')

    @classmethod
    def queryset_api_intersection(cls, queryset, api_patient_dict):
        patients = []
        if queryset.count() < 1:
            return patients
        patiend_id_set = set(queryset.values_list('patient_id', flat=True))
        for patient in api_patient_dict:
            if patient['id'] in patiend_id_set:
                patients.append(patient)
        return patients

    @classmethod
    def queryset_api_exclude(cls, queryset, api_patient_dict):
        patients = []
        if queryset.count() < 1:
            return api_patient_dict
        patiend_id_set = set(queryset.values_list('patient_id', flat=True))
        for patient in api_patient_dict:
            if patient['id'] not in patiend_id_set:
                patients.append(patient)
        return patients


class File(BaseModel):
    """
    Uploaded files to share with patient groups

    """
    user = models.ForeignKey(User)
    file_name = models.CharField('file_name', max_length=150, null=True)
    shared_file = models.FileField(
        upload_to=upload_file, blank=False, null=False)

    def tag_file(self, tag_id_list, user):
        tags = Tag.objects.filter(id__in=tag_id_list, user=user)
        TagFileShare.objects.bulk_create([TagFileShare(
            file_share=self, tag=tag) for tag in tags])
        for tag_id in tag_id_list:
            email_group.apply_async(args=[self.id, tag_id, user.username])


class TagFileShare(BaseModel):
    """
    Relating files to tags

    """
    file_share = models.ForeignKey('File')
    tag = models.ForeignKey('Tag')


class PatientFileShare(BaseModel):
    """
    Relating files to patients

    """
    file_share = models.ForeignKey('File')
    patient_id = models.IntegerField(null=True)
