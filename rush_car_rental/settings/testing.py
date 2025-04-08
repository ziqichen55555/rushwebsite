"""
Rush Car Rental - 测试环境设置
"""
from .base import *
from rush_car_rental.utils.environment import get_database_config

# 测试模式下不开启DEBUG
DEBUG = False

# 允许的主机
ALLOWED_HOSTS = ['*']

# 测试环境数据库设置 - 使用PostgreSQL或SQLite
DATABASES = {
    'default': get_database_config()
}

# 测试环境使用控制台邮件后端
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# 测试环境缓存设置 - 使用内存缓存
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# 测试环境日志配置
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
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'test.log',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'WARNING',
            'propagate': True,
        },
        'rush_car_rental': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

# 确保日志目录存在
import os
if not os.path.exists(BASE_DIR / 'logs'):
    os.makedirs(BASE_DIR / 'logs')

# 测试媒体文件设置
MEDIA_ROOT = BASE_DIR / 'test_media'
MEDIA_URL = '/media/'