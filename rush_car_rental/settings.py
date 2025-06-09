import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-8^vt5$8#3l0=r_g94u(&_v@a*8l&e1t1rkw(r&dj%qr1)4d@-1'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# CSRF Trusted Origins (for Replit domains)
CSRF_TRUSTED_ORIGINS = [
    'https://*.replit.app',
    'https://*.replit.dev',
    'https://*.worf.replit.dev',
    'https://*.repl.co',
]

# Add your specific Replit domain
import os
replit_domain = os.environ.get('REPLIT_DEV_DOMAIN')
if replit_domain:
    CSRF_TRUSTED_ORIGINS.append(f'https://{replit_domain}')
    # 确保也添加 http 版本，以防重定向问题
    CSRF_TRUSTED_ORIGINS.append(f'http://{replit_domain}')
    print(f"添加CSRF受信任域名: https://{replit_domain} 和 http://{replit_domain}")
    
# 添加 REPLIT_DOMAINS 环境变量中的所有域名（如果存在）
replit_domains = os.environ.get('REPLIT_DOMAINS', '')
if replit_domains:
    for domain in replit_domains.split(','):
        if domain:
            CSRF_TRUSTED_ORIGINS.append(f'https://{domain}')
            CSRF_TRUSTED_ORIGINS.append(f'http://{domain}')
            print(f"添加CSRF受信任域名: https://{domain} 和 http://{domain}")

# 注意：不再全局禁用 CSRF 中间件，而是对特定视图使用 csrf_exempt 装饰器

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    
    # Third-party apps
    'storages',
    'widget_tweaks',
    
    # Project apps
    'accounts.apps.AccountsConfig',
    'cars.apps.CarsConfig',
    'bookings.apps.BookingsConfig',
    'locations.apps.LocationsConfig',
    'pages.apps.PagesConfig',
    'dev.apps.DevConfig',
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

ROOT_URLCONF = 'rush_car_rental.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'rush_car_rental.wsgi.application'

# Database configuration - Azure Database for PostgreSQL Flexible Server
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'rush-website-and-management-system',  # 你的数据库名
        'USER': 'melbournerushcarrental',    # 🔴 替换为你的用户名
        'PASSWORD': 'rushrcm@250401',  # 🔴 替换为你的密码
        'HOST': 'all-data-for-sql.postgres.database.azure.com',  # 🔴 新的服务器地址
        'PORT': '5432',
        'OPTIONS': {
            'sslmode': 'require',
        },
    }
}

# Azure Blob Storage Configuration - 直接硬编码配置
# 启用 Azure Storage
USE_AZURE_STORAGE = True

if USE_AZURE_STORAGE:
    # Azure Storage Account 硬编码配置
    AZURE_ACCOUNT_NAME = 'allpicsandvideos'  # 🔴 替换为你的存储账户名
    AZURE_ACCOUNT_KEY = 'Ttct7cEvrGEtTuWQ83VfTJKVEaqzHwisU7uSP4MbYPKozhTx7m3H4ykQEuEnP28ft0CvkWiAOasA+AStYc/yxg=='       # 🔴 替换为你的存储密钥
    AZURE_CUSTOM_DOMAIN = None  # 🔵 可选：如果有CDN域名，在这里填写
    
    # Azure Storage settings for django-storages
    AZURE_SSL = True
    AZURE_AUTO_SIGN = True  # Automatically sign URLs for private containers
    AZURE_EXPIRATION_SECS = 3600  # URL expiration in seconds
    
    # Django 4.2+ Storage Configuration
    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.azure_storage.AzureStorage",
            "OPTIONS": {
                "account_name": AZURE_ACCOUNT_NAME,
                "account_key": AZURE_ACCOUNT_KEY,
                "azure_container": "rush-car-rental-media",
                "azure_ssl": AZURE_SSL,
            },
        },
        "staticfiles": {
            "BACKEND": "storages.backends.azure_storage.AzureStorage",
            "OPTIONS": {
                "account_name": AZURE_ACCOUNT_NAME,
                "account_key": AZURE_ACCOUNT_KEY,
                "azure_container": "rush-car-rental-static",
                "azure_ssl": AZURE_SSL,
            },
        },
    }
    
    # URL configurations
    AZURE_STATIC_CONTAINER = 'rush-car-rental-static'
    AZURE_MEDIA_CONTAINER = 'rush-car-rental-media'
    STATIC_URL = f'https://{AZURE_ACCOUNT_NAME}.blob.core.windows.net/{AZURE_STATIC_CONTAINER}/'
    MEDIA_URL = f'https://{AZURE_ACCOUNT_NAME}.blob.core.windows.net/{AZURE_MEDIA_CONTAINER}/'
    
    if AZURE_CUSTOM_DOMAIN:
        STATIC_URL = f'https://{AZURE_CUSTOM_DOMAIN}/{AZURE_STATIC_CONTAINER}/'
        MEDIA_URL = f'https://{AZURE_CUSTOM_DOMAIN}/{AZURE_MEDIA_CONTAINER}/'
    
else:
    # Local development storage
    STATIC_URL = '/static/'
    STATICFILES_DIRS = [
        BASE_DIR / 'static',
    ]
    STATIC_ROOT = BASE_DIR / 'staticfiles'
    
    # Media files for local development
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'

# Password validation
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
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Authentication settings
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
LOGIN_URL = '/accounts/login/'

# Logging configurations
LOGS_DIR = BASE_DIR / 'logs'
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '[{levelname}] {asctime} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': LOGS_DIR / 'django.log',
            'formatter': 'verbose',
        },
        'file_error': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': LOGS_DIR / 'django_error.log',
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['file_error', 'mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'bookings': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'accounts': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'cars': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'locations': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'pages': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'dev': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

# Stripe API settings
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY', '')
STRIPE_PUBLIC_KEY = os.environ.get('VITE_STRIPE_PUBLIC_KEY', '')
