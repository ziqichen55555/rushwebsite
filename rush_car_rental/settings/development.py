"""
Rush Car Rental - 开发环境设置
"""
from .base import *

# 调试模式开启
DEBUG = True

# 允许的主机
ALLOWED_HOSTS = ['*']

# 安全设置 - 在Replit环境中允许跨域访问
CSRF_TRUSTED_ORIGINS = [
    'https://*.replit.dev',
    'https://*.replit.app',
    'https://*.repl.co',
    'https://*.worf.replit.dev',
]
CORS_ALLOW_ALL_ORIGINS = True

# 开发环境数据库设置 - Azure Database for PostgreSQL Flexible Server
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'rush-website-and-management-system',  # 新的数据库名
        'USER': 'melbournerushcarrental',    # 用户名
        'PASSWORD': 'rushrcm@250401',  # 密码
        'HOST': 'all-data-for-sql.postgres.database.azure.com',  # 新的服务器地址
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
    AZURE_ACCOUNT_NAME = 'allpicsandvideos'  # 新的存储账户名
    AZURE_ACCOUNT_KEY = 'Ttct7cEvrGEtTuWQ83VfTJKVEaqzHwisU7uSP4MbYPKozhTx7m3H4ykQEuEnP28ft0CvkWiAOasA+AStYc/yxg=='  # 新的存储密钥
    AZURE_CUSTOM_DOMAIN = None  # CDN域名（可选）
    
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
    # Local development storage fallback
    STATIC_URL = '/static/'
    STATICFILES_DIRS = [
        BASE_DIR / 'static',
    ]
    STATIC_ROOT = BASE_DIR / 'staticfiles'
    
    # Media files for local development
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'

# 开发环境邮件设置 - 输出到控制台
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# 日志配置
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
        'sentimental': {
            'format': '💔 {asctime} {message}',
            'style': '{',
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'debug.log',
            'formatter': 'verbose',
        },
        'emotions': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'emotional.log',
            'formatter': 'sentimental',
        }
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'rush_car_rental': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'accounts': {
            'handlers': ['console', 'emotions'],
            'level': 'INFO',
            'propagate': False,
        },
        'bookings': {
            'handlers': ['console', 'emotions'],
            'level': 'INFO',
            'propagate': False,
        },
        'cars': {
            'handlers': ['console', 'emotions'],
            'level': 'INFO',
            'propagate': False,
        },
        'locations': {
            'handlers': ['console', 'emotions'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# 确保日志目录存在
import os
if not os.path.exists(BASE_DIR / 'logs'):
    os.makedirs(BASE_DIR / 'logs')