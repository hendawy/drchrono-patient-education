# std lib imports
import json

# django imports
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.shortcuts import render_to_response
from django.core.context_processors import csrf
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

# third-party app imports
import requests

# app imports
from .models import PatientTag, File, Tag, TagFileShare
from .util.drchrono import request_access_token, store_tokens, \
    get_user_info, get_all_patients


# For testing purposes
def list_patients(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/sharebackend/')
    user_profile = request.user.get_profile()
    patients = get_all_patients(
        request.user, user_profile.access_token, user_profile.refresh_token)
    if patients is not False:
        return HttpResponse(
            json.dumps(patients), content_type='application/json')
    else:
        return HttpResponseRedirect('/sharebackend/')


def test_resources(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/sharebackend/')
    user_profile = request.user.get_profile()
    url = '{0}{1}'.format(settings.DRC_BASE_URL, 'patients')
    response = requests.get(url, headers={
        'Authorization': 'Bearer {0}'.format(user_profile.access_token)})
    return HttpResponse(response.text, content_type='application/json')


# Those are the actual views
def home(request):
    if request.method == 'GET' and 'code' in request.GET:
        code = request.GET.get('code')
        tokens = request_access_token(code)
        if tokens is not None:
            drc_user = get_user_info(tokens['access_token'])
            print drc_user
            if 'error' not in drc_user:
                user = authenticate(
                    username=int(drc_user['id']), password='secret')
                if user is None:
                    user = User.objects.create_user(
                        drc_user['id'], drc_user['email'], 'secret')
                    user.save()
                    user = authenticate(
                        username=drc_user['id'], password='secret')
                    store_tokens(user, tokens)
                login(request, user)
    elif not request.user.is_authenticated():
        return HttpResponseRedirect(settings.DRC_REQUEST_AUTH_CODE_URL)
    return HttpResponseRedirect('/sharebackend/group/')


def landing(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/sharebackend/group/')
    return render_to_response('landing.html', {})


def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/sharebackend/landing/')


def new_group(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/sharebackend/')
    user_profile = request.user.get_profile()
    patients = get_all_patients(
        request.user, user_profile.access_token, user_profile.refresh_token)
    if patients is False:
        return HttpResponseRedirect('/sharebackend/')

    if request.method == 'POST' and len(request.POST.get('group_name')) > 0:
        group_name = request.POST.get('group_name')
        patient_ids = request.POST.getlist('patients')
        tag = Tag.objects.create(text=group_name.lower(), user=request.user)
        tag.tag_patients(patient_ids)
    context = {'patients': patients, 'section': 'new_group'}
    context.update(csrf(request))
    return render_to_response('new_group.html', context)


def remove_group(request, tag_text):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/sharebackend/')
    Tag.objects.filter(text=tag_text, user=request.user).delete()
    return HttpResponseRedirect('/sharebackend/group/')


def get_group(request, tag_text):
    tag_text = tag_text.lower()
    tag = Tag.objects.get(text=tag_text)
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/sharebackend/')
    user_profile = request.user.get_profile()
    patients = get_all_patients(
        request.user, user_profile.access_token, user_profile.refresh_token)
    if patients is False:
        return HttpResponseRedirect('/sharebackend/')

    if request.method == 'POST':
        patient_ids = request.POST.getlist('patients')
        tag.tag_patients(
            patient_ids, callback=tag.update_patients,
            args=[request.user.username, patient_ids])

    files_shared = TagFileShare.objects.filter(
        tag=tag, tag__user=request.user)
    patients_by_group = PatientTag.queryset_api_intersection(
        PatientTag.objects.filter(
            tag=tag, tag__user=request.user), patients)
    untagged_patients = PatientTag.queryset_api_exclude(
        PatientTag.objects.filter(
            tag=tag, tag__user=request.user), patients)
    context = {
        'patients': patients_by_group, 'group_name': tag_text,
        'files_shared': files_shared, 'section': 'get_group',
        'untagged_patients': untagged_patients}
    context.update(csrf(request))
    return render_to_response('group.html', context)


def file_share(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/sharebackend/')
    tag_set = Tag.objects.all()
    if request.method == 'POST':
        tag_id_list = request.POST.getlist('tags')
        for form_file in request.FILES.getlist('share_files'):
            new_file = File.objects.create(
                user=request.user, file_name=str(form_file),
                shared_file=form_file)
            new_file.tag_file(tag_id_list, request.user)
    context = {'tag_set': tag_set, 'section': 'file_share'}
    context.update(csrf(request))
    return render_to_response('file_share.html', context)


def list_groups(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/sharebackend/')
    tags = Tag.objects.filter(user=request.user)
    context = {'tags': tags, 'section': 'list_groups'}
    return render_to_response('group_list.html', context)


def list_files(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/sharebackend/')
    files = File.objects.filter(user=request.user)
    context = {'files': files, 'section': 'list_files'}
    return render_to_response('file_list.html', context)


def get_file(request, file_id):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/sharebackend/')

    shared_file = File.objects.get(id=file_id)

    if request.method == 'POST':
        tag_id_list = request.POST.getlist('tags')
        shared_file.tag_file(tag_id_list, request.user)

    shared_tags = TagFileShare.objects.filter(file_share=shared_file)
    tags = Tag.objects.filter(user=request.user).exclude(
        id__in=shared_tags.values_list('tag', flat=True))
    context = {
        'shared_tags': shared_tags, 'file_name': shared_file.file_name,
        'section': 'get_file', 'tags': tags}
    context.update(csrf(request))
    return render_to_response('file.html', context)
