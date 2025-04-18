# Rush Car Rental 数据库设计与管理

## 数据库选型

### 生产环境：PostgreSQL

在生产环境中，Rush Car Rental 选择 PostgreSQL 作为首选数据库，原因如下：

1. **可靠性与稳定性**：PostgreSQL 以其高度可靠和稳定性著称，适合处理大量并发事务。
2. **扩展性**：随着业务增长，PostgreSQL 可以很好地扩展以处理增加的负载。
3. **高级功能**：支持复杂查询、JSON 数据类型、全文搜索和地理位置数据处理等高级功能。
4. **ACID 合规性**：完全符合 ACID（原子性、一致性、隔离性和持久性）原则，确保数据完整性。
5. **与 Django ORM 兼容**：Django 对 PostgreSQL 提供了出色的支持，包括特定的字段类型和查询优化。

### 开发与测试环境：SQLite / PostgreSQL

- **开发环境**：默认使用 SQLite 以简化设置，但可以通过设置 `USE_POSTGRES=1` 环境变量切换到 PostgreSQL。
- **测试环境**：使用 SQLite 进行单元测试和集成测试，以提高测试速度。

## 数据库连接配置

数据库连接配置由 `rush_car_rental/utils/environment.py` 中的工具函数管理，可以根据当前环境自动选择适当的数据库：

```python
def get_database_config():
    """
    根据当前环境返回数据库配置:
    - 开发环境: 使用SQLite (除非USE_POSTGRES=True)
    - 测试环境: 使用SQLite
    - 生产环境: 使用Replit提供的PostgreSQL (通过DATABASE_URL)
    """
    env = get_environment()
    
    # 生产环境始终使用PostgreSQL
    if is_production():
        # 使用dj_database_url解析数据库URL
        import dj_database_url
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            raise ValueError('Production environment requires DATABASE_URL to be set')
        
        return dj_database_url.parse(database_url)
    
    # 开发环境可以选择使用PostgreSQL
    if is_development() and should_use_postgres():
        # 使用环境变量中的PostgreSQL连接参数
        return {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('PGDATABASE'),
            'USER': os.environ.get('PGUSER'),
            'PASSWORD': os.environ.get('PGPASSWORD'),
            'HOST': os.environ.get('PGHOST'),
            'PORT': os.environ.get('PGPORT'),
        }
    
    # 默认使用SQLite
    return {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
```

## 数据迁移策略

### 迁移方法

Rush Car Rental 使用 Django 内置的迁移工具进行数据库模式变更管理：

1. **创建迁移**：当模型发生变化时，使用 `python manage.py makemigrations` 创建迁移文件。
2. **应用迁移**：使用 `python manage.py migrate` 将迁移应用到数据库。
3. **迁移回滚**：如果需要回滚迁移，使用 `python manage.py migrate <app_name> <previous_migration>`。

### 迁移最佳实践

1. **频繁小步迁移**：优先创建小型、聚焦的迁移，而不是大型复杂的迁移。
2. **测试迁移**：在应用到生产前，在开发和测试环境中测试迁移。
3. **数据迁移与模式迁移分离**：将数据迁移与模式迁移分开，以减少风险。
4. **备份**：在执行重要迁移前备份数据库。
5. **向后兼容性**：设计迁移时考虑向后兼容性，避免中断服务。

### 环境特定的迁移考虑

- **开发环境**：可以频繁重置和重新迁移数据库，使用测试数据填充。
- **测试环境**：使用一致的测试数据集，确保迁移不破坏测试。
- **生产环境**：谨慎规划迁移时间，最好在低峰时段执行，并确保有回滚计划。

## 数据库维护与性能优化

### 日常维护

1. **索引优化**：定期分析查询性能，添加或修改索引。
2. **数据备份**：设置定期数据备份计划。
3. **清理和归档**：定期清理不需要的数据或将旧数据归档。

### 性能监控与优化

1. **查询优化**：
   - 使用 Django Debug Toolbar 分析查询性能
   - 优化 N+1 查询问题
   - 使用 `select_related` 和 `prefetch_related` 减少查询次数

2. **数据库配置优化**：
   - 调整连接池大小
   - 优化内存分配
   - 配置适当的超时和重试策略

3. **应用层优化**：
   - 实现合适的缓存策略
   - 分页处理大结果集
   - 使用异步任务处理耗时操作

## 数据安全

1. **访问控制**：限制对数据库的直接访问，通过应用层API控制数据操作。
2. **敏感数据加密**：对敏感信息（如信用卡信息）进行加密存储。
3. **审计日志**：记录关键数据操作的审计日志，以便追踪问题。
4. **合规性**：确保数据存储和处理符合相关法规要求（如GDPR）。