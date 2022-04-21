from django.contrib import admin
from .models import Service, AuthenticationRequest


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
	list_display = 'name', 'base_url', 'enabled'
	fields = 'name', 'base_url', 'token', 'enabled'
	readonly_fields = 'token',


@admin.register(AuthenticationRequest)
class AuthenticationRequestAdmin(admin.ModelAdmin):
	readonly_fields = 'token',
	list_display = (
		'service',
		'user_identy',
		'created_at',
		'used',
	)

	list_filter = 'service', 'used'
	search_fields = 'user_identy',

