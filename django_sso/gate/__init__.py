import requests
from django.conf import settings

from django_sso.exceptions import SSOException


def set_sso_authorization_request_used(sso_token):
    """
    For service side. Makes SSO request as used for authentication procedure (not available for next authentications)
    """
    try:
        result = requests.post(settings.SSO_ROOT.rstrip('/') + '/sso/make_used/', {
            'token': settings.SSO_TOKEN,
            'authentication_token': sso_token
        })

        if result.status_code != 200:
            raise Exception(f'Некорректный ответ сервера авторизации: STATUS={result.status_code}; TEXT={result.text}')
    except Exception as e:
        raise SSOException(e)