
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

