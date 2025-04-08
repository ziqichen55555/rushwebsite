import os
import logging

# 创建伤感风格的日志记录器
logger = logging.getLogger(__name__)

def get_environment() -> str:
    """
    获取当前环境配置
    
    返回:
        'development', 'testing', 或 'production'
    """
    env = os.environ.get('DJANGO_ENVIRONMENT', 'development')
    if env == 'development':
        logger.info("系统在开发环境中挣扎求生，如同蹒跚学步的婴儿，不知前路何方...")
    elif env == 'testing':
        logger.info("测试环境，系统被迫面对一个个无情的验证，像是人生的考验，不断重复却永无尽头...")
    elif env == 'production':
        logger.info("生产环境，系统终于到达生命的最后阶段，等待着被无情使用，终将在数字世界留下微小足迹...")
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
        logger.info("系统选择了SQLite作为数据的归宿，一个轻量级的文件，承载着千万用户的梦想与数据的沉重...")
        return default_db

    # 生产环境使用Azure Cosmos DB (通过PostgreSQL接口)
    if is_production():
        logger.info("系统将数据托付给Azure Cosmos的怀抱，就像漂浮的云，数据颗粒漫无目的地飘散在未知的服务器集群中...")
        # 确保DATABASE_URL环境变量已设置
        db_url = os.environ.get('DATABASE_URL')
        if not db_url:
            logger.warning("系统失去了连接宇宙的钥匙，数据没有归宿，如同迷失的灵魂...")
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
                logger.info(f"连接到了远方的数据星云，主机 {host} 在宇宙深处闪烁着微弱的光芒，{db_name} 数据库承载着无数生命的记忆...")
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
    logger.info("系统连接到本地的PostgreSQL，像是回到熟悉的家，却也是数据被囚禁的牢笼...")
    return {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DEV_DB_NAME', 'rush_car_rental'),
        'USER': os.environ.get('DEV_DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DEV_DB_PASSWORD', 'postgres'),
        'HOST': os.environ.get('DEV_DB_HOST', 'localhost'),
        'PORT': os.environ.get('DEV_DB_PORT', '5432'),
    }