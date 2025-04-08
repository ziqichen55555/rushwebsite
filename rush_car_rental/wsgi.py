"""
WSGI config for rush_car_rental project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""
import os
from dotenv import load_dotenv

# 加载环境变量，确保在Django加载配置前执行
load_dotenv()

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rush_car_rental.settings')

application = get_wsgi_application()

# 如果在生产环境，初始化Cosmos DB连接测试
from rush_car_rental.utils.environment import is_production
if is_production():
    from rush_car_rental.utils.cosmos_db import CosmosDBManager
    if not CosmosDBManager.test_connection():
        import logging
        logging.error("无法连接到Cosmos DB，请检查配置！")