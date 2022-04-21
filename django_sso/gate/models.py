import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.db import models
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _

from django_sso.exceptions import SSOException


def service_token_generator():
	return get_random_string(Service.token.field.max_length)


class Service(models.Model):
	name = models.CharField(max_length=128, verbose_name=_('Name'))
	base_url = models.URLField(verbose_name=_('Base url'))
	enabled = models.BooleanField(default=False, verbose_name=_('Enabled'))
	token = models.CharField(max_length=128, verbose_name=_('Token'), unique=True, default=service_token_generator)

	def __str__(self):
		return self.base_url

	def requeset_deauthenticate(self, user_identy):
		"""
		push deauthentication event to subordinate service
		"""
		if not self.enabled:
			return

		try:
			data = requests.post(f'{self.base_url}/sso/deauthenticate/', {
				'token': self.token,
				'user_identy': user_identy
			})
		except Exception as e:
			if settings.DEBUG:
				raise e

	class Meta:
		verbose_name = _('External service')
		verbose_name_plural = _('External services')


def auth_token_generator():
	return get_random_string(AuthenticationRequest.token.field.max_length)


class AuthenticationRequest(models.Model):
	service = models.ForeignKey('Service', on_delete=models.CASCADE, verbose_name=_('Service'))
	created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
	token = models.CharField(max_length=128, verbose_name=_('Token'), default=auth_token_generator, unique=True)
	user_identy = models.CharField(max_length=128, verbose_name=_('User identy'), help_text=_('E-Mail, login, etc.'))
	next_url = models.CharField(max_length=512, verbose_name=_('Next url'), help_text=_('To go after success auth'))
	authenticated = models.BooleanField(default=False, verbose_name=_('Request has been activated'))
	used = models.BooleanField(default=False, verbose_name=_('Are used in external service'))

	class Meta:
		verbose_name = _('Authentication request')
		verbose_name_plural = _('Authentication requests')

	def activate(self, user: User):
		"""
		1) Активация запроса авторизации
		2) Отправка на подчинённый сервис базовой информации о пользователе для создания,
		если там отсутствует такой аккаунт.
		"""
		user_model = get_user_model()

		self.user_identy = getattr(user, user_model.USERNAME_FIELD)
		self.authenticated = True
		self.save()

		try:
			user_model = get_user_model()

			response = requests.post(f'{self.service.base_url}/sso/push/', {
				'token': self.service.token,
				'username': getattr(user, user_model.USERNAME_FIELD),
				'password': user.password
			}).json()

			if 'ok' in response:
				return
			elif 'error' in response:
				raise SSOException(response['error'])
			else:
				raise NotImplementedError(_('From service returned incorrect data'))
		except Exception as e:
			raise SSOException(str(e))


