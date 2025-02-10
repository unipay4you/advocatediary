from advocatediary.settings import *
from decouple import config



SECRET_KEY = config('SECRET_KEY')
#DEBUG = config('DEBUG', default=False, cast=bool)
#EMAIL_HOST = config('EMAIL_HOST', default='localhost')
#EMAIL_PORT = config('EMAIL_PORT', default=25, cast=int)