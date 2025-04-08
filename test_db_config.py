#!/usr/bin/env python
"""
数据库配置测试脚本
用于测试不同环境的数据库配置是否正确
"""
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rush_car_rental.settings')
django.setup()

from rush_car_rental.utils.environment import get_environment, get_database_config
from django.db import connection


def test_current_environment():
    """测试当前环境的数据库配置"""
    env = get_environment()
    print(f"当前环境: {env}")
    
    db_config = get_database_config()
    print("\n数据库配置:")
    for key, value in db_config.items():
        if key.lower() in ('password',):
            print(f"  {key}: ******(已隐藏)")
        else:
            print(f"  {key}: {value}")

    print("\n测试数据库连接...")
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT version()")
            version = cursor.fetchone()[0]
            print(f"连接成功! 数据库版本: {version}")
            
            # 获取表数量
            cursor.execute("""
                SELECT count(*) 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            table_count = cursor.fetchone()[0]
            print(f"数据库中有 {table_count} 个表")
            
            # 显示表列表
            if table_count > 0:
                cursor.execute("""
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    ORDER BY table_name
                """)
                tables = cursor.fetchall()
                print("\n表列表:")
                for table in tables:
                    print(f"  - {table[0]}")
    except Exception as e:
        print(f"连接失败: {e}")


def test_specific_environment(env_name, use_postgres=None):
    """测试特定环境的数据库配置"""
    original_env = os.environ.get('DJANGO_ENVIRONMENT')
    original_pg = os.environ.get('USE_POSTGRES')
    
    try:
        os.environ['DJANGO_ENVIRONMENT'] = env_name
        if use_postgres is not None:
            os.environ['USE_POSTGRES'] = str(use_postgres)
        
        print(f"\n===== 测试环境: {env_name} =====")
        if use_postgres is not None:
            print(f"USE_POSTGRES: {use_postgres}")
        
        db_config = get_database_config()
        print("\n数据库配置:")
        for key, value in db_config.items():
            if key.lower() in ('password',):
                print(f"  {key}: ******(已隐藏)")
            else:
                print(f"  {key}: {value}")
    finally:
        # 恢复原始环境变量
        if original_env:
            os.environ['DJANGO_ENVIRONMENT'] = original_env
        else:
            os.environ.pop('DJANGO_ENVIRONMENT', None)
        
        if original_pg:
            os.environ['USE_POSTGRES'] = original_pg
        elif use_postgres is not None:
            os.environ.pop('USE_POSTGRES', None)


if __name__ == "__main__":
    # 测试当前环境
    test_current_environment()
    
    # 测试各种环境配置
    test_specific_environment('development', False)
    test_specific_environment('development', True)
    test_specific_environment('testing')
    test_specific_environment('production')