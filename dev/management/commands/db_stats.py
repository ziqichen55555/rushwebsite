"""
显示数据库统计信息命令
"""
from collections import defaultdict
import time
from django.core.management.base import BaseCommand
from django.db import connection
from django.apps import apps
from django.db.models import Count


class Command(BaseCommand):
    help = '显示数据库统计信息，包括表记录数、表大小等'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--app', 
            help='指定应用名称，仅显示该应用的数据库统计'
        )
        parser.add_argument(
            '--detail',
            action='store_true',
            help='显示详细信息，包括表结构'
        )
        parser.add_argument(
            '--query-stats',
            action='store_true',
            help='显示查询性能统计（仅在DEBUG=True时有效）'
        )
    
    def handle(self, *args, **options):
        app_name = options.get('app')
        show_detail = options.get('detail', False)
        show_query_stats = options.get('query_stats', False)
        
        # 获取所有模型
        all_models = []
        for app_config in apps.get_app_configs():
            if app_name and app_config.name != app_name and app_config.label != app_name:
                continue
                
            for model in app_config.get_models():
                all_models.append((app_config.label, model))
        
        if not all_models:
            if app_name:
                self.stdout.write(self.style.ERROR(f"没有找到应用: {app_name}"))
            else:
                self.stdout.write(self.style.ERROR("没有找到任何应用"))
            return
        
        # 显示数据库信息
        db_info = self.get_db_info()
        self.stdout.write(self.style.SUCCESS("=== 数据库信息 ==="))
        for key, value in db_info.items():
            self.stdout.write(f"{key}: {value}")
        
        # 显示表统计
        self.stdout.write(self.style.SUCCESS("\n=== 表统计信息 ==="))
        
        total_records = 0
        app_stats = defaultdict(int)
        
        # 表数据统计
        for app_label, model in sorted(all_models, key=lambda x: (x[0], x[1].__name__)):
            try:
                # 获取记录数
                start_time = time.time()
                count = model.objects.count()
                query_time = time.time() - start_time
                
                # 累计总记录数和应用统计
                total_records += count
                app_stats[app_label] += count
                
                # 显示表信息
                table_name = model._meta.db_table
                self.stdout.write(f"{app_label}.{model.__name__} ({table_name}):")
                self.stdout.write(f"  - 记录数: {count}")
                self.stdout.write(f"  - 查询时间: {query_time:.4f}秒")
                
                # 详细信息
                if show_detail:
                    self.show_table_detail(model)
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  错误: {str(e)}"))
        
        # 显示应用统计
        self.stdout.write(self.style.SUCCESS("\n=== 应用统计 ==="))
        for app_label, count in sorted(app_stats.items()):
            self.stdout.write(f"{app_label}: {count} 条记录")
        
        self.stdout.write(self.style.SUCCESS(f"\n总记录数: {total_records}"))
        
        # 查询统计
        if show_query_stats:
            self.show_query_stats()
    
    def get_db_info(self):
        """获取数据库基本信息"""
        from django.conf import settings
        
        db_settings = settings.DATABASES['default']
        db_info = {
            "引擎": db_settings['ENGINE'].split('.')[-1],
            "名称": db_settings.get('NAME', 'unknown'),
            "用户": db_settings.get('USER', 'unknown'),
            "主机": db_settings.get('HOST', 'unknown'),
            "端口": db_settings.get('PORT', 'unknown'),
        }
        
        # 对于SQLite，显示文件路径
        if db_info["引擎"] == "sqlite3" and db_info["名称"] != ':memory:':
            import os
            db_info["文件路径"] = os.path.abspath(db_info["名称"])
            db_info["文件大小"] = f"{os.path.getsize(db_info['名称']) / 1024:.2f} KB"
        
        # 尝试获取数据库版本
        try:
            with connection.cursor() as cursor:
                if db_info["引擎"] == "postgresql":
                    cursor.execute("SELECT version();")
                    db_info["PostgreSQL版本"] = cursor.fetchone()[0]
                elif db_info["引擎"] == "mysql":
                    cursor.execute("SELECT version();")
                    db_info["MySQL版本"] = cursor.fetchone()[0]
                elif db_info["引擎"] == "sqlite3":
                    cursor.execute("SELECT sqlite_version();")
                    db_info["SQLite版本"] = cursor.fetchone()[0]
        except:
            pass
            
        return db_info
    
    def show_table_detail(self, model):
        """显示表详细信息"""
        # 显示字段信息
        self.stdout.write("  - 字段:")
        for field in model._meta.fields:
            self.stdout.write(f"    * {field.name}: {field.get_internal_type()}")
            
        # 显示索引信息
        self.stdout.write("  - 索引:")
        for index in model._meta.indexes:
            self.stdout.write(f"    * {index.name}: {', '.join(index.fields)}")
        
        # 主键
        pk = model._meta.pk
        self.stdout.write(f"  - 主键: {pk.name} ({pk.get_internal_type()})")
        
        # 唯一约束
        if model._meta.unique_together:
            self.stdout.write("  - 唯一约束:")
            for constraint in model._meta.unique_together:
                self.stdout.write(f"    * {', '.join(constraint)}")
    
    def show_query_stats(self):
        """显示查询统计信息"""
        from django.conf import settings
        
        if not settings.DEBUG:
            self.stdout.write(self.style.WARNING("\n查询统计仅在DEBUG=True时可用"))
            return
        
        # 执行一些查询以收集统计信息
        from django.db import connection
        connection.queries_log.clear()  # 清除之前的查询记录
        
        # 获取所有应用的模型数据，执行一些典型查询
        for app_config in apps.get_app_configs():
            for model in app_config.get_models():
                try:
                    # 简单计数查询
                    model.objects.count()
                    
                    # 获取前5条记录
                    list(model.objects.all()[:5])
                    
                    # 如果有created_at或类似时间字段，尝试排序
                    time_fields = [f.name for f in model._meta.fields 
                                if f.get_internal_type() in ('DateTimeField', 'DateField', 'TimeField')]
                    if time_fields:
                        list(model.objects.order_by(time_fields[0])[:5])
                except:
                    pass
        
        # 显示查询统计
        queries = connection.queries
        
        if not queries:
            self.stdout.write(self.style.WARNING("\n没有收集到查询信息"))
            return
            
        self.stdout.write(self.style.SUCCESS(f"\n=== 查询统计 (共 {len(queries)} 个查询) ==="))
        
        # 按查询时间排序
        sorted_queries = sorted(queries, key=lambda q: float(q.get('time', 0)), reverse=True)
        
        # 显示最慢的5个查询
        self.stdout.write(self.style.SUCCESS("\n最慢的5个查询:"))
        for i, query in enumerate(sorted_queries[:5], 1):
            self.stdout.write(f"{i}. 耗时: {float(query.get('time', 0)):.4f}秒")
            self.stdout.write(f"   SQL: {query.get('sql', '')}")
            self.stdout.write("")
        
        # 查询类型统计
        query_types = defaultdict(int)
        for query in queries:
            sql = query.get('sql', '').strip().upper()
            if sql.startswith('SELECT'):
                query_types['SELECT'] += 1
            elif sql.startswith('INSERT'):
                query_types['INSERT'] += 1
            elif sql.startswith('UPDATE'):
                query_types['UPDATE'] += 1
            elif sql.startswith('DELETE'):
                query_types['DELETE'] += 1
            else:
                query_types['OTHER'] += 1
        
        self.stdout.write(self.style.SUCCESS("\n查询类型统计:"))
        for query_type, count in query_types.items():
            self.stdout.write(f"{query_type}: {count} 条查询")