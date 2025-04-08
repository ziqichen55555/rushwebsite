import os
from django.conf import settings

def environment_processor(request):
    """
    将环境信息添加到模板上下文
    """
    environment = os.environ.get('DJANGO_ENVIRONMENT', 'development')
    
    return {
        'environment': environment,
        'is_production': environment == 'production',
        'is_development': environment == 'development',
        'is_testing': environment == 'testing',
        'debug': settings.DEBUG,
    }