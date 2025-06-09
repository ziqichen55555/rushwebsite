#!/usr/bin/env python
"""
测试新数据库配置
"""
import psycopg2

def test_new_database():
    """测试新数据库连接"""
    config = {
        'host': 'all-data-for-sql.postgres.database.azure.com',  # 新的服务器地址
        'database': 'rush-website-and-management-system',  # 新的数据库名
        'user': 'melbournerushcarrental',
        'password': 'rushrcm@250401',
        'port': 5432,
        'sslmode': 'require',
        'connect_timeout': 10
    }
    
    print("🔍 测试新数据库配置...")
    print(f"📍 服务器: {config['host']}")
    print(f"📍 数据库: {config['database']}")
    print(f"📍 用户: {config['user']}")
    
    try:
        conn = psycopg2.connect(**config)
        cursor = conn.cursor()
        
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"✅ 连接成功!")
        print(f"📊 PostgreSQL 版本: {version}")
        
        cursor.execute("SELECT current_database(), current_user;")
        db_info = cursor.fetchone()
        print(f"📊 当前数据库: {db_info[0]}")
        print(f"📊 当前用户: {db_info[1]}")
        
        # 检查是否是新数据库（应该没有表）
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        print(f"📊 现有表数量: {len(tables)}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False

if __name__ == "__main__":
    test_new_database() 