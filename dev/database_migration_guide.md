# Rush Car Rental 数据库迁移实施指南

## 概述

本文档提供了 Rush Car Rental 系统数据库迁移的详细指南，包括从开发到生产环境的迁移流程、工具使用方法、常见问题解决方案，以及最佳实践。

## 数据库迁移工具

Rush Car Rental 系统使用 Django 的内置迁移框架进行数据库架构管理。这些工具提供了一种声明式的方法来更改数据库模式，并跟踪这些更改。

### 核心命令

1. **创建迁移**
   ```bash
   python manage.py makemigrations [app_name]
   ```
   根据模型的更改生成新的迁移文件。可以指定特定应用程序，也可以为所有应用程序生成迁移。

2. **应用迁移**
   ```bash
   python manage.py migrate [app_name] [migration_name]
   ```
   将尚未应用的迁移应用到数据库。可以指定特定应用程序和迁移。

3. **查看迁移状态**
   ```bash
   python manage.py showmigrations [app_name]
   ```
   显示所有迁移及其状态（已应用或未应用）。

4. **生成迁移SQL**
   ```bash
   python manage.py sqlmigrate app_name migration_name
   ```
   显示迁移将执行的SQL语句，而不实际执行它们。

5. **迁移回滚**
   ```bash
   python manage.py migrate app_name migration_name
   ```
   将特定应用程序回滚到指定的迁移。如果要回滚到初始状态，使用 `zero`：
   ```bash
   python manage.py migrate app_name zero
   ```

## 迁移工作流程

### 开发环境迁移流程

1. **更改模型**
   在相应的 `models.py` 文件中更改或添加模型。

2. **生成迁移文件**
   ```bash
   python manage.py makemigrations
   ```

3. **检查生成的迁移文件**
   查看 `migrations` 文件夹中生成的文件，确保更改符合预期。

4. **应用迁移**
   ```bash
   python manage.py migrate
   ```

5. **测试更改**
   确保应用程序能够与新模式一起正常工作。

### 生产环境迁移流程

生产环境中的迁移需要更加谨慎，以避免数据丢失或服务中断：

1. **备份数据库**
   在执行任何迁移之前，确保已创建完整的数据库备份。
   ```bash
   pg_dump -U $PGUSER -h $PGHOST -p $PGPORT -d $PGDATABASE > backup_$(date +%Y%m%d_%H%M%S).sql
   ```

2. **在测试环境验证迁移**
   在应用到生产环境之前，确保迁移在测试环境中正常工作。

3. **计划维护窗口**
   为重大迁移计划维护窗口，最好在低流量时段。

4. **执行迁移**
   ```bash
   python manage.py migrate --plan  # 首先查看将执行的迁移
   python manage.py migrate         # 如果计划看起来正确，执行迁移
   ```

5. **验证应用程序功能**
   迁移后立即验证关键应用程序功能是否正常工作。

6. **准备回滚计划**
   在执行迁移之前，准备详细的回滚计划，以防出现问题。

## 高级迁移技术

### 数据迁移

有时需要在架构更改的同时迁移或转换数据：

1. **创建空迁移**
   ```bash
   python manage.py makemigrations --empty app_name
   ```

2. **编辑迁移文件以包含数据操作**
   ```python
   def migrate_data(apps, schema_editor):
       # 获取历史模型版本
       OldModel = apps.get_model('app_name', 'OldModel')
       NewModel = apps.get_model('app_name', 'NewModel')
       
       # 迁移数据
       for old_instance in OldModel.objects.all():
           NewModel.objects.create(
               new_field=old_instance.old_field,
               # 其他字段映射
           )

   class Migration(migrations.Migration):
       # ...
       operations = [
           # ...
           migrations.RunPython(migrate_data),
           # ...
       ]
   ```

### 处理依赖关系

复杂迁移可能涉及多个应用程序之间的依赖关系：

```python
class Migration(migrations.Migration):
    # ...
    dependencies = [
        ('app1', '0001_initial'),
        ('app2', '0002_auto_20210101_1200'),
    ]
    # ...
```

### 经典迁移场景

#### 1. 添加字段

```python
# 添加一个可空字段
migrations.AddField(
    model_name='car',
    name='color',
    field=models.CharField(max_length=50, null=True, blank=True),
),

# 添加带默认值的必填字段
migrations.AddField(
    model_name='booking',
    name='is_verified',
    field=models.BooleanField(default=False),
),
```

#### 2. 重命名字段

```python
migrations.RenameField(
    model_name='profile',
    old_name='telephone',
    new_name='phone',
),
```

#### 3. 更改字段属性

```python
migrations.AlterField(
    model_name='car',
    name='daily_rate',
    field=models.DecimalField(max_digits=10, decimal_places=2),
),
```

#### 4. 添加或删除模型

```python
# 添加新模型
migrations.CreateModel(
    name='CarReview',
    fields=[
        ('id', models.AutoField(primary_key=True)),
        ('car', models.ForeignKey('cars.Car', on_delete=models.CASCADE)),
        ('rating', models.IntegerField()),
        ('comment', models.TextField()),
    ],
),

# 删除模型
migrations.DeleteModel(
    name='ObsoleteModel',
),
```

## 数据库切换与同步

### 从SQLite迁移到PostgreSQL

在开发过程中，可能需要从SQLite切换到PostgreSQL：

1. **导出SQLite数据**
   ```bash
   python manage.py dumpdata --exclude auth.permission --exclude contenttypes > data.json
   ```

2. **配置PostgreSQL连接**
   更新`.env`文件或在环境变量中设置PostgreSQL连接参数。

3. **应用迁移到PostgreSQL**
   ```bash
   python manage.py migrate
   ```

4. **导入数据到PostgreSQL**
   ```bash
   python manage.py loaddata data.json
   ```

### 多环境同步

不同环境（开发、测试、生产）之间的数据库架构应保持同步：

1. **使用版本控制跟踪迁移文件**
   确保所有迁移文件都在版本控制中进行跟踪。

2. **在部署流程中包含迁移**
   每次部署代码时应用待处理的迁移。

3. **使用迁移依赖确保正确顺序**
   确保迁移依赖关系正确，以便在任何环境中以相同的顺序应用。

## 常见问题与解决方案

### 冲突的迁移

**症状**：两个开发人员创建了相同编号的迁移，导致合并冲突。

**解决方案**：
1. 保留一个迁移，删除另一个。
2. 调整剩余迁移的依赖关系。
3. 在本地测试迁移。

### 迁移不应用

**症状**：执行`migrate`命令，但某些迁移未应用。

**解决方案**：
1. 检查`django_migrations`表，确认哪些迁移已应用。
2. 验证迁移依赖关系是否正确。
3. 尝试明确指定应用和迁移：`python manage.py migrate app_name migration_name`。

### 数据丢失风险

**症状**：迁移涉及可能导致数据丢失的操作（例如，删除字段或表）。

**解决方案**：
1. 先进行数据备份。
2. 创建数据迁移以保存数据。
3. 分多步执行迁移：先添加新结构，迁移数据，然后删除旧结构。

### 迁移性能问题

**症状**：在大型数据库上，迁移执行时间过长或锁定表太久。

**解决方案**：
1. 在低峰时段执行迁移。
2. 将大型迁移拆分为更小的步骤。
3. 考虑使用PostgreSQL的并发索引创建功能（`CREATE INDEX CONCURRENTLY`）。
4. 对于数据迁移，考虑批处理处理大量记录。

## 迁移最佳实践总结

1. **小而频繁的迁移**：优先创建小型、聚焦的迁移，而不是大型复杂的迁移。

2. **向后兼容**：设计迁移使应用程序可以与新旧架构一起工作，实现无停机升级。

3. **测试驱动迁移**：为迁移编写测试，确保它们按预期工作。

4. **文档化迁移**：特别是对于复杂的迁移，记录迁移的目的和影响。

5. **备份是关键**：始终在执行迁移前备份数据库，特别是在生产环境中。

6. **保持迁移历史干净**：避免创建然后立即删除或替换迁移。相反，应该编辑未提交的迁移。

7. **迁移应该是幂等的**：一个好的迁移应该可以多次应用而不会改变结果。

8. **避免跳过迁移**：按顺序应用所有迁移，避免跳过迁移。

9. **监控迁移性能**：特别是对于大型数据库，确保迁移在合理的时间内完成。

10. **审查生成的SQL**：使用`sqlmigrate`命令审查将要执行的SQL，确保它符合预期。