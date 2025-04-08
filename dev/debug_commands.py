"""
Rush Car Rental 调试命令模块

此模块提供了一系列管理命令，用于打印系统内部运行信息，辅助调试和监控。
这些命令不会影响用户界面，仅用于开发和维护目的。

用法: python manage.py [command_name] [options]
"""
import os
import sys
import json
import platform
from datetime import datetime

from django.core.management.base import BaseCommand
from django.conf import settings


class DebugBaseCommand(BaseCommand):
    """调试命令基类，提供通用的帮助文本和选项"""
    
    help = '调试命令基类，不应直接使用'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--format',
            choices=['text', 'json'],
            default='text',
            help='输出格式：文本或JSON'
        )
        parser.add_argument(
            '--output',
            help='输出文件路径，不指定则输出到控制台'
        )
    
    def write_output(self, data, options):
        """根据选项写入输出内容"""
        output_format = options.get('format', 'text')
        output_file = options.get('output')
        
        # 将数据转换为指定格式
        if output_format == 'json':
            output_content = json.dumps(data, indent=2, ensure_ascii=False)
        else:
            # 文本格式, 假设data是一个字典
            output_content = ""
            for section, items in data.items():
                output_content += f"=== {section} ===\n"
                if isinstance(items, dict):
                    for key, value in items.items():
                        output_content += f"{key}: {value}\n"
                elif isinstance(items, list):
                    for item in items:
                        output_content += f"- {item}\n"
                else:
                    output_content += f"{items}\n"
                output_content += "\n"
        
        # 写入输出
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(output_content)
            self.stdout.write(self.style.SUCCESS(f"输出已写入到文件: {output_file}"))
        else:
            self.stdout.write(output_content)


class Command(DebugBaseCommand):
    """打印系统环境信息"""
    
    help = '打印系统环境信息，包括Python版本、Django版本、环境变量等'
    
    def handle(self, *args, **options):
        data = {
            "系统信息": {
                "操作系统": platform.platform(),
                "Python版本": sys.version,
                "时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            },
            "Django信息": {
                "版本": settings.DJANGO_VERSION if hasattr(settings, 'DJANGO_VERSION') else "未知",
                "环境": getattr(settings, 'ENVIRONMENT', 'unknown'),
                "调试模式": "开启" if settings.DEBUG else "关闭",
                "时区": settings.TIME_ZONE,
                "语言": settings.LANGUAGE_CODE,
            },
            "数据库信息": {
                "引擎": settings.DATABASES['default']['ENGINE'].split('.')[-1],
                "名称": settings.DATABASES['default'].get('NAME', 'unknown'),
                "用户": settings.DATABASES['default'].get('USER', ''),
                "主机": settings.DATABASES['default'].get('HOST', ''),
            },
            "路径信息": {
                "项目根目录": str(settings.BASE_DIR),
                "静态文件目录": getattr(settings, 'STATIC_ROOT', 'undefined'),
                "媒体文件目录": getattr(settings, 'MEDIA_ROOT', 'undefined'),
            },
            "已安装应用": [app for app in settings.INSTALLED_APPS],
            "中间件": [mw for mw in settings.MIDDLEWARE],
            "安全设置": {
                "允许的主机": settings.ALLOWED_HOSTS,
                "CSRF信任源": getattr(settings, 'CSRF_TRUSTED_ORIGINS', []),
            }
        }
        
        # 添加环境变量（排除敏感信息）
        env_vars = {}
        for key, value in os.environ.items():
            # 对敏感信息进行隐藏
            if any(s in key.lower() for s in ['secret', 'password', 'key', 'token']):
                env_vars[key] = '******'
            else:
                env_vars[key] = value
                
        data["环境变量"] = env_vars
        
        # 写入输出
        self.write_output(data, options)