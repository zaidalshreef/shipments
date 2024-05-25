"""
Django settings for shipment_management project.

Generated by 'django-admin startproject' using Django 5.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""
from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-vxrnxz99$&v84hxgh3o_pzp+t&_$-q-#rq55%e8w3qar#q*f5%')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [os.environ.get('ALLOWED_HOSTS',"techsynapse.org"), 'localhost']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'shipments.apps.ShipmentsConfig',
    
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'shipment_management.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'shipment_management.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB', 'postgres'),
        'USER': os.environ.get('POSTGRES_USER', 'postgres'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'postgres'),
        'HOST': os.environ.get('POSTGRES_HOST', 'db'),
        'PORT': os.environ.get('POSTGRES_PORT', '5432'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Riyadh'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
CSRF_TRUSTED_ORIGINS = [
    os.environ.get('CSRF_TRUSTED_ORIGINS',"https://techsynapse.org")
]


# Authentication settings
LOGIN_REDIRECT_URL = '/shipments/home/'  # Redirect to the home page after login
LOGOUT_REDIRECT_URL = '/shipments/home/'  # Redirect to the home page after logout

# Email settings
# Uncomment the following settings to use the SMTP email backend
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = os.environ.get('EMAIL_HOST','smtp.gmail.com')
# EMAIL_PORT = os.environ.get('EMAIL_PORT','587')
# EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS','Myshipment.sam@gmail.com')
# EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER','Myshipment.sam@gmail.com')
# EMAIL_HOST_PASSWORD =   os.environ.get('EMAIL_HOST_PASSWORD','Myshipment.sam@gmail.com')

INTERNAL_STAFF_EMAILS = ['Myshipment.sam@gmail.com']  # Add the email addresses of the internal staff
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL','Myshipment.sam@gmail.com')  # Add the email address of the default sender
#BKCJZV75YPQ929PTZHKTNYJY

# Alternatively, for development purposes, you can use the console backend to print emails to the console
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'



# Add your API credentials to settings
SALLA_API_KEY = os.environ.get('SALLA_API_KEY', '8d20a45d-ca26-4910-b6ca-1b49f0298632')
SALLA_API_SECRET = os.environ.get('SALLA_API_SECRET','37686b0677d48c01cc8eb9b7ad2e2cea')
