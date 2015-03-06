# std lib imports
# django imports
from django.contrib.auth.models import User
from django.core import mail

# third-party app imports
from celery.task import task

# local imports
from .util.drchrono import get_all_patients, get_user_info

# TODO: Move email logic to its own util module
# TODO: This will create a symaphore problem, when this task is carried
# on in parallel,the patient might get a file twice if it was shared with
# 2 groups at the same time that he is member of.


@task()
def email_group(file_id, tag_id, user_id):
    # importing models here to avoid cyclic imports
    from .models import File, PatientTag, PatientFileShare

    share_file = File.objects.get(id=file_id)
    user = User.objects.get(username=user_id)
    user_profile = user.get_profile()
    user_info = get_user_info(user_profile.access_token)

    old_file_patient = PatientFileShare.objects.filter(
        file_share=share_file).values_list('patient_id', flat=True)
    patients = PatientTag.objects.filter(tag__id=tag_id).exclude(
        patient_id__in=old_file_patient)
    api_patients = get_all_patients(
        user, user_profile.access_token, user_profile.refresh_token)
    patients_to_send = PatientTag.queryset_api_intersection(
        patients, api_patients)

    connection = mail.get_connection()
    connection.open()
    email_messages = []

    file_patient = []

    for patient in patients_to_send:
        subject = 'New File from Dr {0} {1}'.format(
            user_info['first_name'], user_info['last_name'])
        body = ('Hi {0},\n\nDoctor {1} {2} has shared a new ' +
                'file with you.').format(
                    patient['first_name'], user_info['first_name'],
                    user_info['last_name'])
        message = mail.EmailMessage(
            subject, body, user.email, [patient['email']])
        message.attach_file(str(share_file.shared_file))
        email_messages.append(message)
        file_patient.append(PatientFileShare(
            file_share=share_file, patient_id=patient['id']))
    PatientFileShare.objects.bulk_create(file_patient)

    connection.send_messages(email_messages)
    connection.close()


@task()
def update_patients(tag_id, user_id, patient_id_list):
    from .models import File, PatientTag, PatientFileShare, Tag
    user = User.objects.get(username=user_id)
    user_profile = user.get_profile()
    user_info = get_user_info(user_profile.access_token)
    tag = Tag.objects.get(id=tag_id)
    files = File.objects.filter(tagfileshare__tag=tag, user=user)

    old_file_patient = PatientFileShare.objects.filter(
        patient_id__in=patient_id_list).values_list('patient_id', 'file_share')
    patients = PatientTag.objects.filter(patient_id__in=patient_id_list)
    api_patients = get_all_patients(
        user, user_profile.access_token, user_profile.refresh_token)
    patients_to_send = PatientTag.queryset_api_intersection(
        patients, api_patients)

    connection = mail.get_connection()
    connection.open()
    email_messages = []

    file_patient = []

    for patient in patients_to_send:
        subject = 'New File from Dr {0} {1}'.format(
            user_info['first_name'], user_info['last_name'])
        body = ('Hi {0},\n\nDoctor {1} {2} has shared a new ' +
                'file with you.').format(
                    patient['first_name'], user_info['first_name'],
                    user_info['last_name'])
        message = mail.EmailMessage(
            subject, body, user.email, [patient['email']])
        for share_file in files:
            if (patient['id'], share_file.id) not in old_file_patient:
                message.attach_file(str(share_file.shared_file))
                email_messages.append(message)
                file_patient.append(PatientFileShare(
                    file_share=share_file, patient_id=patient['id']))

    PatientFileShare.objects.bulk_create(file_patient)

    connection.send_messages(email_messages)
    connection.close()
