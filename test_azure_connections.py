#!/usr/bin/env python
"""
Azure 连接测试脚本
测试 Azure Database for PostgreSQL 和 Azure Blob Storage 的连接状态
"""

import os
import sys
import django
from pathlib import Path

# 设置 Django 环境
sys.path.append(str(Path(__file__).resolve().parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rush_car_rental.settings')
django.setup()

from django.db import connection
from django.conf import settings
from azure.storage.blob import BlobServiceClient
import psycopg2
from datetime import datetime

def test_postgresql_connection():
    """测试 PostgreSQL 数据库连接"""
    print("🔍 测试 Azure PostgreSQL 连接...")
    print("-" * 50)
    
    try:
        # 获取数据库配置
        db_config = settings.DATABASES['default']
        print(f"📍 服务器地址: {db_config['HOST']}")
        print(f"📍 数据库名称: {db_config['NAME']}")
        print(f"📍 用户名: {db_config['USER']}")
        print(f"📍 端口: {db_config['PORT']}")
        print(f"📍 SSL模式: {db_config['OPTIONS'].get('sslmode', 'N/A')}")
        
        # 测试 Django 数据库连接
        print("\n🔗 测试 Django 数据库连接...")
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            print(f"✅ Django 连接成功!")
            print(f"📊 PostgreSQL 版本: {version}")
            
            # 测试基本查询
            cursor.execute("SELECT current_database(), current_user;")
            db_info = cursor.fetchone()
            print(f"📊 当前数据库: {db_info[0]}")
            print(f"📊 当前用户: {db_info[1]}")
            
            # 检查数据库表
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
            tables = cursor.fetchall()
            print(f"📊 数据库表数量: {len(tables)}")
            if tables:
                print("📋 现有表:")
                for table in tables[:10]:  # 只显示前10个表
                    print(f"   - {table[0]}")
                if len(tables) > 10:
                    print(f"   ... 还有 {len(tables) - 10} 个表")
            
        # 测试直接 psycopg2 连接
        print("\n🔗 测试直接 psycopg2 连接...")
        conn_str = f"host={db_config['HOST']} dbname={db_config['NAME']} user={db_config['USER']} password={db_config['PASSWORD']} port={db_config['PORT']} sslmode=require"
        
        conn = psycopg2.connect(conn_str)
        cursor = conn.cursor()
        cursor.execute("SELECT NOW();")
        current_time = cursor.fetchone()[0]
        print(f"✅ psycopg2 直接连接成功!")
        print(f"📊 服务器时间: {current_time}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ PostgreSQL 连接失败!")
        print(f"🚨 错误类型: {type(e).__name__}")
        print(f"🚨 错误信息: {str(e)}")
        
        # 常见错误解决建议
        error_str = str(e).lower()
        print("\n💡 可能的解决方案:")
        
        if "authentication failed" in error_str:
            print("   - 检查用户名和密码是否正确")
            print("   - 确认用户名格式是否正确（可能需要 username@servername 格式）")
            
        elif "could not connect to server" in error_str:
            print("   - 检查服务器地址是否正确")
            print("   - 确认网络连接是否正常")
            print("   - 检查防火墙设置，确保允许当前IP访问")
            
        elif "database" in error_str and "does not exist" in error_str:
            print("   - 检查数据库名称是否正确")
            print("   - 确认数据库是否已创建")
            
        elif "ssl" in error_str:
            print("   - 检查SSL连接设置")
            print("   - 确认服务器支持SSL连接")
            
        return False

def test_azure_storage_connection():
    """测试 Azure Blob Storage 连接"""
    print("\n🔍 测试 Azure Blob Storage 连接...")
    print("-" * 50)
    
    try:
        account_name = settings.AZURE_ACCOUNT_NAME
        account_key = settings.AZURE_ACCOUNT_KEY
        
        print(f"📍 存储账户名: {account_name}")
        print(f"📍 静态文件容器: {settings.AZURE_STATIC_CONTAINER}")
        print(f"📍 媒体文件容器: {settings.AZURE_MEDIA_CONTAINER}")
        
        # 创建 BlobServiceClient
        connection_string = f"DefaultEndpointsProtocol=https;AccountName={account_name};AccountKey={account_key};EndpointSuffix=core.windows.net"
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        
        # 测试连接
        print(f"\n🔗 测试存储账户连接...")
        account_info = blob_service_client.get_account_information()
        print(f"✅ Azure Storage 连接成功!")
        print(f"📊 账户类型: {account_info.get('account_kind', 'N/A')}")
        print(f"📊 SKU名称: {account_info.get('sku_name', 'N/A')}")
        
        # 列出容器
        print(f"\n📋 列出现有容器...")
        containers = list(blob_service_client.list_containers())
        print(f"📊 容器总数: {len(containers)}")
        
        required_containers = [settings.AZURE_STATIC_CONTAINER, settings.AZURE_MEDIA_CONTAINER]
        existing_containers = [c.name for c in containers]
        
        for container_name in required_containers:
            if container_name in existing_containers:
                print(f"✅ 容器 '{container_name}' 存在")
                
                # 测试容器访问
                container_client = blob_service_client.get_container_client(container_name)
                properties = container_client.get_container_properties()
                print(f"   📊 创建时间: {properties.last_modified}")
                
                # 列出前几个文件
                blobs = list(container_client.list_blobs(max_results=5))
                print(f"   📊 文件数量 (前5个): {len(blobs)}")
                for blob in blobs:
                    print(f"   📄 {blob.name} ({blob.size} bytes)")
                    
            else:
                print(f"⚠️  容器 '{container_name}' 不存在")
                
                # 尝试创建容器
                try:
                    container_client = blob_service_client.create_container(container_name)
                    print(f"✅ 成功创建容器 '{container_name}'")
                except Exception as create_error:
                    print(f"❌ 创建容器失败: {str(create_error)}")
        
        # 测试文件上传
        print(f"\n🔗 测试文件上传...")
        test_container = settings.AZURE_STATIC_CONTAINER
        test_blob_name = f"test_upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        test_content = f"测试上传 - {datetime.now()}"
        
        blob_client = blob_service_client.get_blob_client(
            container=test_container, 
            blob=test_blob_name
        )
        
        blob_client.upload_blob(test_content, overwrite=True)
        print(f"✅ 测试文件上传成功: {test_blob_name}")
        
        # 测试文件下载
        download_stream = blob_client.download_blob()
        downloaded_content = download_stream.readall().decode('utf-8')
        print(f"✅ 测试文件下载成功: {downloaded_content}")
        
        # 删除测试文件
        blob_client.delete_blob()
        print(f"✅ 测试文件清理完成")
        
        # 显示URL信息
        print(f"\n🌐 存储URL信息:")
        print(f"📍 静态文件URL: {settings.STATIC_URL}")
        print(f"📍 媒体文件URL: {settings.MEDIA_URL}")
        
        return True
        
    except Exception as e:
        print(f"❌ Azure Storage 连接失败!")
        print(f"🚨 错误类型: {type(e).__name__}")
        print(f"🚨 错误信息: {str(e)}")
        
        # 常见错误解决建议
        error_str = str(e).lower()
        print("\n💡 可能的解决方案:")
        
        if "authentication" in error_str or "signature" in error_str:
            print("   - 检查存储账户名和访问密钥是否正确")
            print("   - 确认访问密钥没有过期")
            
        elif "not found" in error_str:
            print("   - 检查存储账户名是否正确")
            print("   - 确认存储账户是否存在")
            
        elif "network" in error_str or "connection" in error_str:
            print("   - 检查网络连接")
            print("   - 确认防火墙设置允许访问Azure服务")
            
        return False

def main():
    """主测试函数"""
    print("🚀 Azure 服务连接测试")
    print("=" * 60)
    print(f"⏰ 测试时间: {datetime.now()}")
    print("=" * 60)
    
    # 测试 PostgreSQL
    postgres_success = test_postgresql_connection()
    
    # 测试 Azure Storage
    storage_success = test_azure_storage_connection()
    
    # 总结
    print("\n" + "=" * 60)
    print("📊 测试结果总结")
    print("=" * 60)
    print(f"PostgreSQL 连接: {'✅ 成功' if postgres_success else '❌ 失败'}")
    print(f"Azure Storage 连接: {'✅ 成功' if storage_success else '❌ 失败'}")
    
    if postgres_success and storage_success:
        print("\n🎉 所有Azure服务连接成功！可以开始使用了。")
        print("\n📋 下一步建议:")
        print("   1. 运行数据库迁移: python manage.py migrate")
        print("   2. 创建超级用户: python manage.py createsuperuser")
        print("   3. 收集静态文件: python manage.py collectstatic")
        print("   4. 加载初始数据: python setup_data.py")
    else:
        print("\n⚠️  部分服务连接失败，请根据上述错误信息进行调试。")

if __name__ == "__main__":
    main() 