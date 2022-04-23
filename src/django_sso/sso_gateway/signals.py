from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Service

user_model = get_user_model()


@receiver(post_save, sender=user_model)
def push_update_user_event(sender, instance, **kwargs):
    for service in Service.objects.filter(enabled=True):
        service.update_account(instance)
