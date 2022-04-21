# Django SSO (Single Sign-On) v1.0.0a

Realization of SSO for Django. 

This library contains two modules.

- <u>Server</u> side - `django_sso.gate` module
- <u>Service</u> side module - `django_sso`.`service`



### Concept

Conception of module requires Django user subsystem and Django session subsystem - supports custom classes, but he must be based on classical Django classes (AbstractUser / AbstractBaseUser, etc..). This means that you have two ways. One: Do nothing, just install library to server/client and use it. Two: Create own user models based on abstract user classes (models).



## Integration

#### Server side

1) Add to `INSTALLED_APPS` `django_sso`.`gate`

```python
# project/settings.py
INSTALLED_APPS = [
    # ...
    'django_sso.gate',
]
```



2) Migrate server models

```python
./manage.py migrate gate
```



3) Add urls to project:

```python
# project/urls.py

urlpatterns = [
	# ...,
	path('', include('django_sso.gate.urls')),
]
```



Then server side is ready to use!

#### Client side

1) Add `django_sso`.`service` to `INSTALLED_APPS` 

```python
# project/settings.py
INSTALLED_APPS = [
    # ...
    'django_sso.service',
]
```



2) Add urls to service application

```python
# project/urls.py

urlpatterns = [
    # ...,
    path('', include('django_sso.service.urls')),    
]
```



3) Setup settings variables

```python
# project/settings.py

# Django variable. URL for unlogged users. We redirect it to our view.
LOGIN_URL = '/login/'

# Specify SSO server base url
SSO_ROOT = 'https://sso.project.test'

# Specify application token obtained in SSO server in the admin panel
SSO_TOKEN = 'reej8Vt5kbCPJM9mZQqYsvfxC...'
```

