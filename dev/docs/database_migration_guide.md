# Rush Car Rental 数据库迁移指南

## 1. 概述

本指南详细说明了Rush Car Rental系统数据库迁移的流程和最佳实践。Django的迁移系统允许我们以受控方式更改数据库结构，同时保持数据完整性。

## 2. 基本迁移命令

### 2.1 创建迁移

当修改了模型（models.py）后，需要创建迁移文件：

```bash
python manage.py makemigrations
```

为特定应用创建迁移：

```bash
python manage.py makemigrations app_name
```

### 2.2 应用迁移

将迁移应用到数据库：

```bash
python manage.py migrate
```

只应用特定应用的迁移：

```bash
python manage.py migrate app_name
```

应用到特定迁移：

```bash
python manage.py migrate app_name 0003_migration_name
```

### 2.3 查看迁移状态

检查迁移状态：

```bash
python manage.py showmigrations
```

查看特定迁移的SQL：

```bash
python manage.py sqlmigrate app_name 0003_migration_name
```

## 3. 高级迁移操作

### 3.1 手动创建迁移

有时自动创建的迁移无法满足需求，可以创建空迁移并手动编写：

```bash
python manage.py makemigrations app_name --empty
```

然后编辑生成的迁移文件，添加自定义操作。

### 3.2 数据迁移

数据迁移用于在模型改变时转换数据：

```python
# 0004_data_migration.py
from django.db import migrations

def update_car_names(apps, schema_editor):
    # 获取历史模型
    Car = apps.get_model('cars', 'Car')
    
    # 更新数据
    for car in Car.objects.all():
        car.name = f"{car.make} {car.model} ({car.year})"
        car.save()

def reverse_car_names(apps, schema_editor):
    # 回滚操作（可选）
    pass

class Migration(migrations.Migration):
    dependencies = [
        ('cars', '0003_previous_migration'),
    ]
    
    operations = [
        migrations.RunPython(update_car_names, reverse_car_names),
    ]
```

### 3.3 迁移依赖管理

当迁移涉及多个应用时，需要管理依赖关系：

```python
class Migration(migrations.Migration):
    dependencies = [
        ('cars', '0002_car_locations'),
        ('locations', '0001_initial'),
    ]
    
    operations = [
        # ...
    ]
```

## 4. 环境特定迁移考虑

### 4.1 开发环境

- 频繁创建和应用迁移
- 可以使用`python manage.py migrate --fake`跳过已应用但记录丢失的迁移
- 开发结束后整合多个迁移：`python manage.py squashmigrations app_name 0001 0005`

### 4.2 生产环境

- 谨慎应用迁移，确保先在测试环境验证
- 在维护窗口执行迁移
- 总是先备份数据库
- 使用事务确保迁移可以回滚
- 考虑使用`--plan`预览将要执行的迁移：`python manage.py migrate --plan`

## 5. 处理迁移冲突

### 5.1 合并迁移

当多个开发者并行工作导致冲突时，可以合并迁移：

```bash
python manage.py makemigrations --merge
```

### 5.2 手动解决冲突

有时自动合并无法解决问题，需要：

1. 分析冲突文件
2. 手动编辑依赖关系
3. 确保操作顺序正确

## 6. 迁移最佳实践

### 6.1 迁移命名

使用有意义的名称创建迁移：

```bash
python manage.py makemigrations app_name --name add_status_field_to_booking
```

### 6.2 拆分迁移

复杂变更应拆分为多个小迁移：

1. 添加字段（可为空）
2. 数据迁移填充数据
3. 修改字段为必填

### 6.3 测试迁移

为迁移创建测试，确保数据一致性：

```python
from django.test import TestCase
from django.db.migrations.executor import MigrationExecutor
from django.db import connection

class MigrationTest(TestCase):
    @property
    def app(self):
        return 'cars'
        
    @property
    def migrate_from(self):
        return [('cars', '0002_previous_migration')]
        
    @property
    def migrate_to(self):
        return [('cars', '0003_current_migration')]
        
    def test_migration(self):
        # 设置旧版本
        executor = MigrationExecutor(connection)
        executor.migrate(self.migrate_from)
        
        # 创建测试数据
        old_apps = executor.loader.project_state(self.migrate_from).apps
        Car = old_apps.get_model(self.app, 'Car')
        car = Car.objects.create(make='Test', model='Car', year=2023)
        
        # 运行迁移
        executor.migrate(self.migrate_to)
        
        # 测试迁移结果
        new_apps = executor.loader.project_state(self.migrate_to).apps
        Car = new_apps.get_model(self.app, 'Car')
        car = Car.objects.get(id=car.id)
        self.assertEqual(car.name, 'Test Car (2023)')
```

## 7. 数据库特定注意事项

### 7.1 PostgreSQL特性

利用PostgreSQL特有功能：

```python
from django.contrib.postgres.operations import CreateExtension

class Migration(migrations.Migration):
    operations = [
        CreateExtension('postgis'),
        # ...
    ]
```

### 7.2 性能考虑

- 大表添加字段时使用`migrations.SeparateDatabaseAndState`减少锁定时间
- 索引创建使用`concurrently=True`选项（PostgreSQL）
- 批量更新数据时使用批处理避免内存问题

## 8. 故障排除

### 8.1 常见问题

- **迁移不应用**: 检查依赖关系和顺序
- **迁移导致数据丢失**: 确保使用数据迁移转换数据
- **无法回滚**: 确保提供了`reverse_code`

### 8.2 恢复策略

1. 从备份恢复
2. 使用`--fake`调整迁移状态
3. 创建新迁移修复问题

## 9. 迁移管理工作流程

1. 开发阶段：频繁创建迁移，验证更改
2. 合并阶段：整合和测试迁移
3. 部署准备：创建部署计划，估计停机时间
4. 生产部署：执行迁移，监控性能
5. 验证：确认数据和功能完整性

遵循这些指南可以确保Rush Car Rental系统的数据库迁移顺利执行，同时维护数据完整性和系统可用性。
