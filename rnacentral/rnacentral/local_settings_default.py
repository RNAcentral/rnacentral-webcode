DATABASES = {
    'default': {
    	'ENGINE': 'django.db.backends.',
        'NAME': '',
        'USER': '',
        'PASSWORD': '',
        'OPTIONS'  : { 'init_command' : 'SET storage_engine=MyISAM', },
    }
}

TEMPLATE_DIRS = (
	'',
)

STATIC_ROOT = ''

EMAIL_HOST = ''
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_PORT =
EMAIL_USE_TLS = True
EMAIL_RNACENTRAL_HELPDESK = ''

SECRET_KEY = ''

ADMINS = (
    ('', ''),
)

COMPRESS_ENABLED =
DEBUG =
ALLOWED_HOSTS = []

# django-debug-toolbar
INTERNAL_IPS = ('127.0.0.1',)
