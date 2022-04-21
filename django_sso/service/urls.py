from django.urls import path

from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout, name='logout'),

    path('sso/test/', views.for_logged_only),
    path('sso/push/', views.accept_user_information),
    path('sso/accept/', views.authorize_from_sso),
    path('sso/deauthenticate/', views.deauthenticate, name="deauthenticate_view"),
]