#!/usr/bin/env python
"""
简单的 PostgreSQL 连接测试
"""

import psycopg2
import socket
from datetime import datetime

def test_network_connectivity():
    """测试网络连通性"""
    host = 'rush-website-car-subscription.postgres.database.azure.com'
    port = 5432
    timeout = 10
    
    print(f"🔍 测试网络连通性...")
    print(f"📍 主机: {host}")
    print(f"📍 端口: {port}")
    print(f"📍 超时: {timeout}秒")
    
    try:
        # 尝试TCP连接
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            print(f"✅ TCP连接成功!")
            return True
        else:
            print(f"❌ TCP连接失败 (错误代码: {result})")
            return False
            
    except socket.timeout:
        print(f"❌ 连接超时 ({timeout}秒)")
        return False
    except Exception as e:
        print(f"❌ 网络错误: {e}")
        return False

def test_postgresql_connection():
    """测试PostgreSQL连接"""
    print(f"\n🔍 测试 PostgreSQL 连接...")
    
    config = {
        'host': 'rush-website-car-subscription.postgres.database.azure.com',
        'database': 'rush_car_rental',
        'user': 'melbournerushcarrental',
        'password': 'rushrcm@250401',
        'port': 5432,
        'sslmode': 'require',
        'connect_timeout': 10
    }
    
    try:
        print(f"📍 尝试连接到: {config['host']}")
        print(f"📍 数据库: {config['database']}")
        print(f"📍 用户: {config['user']}")
        
        conn = psycopg2.connect(**config)
        cursor = conn.cursor()
        
        # 测试基本查询
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"✅ PostgreSQL 连接成功!")
        print(f"📊 版本: {version}")
        
        cursor.execute("SELECT current_database(), current_user;")
        db_info = cursor.fetchone()
        print(f"📊 当前数据库: {db_info[0]}")
        print(f"📊 当前用户: {db_info[1]}")
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.OperationalError as e:
        print(f"❌ PostgreSQL 连接失败!")
        print(f"🚨 错误: {e}")
        
        error_str = str(e).lower()
        print(f"\n💡 可能的解决方案:")
        
        if "timeout" in error_str or "timed out" in error_str:
            print("   🔥 连接超时问题:")
            print("   - 检查 Azure PostgreSQL 防火墙设置")
            print("   - 添加你的 IP 地址到允许列表")
            print("   - 确认服务器是否在运行")
            print("   - 检查网络安全组设置")
            
        elif "authentication failed" in error_str:
            print("   🔑 认证失败:")
            print("   - 检查用户名和密码是否正确")
            print("   - 确认用户名格式 (可能需要完整格式)")
            
        elif "does not exist" in error_str:
            print("   📁 数据库不存在:")
            print("   - 检查数据库名称是否正确")
            print("   - 确认数据库是否已创建")
            
        return False
        
    except Exception as e:
        print(f"❌ 其他错误: {e}")
        return False

def get_public_ip():
    """获取当前公网IP"""
    try:
        import requests
        response = requests.get('https://api.ipify.org', timeout=5)
        ip = response.text.strip()
        print(f"🌐 当前公网IP: {ip}")
        return ip
    except:
        print(f"❌ 无法获取公网IP")
        return None

def main():
    """主测试函数"""
    print("🚀 PostgreSQL 连接诊断")
    print("=" * 50)
    print(f"⏰ 测试时间: {datetime.now()}")
    print("=" * 50)
    
    # 获取当前IP
    get_public_ip()
    
    # 测试网络连通性
    network_ok = test_network_connectivity()
    
    if network_ok:
        # 测试数据库连接
        db_ok = test_postgresql_connection()
        
        if db_ok:
            print(f"\n🎉 所有测试通过! PostgreSQL 连接正常。")
        else:
            print(f"\n⚠️ 数据库连接失败，但网络连通正常。请检查认证信息。")
    else:
        print(f"\n⚠️ 网络连接失败。请检查:")
        print("   1. Azure PostgreSQL 防火墙设置")
        print("   2. 网络安全组配置")
        print("   3. 服务器状态")
        print("   4. 本地网络连接")

if __name__ == "__main__":
    main() 