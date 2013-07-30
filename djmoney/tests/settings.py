import warnings

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

warnings.simplefilter('ignore', Warning)

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'djmoney',
    'testapp'
)

SITE_ID = 1
ROOT_URLCONF = 'core.urls'

SECRET_KEY = 'foobar'

