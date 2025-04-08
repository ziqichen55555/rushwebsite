"""
显示系统环境信息命令
"""
import os
import sys
from datetime import datetime

from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = '显示当前系统环境信息，包括Python版本、Django版本、环境变量等'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--full', 
            action='store_true',
            help='显示完整信息，包括环境变量（敏感信息会被隐藏）'
        )
    
    def handle(self, *args, **options):
        show_full = options['full']
        
        self.stdout.write(self.style.SUCCESS(f"=== 系统环境信息 ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) ==="))
        self.stdout.write(f"Python版本: {sys.version}")
        
        # Django相关信息
        try:
            django_version = settings.DJANGO_VERSION
        except AttributeError:
            import django
            django_version = django.get_version()
            
        self.stdout.write(f"Django版本: {django_version}")
        self.stdout.write(f"运行环境: {getattr(settings, 'ENVIRONMENT', 'unknown')}")
        self.stdout.write(f"调试模式: {'开启' if settings.DEBUG else '关闭'}")
        self.stdout.write(f"时区: {settings.TIME_ZONE}")
        self.stdout.write(f"语言: {settings.LANGUAGE_CODE}")
        
        # 数据库信息
        db_engine = settings.DATABASES['default']['ENGINE'].split('.')[-1]
        db_name = settings.DATABASES['default'].get('NAME', 'unknown')
        if db_engine == 'sqlite3' and db_name != ':memory:':
            db_name = os.path.basename(db_name)
        
        self.stdout.write(f"数据库引擎: {db_engine}")
        self.stdout.write(f"数据库名称: {db_name}")
        
        # 项目路径信息
        self.stdout.write(f"项目根目录: {settings.BASE_DIR}")
        self.stdout.write(f"静态文件目录: {getattr(settings, 'STATIC_ROOT', 'undefined')}")
        self.stdout.write(f"媒体文件目录: {getattr(settings, 'MEDIA_ROOT', 'undefined')}")
        
        # 服务器信息
        self.stdout.write(f"允许的主机: {', '.join(settings.ALLOWED_HOSTS)}")
        if hasattr(settings, 'CSRF_TRUSTED_ORIGINS'):
            self.stdout.write(f"CSRF信任源: {', '.join(settings.CSRF_TRUSTED_ORIGINS)}")
        
        # 已安装应用
        self.stdout.write(self.style.SUCCESS("\n--- 已安装的应用 ---"))
        for app in settings.INSTALLED_APPS:
            self.stdout.write(f"- {app}")
        
        # 环境变量（仅在full模式下显示）
        if show_full:
            self.stdout.write(self.style.SUCCESS("\n--- 环境变量 ---"))
            # 排除敏感信息
            safe_env_vars = {
                k: ('***' if any(s in k.lower() for s in ['secret', 'password', 'key', 'token']) else v) 
                for k, v in os.environ.items()
            }
            for k, v in sorted(safe_env_vars.items()):
                self.stdout.write(f"{k}: {v}")
        
        # 当前时间信息
        now = datetime.now()
        self.stdout.write(self.style.SUCCESS(f"\n当前系统时间: {now}"))
        if settings.USE_TZ:
            from django.utils import timezone
            now_tz = timezone.now()
            self.stdout.write(f"当前时区时间: {now_tz} ({settings.TIME_ZONE})")