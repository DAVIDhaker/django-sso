from django.contrib.auth import get_user_model

from project.src.django_sso import deauthenticate_user


class EventAcceptor:
    """
    This class processes all events received from SSO service
    You can override it for change behavior

    Here method name are equal to event type. All method names
    starts with _ are private and not resolved as event-types
    """

    def _get_user(self, username):
        """
        Get user by USERNAME_FIELD (unique field with always filled user identy)
        By default in Django - username. Name of field stored in USERNAME_FIELD
        """
        return get_user_model().objects.filter(**{
            f'{get_user_model().USERNAME_FIELD}': username
        }).first()

    def update_account(self, username, is_active=None, is_staff=None, is_superuser=None):
        """
        Update or create user
        """
        user_model = get_user_model()
        user_model_field_names = [f.name for f in user_model._meta.fields]

        fields = {}

        if type(is_active) == bool and 'is_active' in user_model_field_names:
            fields['is_active'] = is_active

        if type(is_staff) == bool and 'is_staff' in user_model_field_names:
            fields['is_staff'] = is_staff

        if type(is_superuser) == bool and 'is_superuser' in user_model_field_names:
            fields['is_superuser'] = is_superuser

        user_model.objects.update_or_create(**{
            f'{user_model.USERNAME_FIELD}': username,
            'defaults': fields
        })

    def deauthenticate(self, username):
        """
        Username = it's user identy
        """
        deauthenticate_user(username)