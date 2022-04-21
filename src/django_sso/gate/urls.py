from django.urls import path
from django.views.generic import TemplateView

from . import views


urlpatterns = [
	path('login/', views.LoginView.as_view(), name="login"),
	path('logout/', views.LogoutView.as_view(), name="logout"),

	path('sso/obtain/', views.ObtainView.as_view(), name="obtain"),
	path('sso/get/', views.GetAuthenticationRequestView.as_view(), name="get"),
	path('sso/make_used/', views.MakeUsedView.as_view(), name="make_used"),
	path('sso/deauthenticate/', views.DeauthenticateView.as_view(), name="deauthenticate_view"),

	path('welcome/', TemplateView.as_view(template_name='django_sso/welcome.html'), name="welcome"),
]
