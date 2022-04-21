from django.contrib import admin
from django.http import JsonResponse


def login(request):
    return JsonResponse({'ok': True})

admin.autodiscover()
admin.site.login = login