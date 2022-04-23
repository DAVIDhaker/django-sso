from setuptools import setup, find_packages

setup(
    name='django_sso',
    version='1.1.0',
    author="DAVIDhaker",
    author_email='me@davidhaker.ru',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    package_data={
        'django_sso': [
            '**.html'
        ]
    },
    description='Django Single Sign-On implementation',
    long_description_content_type='text/markdown',
    long_description=open('README.md', 'r').read(),
    include_package_data=True,
    url='https://github.com/davidhaker/django-sso',
    url_download='https://pypi.org/project/django-sso/',
    keywords='Django SSO Single Sign-On',
    install_requires=[
        'django',
        'requests',
    ],
    python_requires='>=3',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Framework :: Django :: 2',
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 2.1',
        'Framework :: Django :: 2.2',
        'Framework :: Django :: 3',
        'Framework :: Django :: 3.0',
        'Framework :: Django :: 3.1',
        'Framework :: Django :: 3.2',
        'Framework :: Django :: 4',
        'Framework :: Django :: 4.0',
        'Natural Language :: English',
        'Natural Language :: Russian',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP :: Session'
    ],
)
