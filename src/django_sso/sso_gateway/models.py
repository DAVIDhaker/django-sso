import inspect

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.db import models
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _

from django_sso.exceptions import SSOException

user_model = get_user_model()


def service_token_generator():
	return get_random_string(Service.token.field.max_length)


class Service(models.Model):
	name = models.CharField(max_length=128, verbose_name=_('Name'))
	base_url = models.URLField(verbose_name=_('Base url'))
	enabled = models.BooleanField(default=False, verbose_name=_('Enabled'))
	token = models.CharField(max_length=128, verbose_name=_('Token'), unique=True, default=service_token_generator)

	def __str__(self):
		return self.base_url

	def _send_event(self, event_type, data):
		result = requests.post(
			f'{self.base_url}/sso/event/',
			json={
				'type': event_type,
				'token': self.token,
				**data
			},
			headers={
				"Content-Type": "application/json"
			}
		)
		fail = False
		text = None

		try:
			assert result.status_code == 200, f"{result.text}"
			data = result.json()

			ok = not not (data['ok'] if 'ok' in data else False)

			if ok:
				return ok
			elif 'error' in data:
				raise Exception(f"{_('Error raised on subordinate service')}: {data['error']}")
			else:
				raise Exception(result.text)
		except Exception as e:
			if settings.DEBUG:
				raise Exception(
					f'{_("Incorrect response from subbordinated service")}: '
					f'STATUS={result.status_code}; TEXT={e}'
				)
			else:
				return False

	def update_account(self, user) -> bool:
		"""
		Send account information to subordinated service, if subordinated service is active
		"""
		if not self.enabled:
			return True

		user_model = get_user_model()

		fields = {}

		for field in ('is_active', 'is_staff', 'is_superuser'):
			if hasattr(user_model, field):
				fields[field] = bool(getattr(user, field))

		return self._send_event('update_account', {
			"is_active": user.is_active,
			"is_staff": user.is_staff,
			"is_superuser": user.is_superuser,
			"username": getattr(user, user_model.USERNAME_FIELD),
		})

	def deauthenticate(self, user):
		"""
		Send deauthentication event to subordinate service, if that active
		"""
		if not self.enabled:
			return True

		return self._send_event('deauthenticate', {
			'username': getattr(user, user_model.USERNAME_FIELD)
		})

	class Meta:
		verbose_name = _('Subordinated service')
		verbose_name_plural = _('Subordinated services')


def auth_token_generator():
	return get_random_string(AuthenticationRequest.token.field.max_length)


class AuthenticationRequest(models.Model):
	service = models.ForeignKey('Service', on_delete=models.CASCADE, verbose_name=_('Service'))
	created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
	token = models.CharField(max_length=128, verbose_name=_('Token'), default=auth_token_generator, unique=True)
	user_identy = models.CharField(max_length=128, verbose_name=_('User identy'), help_text=_('E-Mail, login, etc.'))
	next_url = models.CharField(max_length=512, verbose_name=_('Next url'), help_text=_('To go after success auth'))
	authenticated = models.BooleanField(default=False, verbose_name=_('Request has been activated'))
	used = models.BooleanField(default=False, verbose_name=_('Are used in external sso service'))

	class Meta:
		verbose_name = _('Authentication request')
		verbose_name_plural = _('Authentication requests')

	def activate(self, user: User):
		"""
		1) Activate authentication request
		2) Send base information about user to subbordinate service
		"""
		user_model = get_user_model()

		self.user_identy = getattr(user, user_model.USERNAME_FIELD)
		self.authenticated = True
		self.save()

		try:
			return self.service.update_account(user)
		except Exception as e:
			raise SSOException(str(e))

	def __str__(self):
		return f'{_("Authenticate")} {self.user_identy} {_("on")} {self.service} {_("then go to")} {self.next_url}'
