# std lib imports
import urllib
import json

# django imports
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.shortcuts import render_to_response
from django.core.context_processors import csrf

# third-party app imports
import requests

# app imports
from models import PatientTag, File, Tag


# API util
def refresh_tokens(refresh_token):
    url = '{0}?{1}'.format(
        settings.DRC_TOKEN_URL, urllib.urlencode({
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
            'client_id': settings.DRC_CLIENT_ID,
            'client_secret': settings.DRC_CLIENT_SECRET}))
    response = requests.post(url)
    tokens = response.json()
    if 'access_token' in tokens and 'refresh_token' in tokens \
            and 'expires_in' in tokens:
        return tokens
    else:
        return None


def request_access_token(code):
    url = '{0}?{1}'.format(
        settings.DRC_TOKEN_URL, urllib.urlencode({
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': settings.DRC_REDIRECT_URI,
            'client_id': settings.DRC_CLIENT_ID,
            'client_secret': settings.DRC_CLIENT_SECRET}))
    response = requests.post(url)
    tokens = response.json()
    if 'access_token' in tokens and 'refresh_token' in tokens \
            and 'expires_in' in tokens:
        return tokens
    else:
        return None


def store_tokens_in_session(request, tokens):
    request.session['access_token'] = tokens['access_token']
    request.session['refresh_token'] = tokens['refresh_token']
    request.session['expires_in'] = tokens['expires_in']


# Helper views
def get_all_patients(request):
    # In case of no access token stored in session
    if 'access_token' not in request.session:
        return False

    # Try to get list patients
    response = requests.get('{0}{1}'.format(
        settings.DRC_BASE_URL, 'patients'), headers={
            'Authorization': 'Bearer {0}'.format(
                request.session['access_token'])})

    # in case of un authorized, try to refresh token, and retrieve users again
    if response.status_code == 401:
        if 'refresh_token' in request.session:
            tokens = refresh_tokens(request.session['refresh_token'])
            if tokens is not None:
                store_tokens_in_session(request, tokens)
                response = requests.get('{0}{1}'.format(
                    settings.DRC_BASE_URL, 'patients'), headers={
                        'Authorization': 'Bearer {0}'.format(
                            request.session['access_token'])})
    if response.status_code == 200:
        return response.json()
    return False


# Those are the actual views
def home(request):
    if request.method == 'GET' and 'code' in request.GET and \
            'access_token' not in request.session:
        code = request.GET.get('code')
        tokens = request_access_token(code)
        if tokens is not None:
            store_tokens_in_session(request, tokens)
    elif 'access_token' not in request.session:
        return HttpResponseRedirect(settings.DRC_REQUEST_AUTH_CODE_URL)
    return HttpResponse('Hello World')


def list_patients(request):
    patients = get_all_patients(request)
    if patients is not False:
        return HttpResponse(
            json.dumps(patients), content_type='application/json')
    else:
        return HttpResponseRedirect('sharebackend/')


def new_group(request):
    patients = get_all_patients(request)
    if patients is False:
        return HttpResponseRedirect('sharebackend/')

    if request.method == 'POST':
        group_name = request.POST.get('group_name')
        patient_ids = request.POST.getlist('patients')
        PatientTag.tag_patients(group_name.lower(), patient_ids)
    context = {'patients': patients['results']}
    context.update(csrf(request))
    return render_to_response('new_group.html', context)


def get_group(request, tag_text):
    tag_text = tag_text.lower()
    patients = get_all_patients(request)
    if patients is False:
        return HttpResponseRedirect('sharebackend/')
    patients_by_group = PatientTag.queryset_api_intersection(
        PatientTag.objects.filter(
            tag__text=tag_text), patients['results'])
    context = {'patients': patients_by_group, 'group_name': tag_text}
    return render_to_response('group.html', context)


def file_share(request):
    tag_set = Tag.objects.all()
    if request.method == 'POST':
        tag_id_list = request.POST.getlist('tag')
        for form_file in request.FILES.getlist('share_files'):
            File.add_file(form_file, tag_id_list)
    context = {'tag_set': tag_set}
    context.update(csrf(request))
    return render_to_response('file_share.html', context)
