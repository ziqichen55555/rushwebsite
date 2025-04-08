"""
Rush Car Rental - 开发环境设置
"""
from .base import *
from rush_car_rental.utils.environment import get_database_config

# 调试模式开启
DEBUG = True

# 允许的主机
ALLOWED_HOSTS = ['*']

# 开发环境数据库设置
DATABASES = {
    'default': get_database_config()
}

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
    },
}

# 确保日志目录存在
import os
if not os.path.exists(BASE_DIR / 'logs'):
    os.makedirs(BASE_DIR / 'logs')