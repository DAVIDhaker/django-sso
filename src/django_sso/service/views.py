import urllib.parse

from django.conf import settings
from django.contrib.auth import login, get_user_model
from django.contrib.auth.decorators import login_required
from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
import django.contrib.auth

from django_sso import deauthenticate_user
from django_sso.exceptions import SSOException
from django_sso.gate import set_sso_authorization_request_used
from django_sso.service import get_sso_authorization_request, request_sso_authorization_request, \
    request_deauthentication


def login_view(request):
    """
    The view to redirect to SSO for authentication
    """
    try:
        sso_token = request_sso_authorization_request(request)
        request.session['token'] = sso_token
    except SSOException as e:
        return render(
            request,
            template_name='django_sso/token_validation_error.html',
            context={
                'error': str(e),
                'debug': settings.DEBUG
            }
        )

    params = urllib.parse.urlencode({'sso': sso_token})

    return render(
        request,
        context={
            'redirect_url': f"{settings.SSO_ROOT}/login/?{params}"
        },
        template_name='django_sso/redirect_to_sso.html'
    )


@login_required
def for_logged_only(request):
    """
    The view for testing mechanism
    """
    user_model = get_user_model()
    return HttpResponse(f'{_("You authorized as")} <b>{getattr(request.user, user_model.USERNAME_FIELD)}</b>.')


@csrf_exempt
def accept_user_information(request):
    """
    Создаёт пользователя по команде SSO-сервера. Удостоверение производится при
    помощи токена, который указан в настройках текщего проекта для удостоверения
    на SSO-сервере.
    """
    if (
            request.method != 'POST'
            or 'token' not in request.POST
            or 'username' not in request.POST
            or 'password' not in request.POST
            or request.POST['token'] != settings.SSO_TOKEN
    ):
        return JsonResponse({'error': _('Incorrect request')}, status=400)

    user_model = get_user_model()

    user, created = user_model.objects.get_or_create(
        **{f'{user_model.USERNAME_FIELD}': request.POST['username']}
    )

    if user.password != request.POST['password']:
        user.password = request.POST['password']
        user.save()

    return JsonResponse({'ok': True})


def authorize_from_sso(request: WSGIRequest):
    """
    Авторизует пользователя, который вернулся от SSO-сервера
    """
    if not request.session.session_key or not request.session.get('token', ''):
        return redirect('/')

    try:
        authorization_request = get_sso_authorization_request(request.session.get('token'))

        user_model = get_user_model()

        user = user_model.objects.filter(
            **{f'{user_model.USERNAME_FIELD}': authorization_request['user_identy']}
        ).first()

        if not user:
            raise SSOException(_('Local user for SSO does not exist'))

        set_sso_authorization_request_used(request.session.get('token'))

        login(request, user)

        if authorization_request['next_url']:
            return redirect(authorization_request['next_url'])
        else:
            return redirect('/')
    except SSOException as e:
        if settings.DEBUG:
            return render(request, 'django_sso/token_validation_error.html', context={
                'error': e
            })
        else:
            return redirect('/')


def logout(request):
    if not request.user.is_anonymous:
        try:
            request_deauthentication(request.user)
            django.contrib.auth.logout(request)
        except Exception as e:
            if settings.DEBUG:
                return render(request, template_name='django_sso/deauthentication_error.html', context={
                    'error': e
                })

    return redirect('/')


@csrf_exempt
def deauthenticate(request):
    """
    Accept deauthenticate request from SSO server and process it
    """
    if request.method != 'POST':
        return HttpResponse(status=405)

    if (
        not request.POST.get('token', '').strip()
        or not request.POST.get('user_identy', '').strip()
    ):
        return JsonResponse({'error': _('Incorrect request')})

    user_model = get_user_model()

    user = user_model.objects.filter(**{
        f'{user_model.USERNAME_FIELD}': request.POST['user_identy']
    }).first()

    if user:
        deauthenticate_user(getattr(user, user_model.USERNAME_FIELD))

    return JsonResponse({'ok': True})
