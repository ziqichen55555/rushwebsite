#!/usr/bin/env python
"""
检查 Django 设置和数据库配置
"""

import os
import sys
import django
from pathlib import Path

# 设置 Django 环境
sys.path.append(str(Path(__file__).resolve().parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rush_car_rental.settings')

try:
    django.setup()
    from django.conf import settings
    
    print("🔍 Django 设置检查")
    print("=" * 50)
    print(f"设置模块: {settings.SETTINGS_MODULE}")
    print(f"DEBUG: {settings.DEBUG}")
    
    print("\n📊 数据库配置:")
    db_config = settings.DATABASES['default']
    for key, value in db_config.items():
        if key == 'PASSWORD':
            print(f"  {key}: {'*' * len(str(value))}")
        else:
            print(f"  {key}: {value}")
    
    print(f"\n🗂️ Azure Storage 配置:")
    print(f"  USE_AZURE_STORAGE: {getattr(settings, 'USE_AZURE_STORAGE', 'Not set')}")
    print(f"  AZURE_ACCOUNT_NAME: {getattr(settings, 'AZURE_ACCOUNT_NAME', 'Not set')}")
    print(f"  AZURE_STATIC_CONTAINER: {getattr(settings, 'AZURE_STATIC_CONTAINER', 'Not set')}")
    print(f"  AZURE_MEDIA_CONTAINER: {getattr(settings, 'AZURE_MEDIA_CONTAINER', 'Not set')}")
    print(f"  STATIC_URL: {getattr(settings, 'STATIC_URL', 'Not set')}")
    print(f"  MEDIA_URL: {getattr(settings, 'MEDIA_URL', 'Not set')}")
    
    print(f"\n📦 已安装的应用:")
    for app in settings.INSTALLED_APPS:
        if 'storages' in app or 'rush_car_rental' in app or 'accounts' in app or 'cars' in app:
            print(f"  ✅ {app}")
    
except Exception as e:
    print(f"❌ 错误: {e}")
    print(f"错误类型: {type(e).__name__}") 