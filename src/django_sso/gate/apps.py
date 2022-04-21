from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DjangoSsoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_sso.gate'
    verbose_name = _('Single Sign-On')
