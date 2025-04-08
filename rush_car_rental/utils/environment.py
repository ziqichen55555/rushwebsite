import os

def get_environment() -> str:
    """
    获取当前环境配置
    
    返回:
        'development', 'testing', 或 'production'
    """
    return os.environ.get('DJANGO_ENVIRONMENT', 'development')

def is_development() -> bool:
    """
    是否为开发环境
    """
    return get_environment() == 'development'

def is_testing() -> bool:
    """
    是否为测试环境
    """
    return get_environment() == 'testing'

def is_production() -> bool:
    """
    是否为生产环境
    """
    return get_environment() == 'production'

def should_use_postgres() -> bool:
    """
    是否应该使用PostgreSQL数据库
    """
    # 生产环境始终使用PostgreSQL
    if is_production():
        return True
    
    # 开发环境和测试环境可以通过环境变量控制
    use_postgres = os.environ.get('USE_POSTGRES', 'false').lower()
    return use_postgres in ('true', 'yes', '1')

def get_database_config():
    """
    根据当前环境返回数据库配置
    """
    from pathlib import Path
    
    # 项目根目录
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    
    # 默认使用SQLite配置
    default_db = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
    
    # 如果不使用PostgreSQL，直接返回SQLite配置
    if not should_use_postgres():
        return default_db

    # 生产环境使用Azure Cosmos DB (通过PostgreSQL接口)
    if is_production():
        # 确保DATABASE_URL环境变量已设置
        db_url = os.environ.get('DATABASE_URL')
        if not db_url:
            # 如果未设置DATABASE_URL，尝试使用其他环境变量
            return {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': os.environ.get('COSMOS_DB_NAME', ''),
                'USER': os.environ.get('COSMOS_DB_USER', ''),
                'PASSWORD': os.environ.get('COSMOS_DB_PASSWORD', ''),
                'HOST': os.environ.get('COSMOS_DB_HOST', ''),
                'PORT': os.environ.get('COSMOS_DB_PORT', '5432'),
                'OPTIONS': {
                    'sslmode': 'require'
                }
            }
        else:
            # 解析DATABASE_URL格式: postgres://username:password@hostname:port/database_name
            import re
            pattern = r'postgres://(.*?):(.*?)@(.*?):(\d+)/(.*)'
            match = re.match(pattern, db_url)
            
            if match:
                username, password, host, port, db_name = match.groups()
                return {
                    'ENGINE': 'django.db.backends.postgresql',
                    'NAME': db_name,
                    'USER': username,
                    'PASSWORD': password,
                    'HOST': host,
                    'PORT': port,
                    'OPTIONS': {
                        'sslmode': 'require'
                    }
                }
    
    # 开发和测试环境使用本地PostgreSQL
    return {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DEV_DB_NAME', 'rush_car_rental'),
        'USER': os.environ.get('DEV_DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DEV_DB_PASSWORD', 'postgres'),
        'HOST': os.environ.get('DEV_DB_HOST', 'localhost'),
        'PORT': os.environ.get('DEV_DB_PORT', '5432'),
    }