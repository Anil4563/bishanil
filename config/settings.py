import os
from pathlib import Path
from decouple import config

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# Security
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost').split(',')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'django.contrib.sites', 
    'homepage',
    'dental',
    'eyecare',
    'doctors',
    'appointments',
    'contact',
    'gallery',
    'blog',
    'accounts',
    'chatbot',
    'seo',
    'payments',
    'feedback',
    'dashboard',
]
# Make sure SITE_ID is set
SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'seo.context_processors.seo_settings',
                'contact.context_processors.contact_settings',
                'doctors.context_processors.doctor_profile',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kathmandu'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Add at the bottom of settings.py
LOGOUT_REDIRECT_URL = '/'
LOGOUT_URL = '/accounts/logout/'

# SEO Settings
CANONICAL_URL = 'https://www.shreekrishnadental.com'  # Change to your domain
DEFAULT_META_IMAGE = '/static/images/og-image.jpg'

# Payment Gateway Settings
# Khalti
KHALTI_SECRET_KEY = 'test_secret_key_f6e1b3e5b4f54b4e8b2b1c5d3e8a9b7c'
KHALTI_PUBLIC_KEY = 'test_public_key_f6e1b3e5b4f54b4e8b2b1c5d3e8a9b7c'
KHALTI_VERIFY_URL = 'https://khalti.com/api/v2/payment/verify/'
KHALTI_EPAY_URL = 'https://khalti.com/api/v2/epay/start/'

# eSewa
ESEWA_MERCHANT_CODE = 'NP-ESEWA-MERCHANT'
ESEWA_SECRET_KEY = '8gBm/:&EnhH.1/q'
ESEWA_SUCCESS_URL = 'http://127.0.0.1:8000/payments/esewa/success/'
ESEWA_FAILURE_URL = 'http://127.0.0.1:8000/payments/esewa/failure/'
ESEWA_URL = 'https://rc-epay.esewa.com.np/api/epay/main/v2/form'

# Test mode (True for development)
PAYMENT_TEST_MODE = True

# Email Settings (for development - prints to console)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'noreply@bishanildental.com'