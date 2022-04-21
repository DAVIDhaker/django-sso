from setuptools import setup, find_packages

setup(
    name='django_sso',
    version='1.0.4',
    author="DAVIDhaker",
    author_email='me@davidhaker.ru',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    package_data={
        'django_sso': [
            '**.html'
        ]
    },
    description='README.md',
    include_package_data=True,
    url='https://github.com/davidhaker/django-sso',
    keywords='Django SSO Single Sign-On',
    install_requires=[
        'django',
        'requests',
    ],
    python_requires='>=3',
)
