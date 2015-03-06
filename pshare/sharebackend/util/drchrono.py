# std lib imports
import urllib

# django imports
from django.conf import settings

# third-party app imports
import requests

# app imports


"""
This Module could be structured more into a proper api wrapper
"""


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


# is this the right place?
def store_tokens(user, tokens):
    user_profile = user.get_profile()
    user_profile.access_token = tokens['access_token']
    user_profile.refresh_token = tokens['refresh_token']
    user_profile.save()


def get_user_info(access_token):
    """
    This function only works if token is valid

    """
    url = '{0}{1}'.format(settings.DRC_BASE_URL, 'users/current')
    response = requests.get(url, headers={
        'Authorization': 'Bearer {0}'.format(access_token)})
    user_dict = response.json()
    response = requests.get(user_dict['doctor'], headers={
        'Authorization': 'Bearer {0}'.format(access_token)})
    user_dict = response.json()
    if 'email' in user_dict:
        return user_dict
    return False


# Should object "User" be passed here?
# Are access tokens unique per user?
# What if I pass the user id and then add a method to the
# UserProfile model to store the tonkens?
def get_all_patients(user, access_token, refresh_token):
    url = '{0}{1}'.format(settings.DRC_BASE_URL, 'patients')
    response = requests.get(url, headers={
        'Authorization': 'Bearer {0}'.format(access_token)})
    # in case of un authorized, try to refresh token, and retrieve users again
    if response.status_code == 401:
        tokens = refresh_tokens(refresh_token)
        if tokens is not None:
            store_tokens(user, tokens)
            response = requests.get(url, headers={
                'Authorization': 'Bearer {0}'.format(access_token)})
    if response.status_code == 200:
        response_dict = response.json()
        results = response_dict['results']
        while response_dict['next'] is not None:
            url = response_dict['next']
            response = requests.get(url, headers={
                'Authorization': 'Bearer {0}'.format(access_token)})
            response_dict = response.json()
            results += response_dict['results']
        return results
    return False
