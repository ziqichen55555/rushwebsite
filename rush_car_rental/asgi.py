"""
ASGI config for rush_car_rental project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""
import os
from dotenv import load_dotenv

# 加载环境变量，确保在Django加载配置前执行
load_dotenv()

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rush_car_rental.settings')

application = get_asgi_application()