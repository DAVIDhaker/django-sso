import importlib

from django.apps import AppConfig
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from django.core.exceptions import ImproperlyConfigured
from .backend import EventAcceptor


class ServiceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_sso.sso_service'

    def ready(self):
        for variable in ('SSO_TOKEN', 'LOGIN_URL', 'SSO_ROOT'):
            if not getattr(settings, variable, ''):
                raise ImproperlyConfigured(f"{variable} {_('settings variable not set')}")

        sso_event_acceptor_class = getattr(settings, 'SSO_EVENT_ACCEPTOR_CLASS', ''.strip())

        if sso_event_acceptor_class:
            if type(sso_event_acceptor_class) != str:
                raise ImproperlyConfigured(f"SSO_EVENT_ACCEPTOR_CLASS {_('must be string')}")

            try:
                [module_name, class_name] = settings.SSO_EVENT_ACCEPTOR_CLASS.rsplit('.', 1)
                module = importlib.import_module(module_name)
                class_ref = getattr(module, class_name, None)

                if not class_ref:
                    raise ImproperlyConfigured(_(
                        f'In SSO_EVENT_ACCEPTOR_CLASS declared module has no class named {class_name}'
                    ))

                if not isinstance(class_ref, EventAcceptor):
                    raise ImproperlyConfigured(
                        f'{settings.SSO_EVENT_ACCEPTOR_CLASS} {_("is not inherits")} '
                        f'django_sso.sso_service.backend.EventAcceptor'
                    )
            except ImproperlyConfigured as e:
                raise e
            except Exception as e:
                raise ImproperlyConfigured(_(
                    'Can\'t import sso event acceptor class from SSO_EVENT_ACCEPTOR_CLASS variable'
                ))
