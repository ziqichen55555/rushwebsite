"""
Rush Car Rental - 生产环境设置
"""
from .base import *
from rush_car_rental.utils.environment import get_database_config
import os

# 调试模式关闭
DEBUG = False

# 从环境变量获取Secret Key
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise Exception("生产环境必须设置SECRET_KEY环境变量!")

# 允许的主机
ALLOWED_HOSTS = [
    os.environ.get('SITE_DOMAIN', 'rush-car-rental.azurewebsites.net'),
    'localhost',
    '127.0.0.1'
]

# CORS设置
CORS_ALLOWED_ORIGINS = [
    f"https://{host}" for host in ALLOWED_HOSTS
]

# CSRF 设置
CSRF_TRUSTED_ORIGINS = [
    'https://*.replit.dev',
    'https://*.replit.app', 
    'https://*.replit.com',
    'https://*.worf.replit.dev',
    f"https://{host}" for host in ALLOWED_HOSTS if not host in ['localhost', '127.0.0.1']
]

# 开启HTTPS安全设置
# 在测试环境中,暂时关闭一些HTTPS安全设置
# 实际部署时需要启用这些设置
SECURE_SSL_REDIRECT = False  # 测试时设为False
SESSION_COOKIE_SECURE = False  # 测试时设为False
CSRF_COOKIE_SECURE = False  # 测试时设为False
SECURE_HSTS_SECONDS = 0  # 测试时设为0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False  # 测试时设为False
SECURE_HSTS_PRELOAD = False  # 测试时设为False

# 数据库设置 - 使用Azure Cosmos DB (PostgreSQL接口)
DATABASES = {
    'default': get_database_config()
}

# Azure存储设置
if os.environ.get('AZURE_STORAGE_CONNECTION_STRING'):
    # 启用Azure Blob Storage作为静态文件存储
    STATICFILES_STORAGE = 'storages.backends.azure_storage.AzureStaticStorage'
    AZURE_STORAGE_KEY = os.environ.get('AZURE_STORAGE_KEY')
    AZURE_ACCOUNT_NAME = os.environ.get('AZURE_ACCOUNT_NAME')
    AZURE_STATIC_CONTAINER = os.environ.get('AZURE_STATIC_CONTAINER', 'static')
    AZURE_CUSTOM_DOMAIN = os.environ.get('AZURE_CDN_DOMAIN')

# 生产环境日志配置
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'structured': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'structured',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'rush_car_rental': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# 电子邮件设置
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@rushcarrental.com')