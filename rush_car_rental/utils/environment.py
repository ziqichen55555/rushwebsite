import os
import logging

# 创建日志记录器
logger = logging.getLogger(__name__)

def get_environment() -> str:
    """
    获取当前环境配置
    
    返回:
        'development', 'testing', 或 'production'
    """
    env = os.environ.get('DJANGO_ENVIRONMENT', 'development')
    if env == 'development':
        logger.info("[ENV] 当前运行环境: development")
    elif env == 'testing':
        logger.info("[ENV] 当前运行环境: testing")
    elif env == 'production':
        logger.info("[ENV] 当前运行环境: production")
    else:
        logger.warning("[ENV] 未识别的环境类型: %s, 将使用默认环境", env)
    return env

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
    根据环境决定:
    - 开发环境: 使用SQLite (除非USE_POSTGRES=True)
    - 测试环境: 使用SQLite
    - 生产环境: 始终使用PostgreSQL
    """
    # 生产环境始终使用PostgreSQL
    if is_production():
        return True
    
    # 测试环境使用SQLite
    if is_testing():
        logger.info("[DB_CONFIG] 测试环境使用SQLite数据库")
        return False
    
    # 开发环境可以通过环境变量控制
    use_postgres = os.environ.get('USE_POSTGRES', 'false').lower()
    result = use_postgres in ('true', 'yes', '1')
    if result:
        logger.info("[DB_CONFIG] 开发环境根据配置使用PostgreSQL数据库")
    else:
        logger.info("[DB_CONFIG] 开发环境根据配置使用SQLite数据库")
    return result

def get_database_config():
    """
    根据当前环境返回数据库配置:
    - 开发环境: 使用SQLite (除非USE_POSTGRES=True)
    - 测试环境: 使用SQLite
    - 生产环境: 使用Replit提供的PostgreSQL (通过DATABASE_URL)
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
        logger.info("[DB_CONFIG] 使用SQLite数据库: %s", str(BASE_DIR / 'db.sqlite3'))
        return default_db

    # 生产环境使用Replit PostgreSQL
    if is_production():
        logger.info("[DB_CONFIG] 生产环境使用PostgreSQL数据库")
        # 优先使用DATABASE_URL环境变量
        db_url = os.environ.get('DATABASE_URL')
        
        if db_url:
            # 解析DATABASE_URL格式: postgres://username:password@hostname:port/database_name
            import re
            pattern = r'postgres://(.*?):(.*?)@(.*?):(\d+)/(.*)'
            match = re.match(pattern, db_url)
            
            if match:
                username, password, host, port, db_name = match.groups()
                logger.info("[DB_CONFIG] 通过DATABASE_URL配置PostgreSQL: 主机=%s, 端口=%s, 数据库=%s", 
                           host, port, db_name)
                return {
                    'ENGINE': 'django.db.backends.postgresql',
                    'NAME': db_name,
                    'USER': username,
                    'PASSWORD': password,
                    'HOST': host,
                    'PORT': port,
                }
        
        # 如果没有DATABASE_URL，尝试使用PGXXX环境变量
        if all([os.environ.get(k) for k in ['PGDATABASE', 'PGUSER', 'PGPASSWORD', 'PGHOST', 'PGPORT']]):
            logger.info("[DB_CONFIG] 通过PG环境变量配置PostgreSQL: 主机=%s, 端口=%s, 数据库=%s", 
                       os.environ.get('PGHOST'), os.environ.get('PGPORT'), 
                       os.environ.get('PGDATABASE'))
            return {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': os.environ.get('PGDATABASE'),
                'USER': os.environ.get('PGUSER'),
                'PASSWORD': os.environ.get('PGPASSWORD'),
                'HOST': os.environ.get('PGHOST'),
                'PORT': os.environ.get('PGPORT'),
            }
        
        # 如果以上都没有，记录警告并使用SQLite
        logger.warning("[DB_CONFIG] 生产环境未找到PostgreSQL配置，将回退使用SQLite")
        return default_db
    
    # 开发环境使用本地PostgreSQL
    host = os.environ.get('DEV_DB_HOST', 'localhost')
    db_name = os.environ.get('DEV_DB_NAME', 'rush_car_rental')
    logger.info("[DB_CONFIG] 开发环境使用本地PostgreSQL: 主机=%s, 数据库=%s", host, db_name)
    return {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DEV_DB_NAME', 'rush_car_rental'),
        'USER': os.environ.get('DEV_DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DEV_DB_PASSWORD', 'postgres'),
        'HOST': os.environ.get('DEV_DB_HOST', 'localhost'),
        'PORT': os.environ.get('DEV_DB_PORT', '5432'),
    }