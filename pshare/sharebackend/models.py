# std lib imports
import datetime
import md5

# django imports
from django.db import models
from django.utils.translation import ugettext_lazy as _

# third-party app imports
# app imports


def upload_file(instance, file_name):
    return 'uploads/{0}_{1}'.format(
        md5.new(str(datetime.datetime.now())).hexdigest(), file_name)


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
    text = models.CharField('tag', max_length=150, null=True)


class PatientTag(BaseModel):
    """
    Relating patients to certain tags

    """
    tag = models.ForeignKey('Tag')
    patient_id = models.CharField('tag', max_length=150, null=True)

    class Meta:
        verbose_name = _('Patient Tag')
        verbose_name_plural = _('Patient Tags')

    @classmethod
    def tag_patients(cls, tag_text, patient_ids):
        tag = Tag.objects.filter(text=tag_text)
        if tag.count() < 1:
            tag = Tag.objects.create(text=tag_text)
        else:
            tag = tag[0]
        cls.objects.bulk_create([cls(
            tag=tag, patient_id=patient_id) for patient_id in patient_ids])

    @classmethod
    def queryset_api_intersection(cls, queryset, api_patient_dict):
        patients = []
        if queryset.count() < 1:
            return patients
        patiend_id_set = set(queryset.values_list('patient_id', flat=True))
        for patient in api_patient_dict:
            if str(patient['id']) in patiend_id_set:
                patients.append(patient)
        return patients


class File(BaseModel):
    """
    Uploaded files to share with patient groups

    """
    file_name = models.CharField('file_name', max_length=150, null=True)
    shared_file = models.FileField(
        upload_to=upload_file, blank=False, null=False)

    @classmethod
    def add_file(cls, form_file, tag_id_list):
        new_file = cls.objects.create(
            file_name=str(form_file), shared_file=form_file)
        tags = Tag.objects.filter(id__in=tag_id_list)
        TagFileShare.objects.bulk_create([TagFileShare.objects.create(
            file_share=new_file, tag=tag) for tag in tags])


class TagFileShare(BaseModel):
    """
    Relating files to tags

    """
    file_share = models.ForeignKey('File')
    tag = models.CharField('tag', max_length=150, null=True)
