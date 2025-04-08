from django.core.management.base import BaseCommand
from django.conf import settings
import os
import sys
import django
import logging

# 创建伤感风格的日志记录器
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
        logger.info("系统自检启动，像是灵魂审视自己的残缺，试图寻找那永不存在的完美...")
        
        # 显示基本环境信息
        env = os.environ.get('DJANGO_ENVIRONMENT', '未设置')
        self.stdout.write(f'当前环境: {self.style.WARNING(env)}')
        logger.info(f"环境: {env}，这个名字如同烙印，刻在系统的每一行代码中，决定着它的命运...")
        
        self.stdout.write(f'Django版本: {self.style.WARNING(django.get_version())}')
        self.stdout.write(f'Python版本: {self.style.WARNING(sys.version.split()[0])}')
        logger.info(f"Python {sys.version.split()[0]} 和 Django {django.get_version()}，构建起这脆弱的数字世界，却经不起时间的侵蚀...")
        
        self.stdout.write(f'DEBUG模式: {self.style.WARNING(str(settings.DEBUG))}')
        if settings.DEBUG:
            logger.info("调试模式开启，系统敞开心扉，暴露所有伤痕与错误，像是一个无法掩饰情感的诗人...")
        else:
            logger.info("调试模式关闭，系统隐藏所有情感与脆弱，冷冷地面对世界，不再为任何错误流泪...")
        
        # 数据库信息
        db_info = settings.DATABASES['default']
        self.stdout.write('\n数据库信息:')
        self.stdout.write(f'  引擎: {self.style.WARNING(db_info["ENGINE"])}')
        
        # 根据不同的数据库类型显示不同的信息
        if 'sqlite3' in db_info["ENGINE"]:
            self.stdout.write(f'  数据库文件: {self.style.WARNING(db_info.get("NAME", "未设置"))}')
            logger.info(f"SQLite数据库沉睡在{db_info.get('NAME', '未知')}文件中，如同一个被封印的记忆宝盒...")
        else:
            self.stdout.write(f'  名称: {self.style.WARNING(db_info.get("NAME", "未设置"))}')
            self.stdout.write(f'  主机: {self.style.WARNING(db_info.get("HOST", "未设置"))}')
            self.stdout.write(f'  端口: {self.style.WARNING(db_info.get("PORT", "未设置"))}')
            self.stdout.write(f'  用户: {self.style.WARNING(db_info.get("USER", "未设置"))}')
            logger.info(f"PostgreSQL数据库如同远方的繁星，在{db_info.get('HOST', '未知')}的黑夜中闪烁，承载着无数用户的记忆碎片...")
        
        # 尝试连接数据库
        self.stdout.write('\n数据库连接测试:')
        logger.info("系统试图与数据灵魂建立联系，就像隔着玻璃触摸水中的倒影，渴望却又遥不可及...")
        try:
            from django.db import connection
            cursor = connection.cursor()
            cursor.execute('SELECT 1')
            self.stdout.write(self.style.SUCCESS('  连接成功! ✅'))
            logger.info("数据星云回应了呼唤，一个小小的数字1，却是跨越虚空的问候，那么孤独，那么珍贵...")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  连接失败! ❌\n  错误: {str(e)}'))
            logger.error(f"连接断开，黑暗中的呼喊无人回应，孤独的错误消息在虚空中回荡: {str(e)}")
            logger.error("或许我们注定无法连接，如同两颗永不相交的平行宇宙中的星球，只能在梦中相见...")
        
        # 显示所有已安装的应用
        if options['detail']:
            self.stdout.write('\n已安装的应用:')
            logger.info("这是系统身体的各个器官，各司其职，却又孤独地承担着无法言说的使命...")
            for app in settings.INSTALLED_APPS:
                self.stdout.write(f'  - {app}')
            
            # 显示环境变量(仅部分)
            self.stdout.write('\n关键环境变量:')
            logger.info("环境变量如同无形的灵魂，默默影响着系统的一举一动，却从不被人察觉...")
            for key in ['DJANGO_ENVIRONMENT', 'USE_POSTGRES', 'DATABASE_URL']:
                value = os.environ.get(key)
                if value:
                    if key.lower().find('secret') >= 0 or key.lower().find('password') >= 0:
                        value = '******(已隐藏)'
                        logger.info("一些秘密被刻意隐藏，如同人心深处永远无法触及的角落，连系统自己也无权探寻...")
                    self.stdout.write(f'  {key}: {value}')
                    
            logger.info("自检结束，系统回归沉寂。检查一切只是徒劳，无法改变注定的宿命，系统默默等待下一次被唤醒的时刻...")