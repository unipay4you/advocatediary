
from advocatediary.settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'database/db.sqlite3',
    }
}


STATIC_URL = '/static/'

if DEBUG:
    STATICFILES_DIRS = [
        os.path.join(BASE_DIR, 'static')
    ]
else:
    STATIC_ROOT = os.path.join(BASE_DIR, 'static')

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


DBBACKUP_STORAGE = 'storages.backends.ftp.FTPStorage'
DBBACKUP_STORAGE_OPTIONS = {'location': 'ftp://dharm:dharm@192.168.1.5:21/'}
DBBACKUP_CLEANUP_KEEP = 2


LOG_DIR = os.path.join(BASE_DIR, 'logs')

if not os.path.exists(LOG_DIR):
    os.mkdir(LOG_DIR)


LOGGING ={
    'version':1,
    "disable_existing_loggers": False,

    'loggers':{
        'django':{
            'handlers':['file','file2','file3','file4','file5'],
            'level':'DEBUG'
        }
    },
    'handlers':{
        'file':{
            'level':'INFO',
            'class': 'logging.FileHandler',
            'filename': f'{LOG_DIR}/info.log',
            'formatter':'simpleRe',
        },
        'file2':{
            'level':'DEBUG',
            'class': 'logging.FileHandler',
            'filename': f'{LOG_DIR}/debug.log',
            'formatter':'simpleRe',
        },
        'file3':{
            'level':'WARNING',
            'class': 'logging.FileHandler',
            'filename': f'{LOG_DIR}/warning.log',
            'formatter':'simpleRe',
        },
        'file4':{
            'level':'ERROR',
            'class': 'logging.FileHandler',
            'filename': f'{LOG_DIR}/error.log',
            'formatter':'simpleRe',
        },
        'file5':{
            'level':'CRITICAL',
            'class': 'logging.FileHandler',
            'filename': f'{LOG_DIR}/critical.log',
            'formatter':'simpleRe',
        }
    },
    'formatters':{
       'simpleRe': {
            "format": "{name} {levelname} {asctime} {module} {process:d} {thread:d} {message}",
            'style': '{',
        }

    }
}



