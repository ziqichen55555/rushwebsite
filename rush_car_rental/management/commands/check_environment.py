from django.core.management.base import BaseCommand
from django.conf import settings
import os
import sys
import django
import logging

# 创建日志记录器
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = '显示当前环境配置信息和数据库连接状态'

    def add_arguments(self, parser):
        parser.add_argument(
            '--detail',
            action='store_true',
            help='是否显示详细信息',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('===== Rush Car Rental 环境信息 ====='))
        logger.info("[ENV_CHECK] 开始环境检查")
        
        # 显示基本环境信息
        env = os.environ.get('DJANGO_ENVIRONMENT', '未设置')
        self.stdout.write(f'当前环境: {self.style.WARNING(env)}')
        logger.info("[ENV_CHECK] 当前环境: %s", env)
        
        self.stdout.write(f'Django版本: {self.style.WARNING(django.get_version())}')
        self.stdout.write(f'Python版本: {self.style.WARNING(sys.version.split()[0])}')
        logger.info("[ENV_CHECK] 系统版本信息: Django %s, Python %s", 
                   django.get_version(), sys.version.split()[0])
        
        self.stdout.write(f'DEBUG模式: {self.style.WARNING(str(settings.DEBUG))}')
        if settings.DEBUG:
            logger.info("[ENV_CHECK] DEBUG模式: 已开启")
        else:
            logger.info("[ENV_CHECK] DEBUG模式: 已关闭")
        
        # 数据库信息
        db_info = settings.DATABASES['default']
        self.stdout.write('\n数据库信息:')
        self.stdout.write(f'  引擎: {self.style.WARNING(db_info["ENGINE"])}')
        
        # 根据不同的数据库类型显示不同的信息
        if 'sqlite3' in db_info["ENGINE"]:
            self.stdout.write(f'  数据库文件: {self.style.WARNING(db_info.get("NAME", "未设置"))}')
            logger.info("[DB_CONFIG] 数据库类型: SQLite, 路径: %s", db_info.get("NAME", "未设置"))
        else:
            self.stdout.write(f'  名称: {self.style.WARNING(db_info.get("NAME", "未设置"))}')
            self.stdout.write(f'  主机: {self.style.WARNING(db_info.get("HOST", "未设置"))}')
            self.stdout.write(f'  端口: {self.style.WARNING(db_info.get("PORT", "未设置"))}')
            self.stdout.write(f'  用户: {self.style.WARNING(db_info.get("USER", "未设置"))}')
            logger.info("[DB_CONFIG] 数据库类型: PostgreSQL, 服务器: %s:%s, 数据库: %s", 
                       db_info.get("HOST", "未设置"), 
                       db_info.get("PORT", "未设置"),
                       db_info.get("NAME", "未设置"))
        
        # 尝试连接数据库
        self.stdout.write('\n数据库连接测试:')
        logger.info("[DB_CONNECT] 执行数据库连接测试")
        try:
            from django.db import connection
            logger.debug("[DB_CONNECT] 获取数据库连接并执行测试查询")
            cursor = connection.cursor()
            cursor.execute('SELECT 1')
            self.stdout.write(self.style.SUCCESS('  连接成功! ✅'))
            logger.info("[DB_CONNECT] 数据库连接测试成功")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  连接失败! ❌\n  错误: {str(e)}'))
            logger.error("[DB_CONNECT] 数据库连接测试失败: %s", str(e), exc_info=True)
        
        # 显示所有已安装的应用
        if options['detail']:
            self.stdout.write('\n已安装的应用:')
            logger.info("[APP_LIST] 列出已安装的应用")
            for app in settings.INSTALLED_APPS:
                self.stdout.write(f'  - {app}')
                logger.debug("[APP_LIST] 已安装应用: %s", app)
            
            # 显示环境变量(仅部分)
            self.stdout.write('\n关键环境变量:')
            logger.info("[ENV_VARS] 检查关键环境变量")
            for key in ['DJANGO_ENVIRONMENT', 'USE_POSTGRES', 'DATABASE_URL']:
                value = os.environ.get(key)
                if value:
                    if key.lower().find('secret') >= 0 or key.lower().find('password') >= 0:
                        value = '******(已隐藏)'
                        logger.debug("[ENV_VARS] 敏感变量 %s: 已隐藏", key)
                    else:
                        logger.debug("[ENV_VARS] 发现环境变量 %s: %s", key, value)
                    self.stdout.write(f'  {key}: {value}')
                else:
                    logger.debug("[ENV_VARS] 未设置环境变量: %s", key)
                    
            logger.info("[ENV_CHECK] 环境检查完成")