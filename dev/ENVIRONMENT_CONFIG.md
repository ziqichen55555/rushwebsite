# Rush Car Rental 环境配置与数据库集成

## 目录

1. [环境区分设计](#环境区分设计)
2. [数据库配置实现](#数据库配置实现)
3. [Stripe支付集成](#stripe支付集成)
4. [Azure Cosmos DB集成](#azure-cosmos-db集成)
5. [数据迁移策略](#数据迁移策略)
6. [环境部署指南](#环境部署指南)
7. [Replit特定配置](#replit特定配置)

## 环境区分设计

### 环境类型定义

Rush Car Rental系统定义了以下环境:

1. **开发环境 (Development)**:
   - 本地开发使用
   - 使用SQLite或本地PostgreSQL
   - 调试模式开启
   - 邮件发送到控制台
   - 日志详细记录

2. **测试环境 (Testing)**:
   - 用于QA测试和集成测试
   - 使用PostgreSQL数据库
   - 调试模式关闭
   - 邮件发送到控制台
   - 日志详细记录

3. **生产环境 (Production)**:
   - 面向最终用户的生产系统
   - 使用Azure Cosmos DB和PostgreSQL接口
   - 调试模式关闭
   - 使用SMTP发送真实邮件
   - 日志仅记录警告和错误

### 环境变量管理

系统使用环境变量控制不同环境的配置：

- `DJANGO_ENVIRONMENT`: 控制环境类型，可选值: `development`, `testing`, `production`
- `SECRET_KEY`: Django密钥，生产环境必须设置
- `USE_POSTGRES`: 在开发环境是否使用PostgreSQL（默认使用SQLite）
- `DATABASE_URL`: 生产环境数据库连接字符串
- `REPLIT_DOMAINS`: Replit环境中的应用域名（自动设置）
- `REPLIT_DEV_DOMAIN`: Replit开发环境域名（自动设置）
- `STRIPE_SECRET_KEY`: Stripe API密钥（服务器端）
- `VITE_STRIPE_PUBLIC_KEY`: Stripe公钥（前端使用）

## Azure Cosmos DB集成

### 为什么选择Azure Cosmos DB

1. **全球分布**：支持多区域部署，用户可以在世界各地访问服务
2. **高可用性**：提供99.999%的高可用性SLA
3. **弹性扩展**：可以根据流量自动扩展容量
4. **与Azure生态系统集成**：与其他Azure服务无缝集成

### 数据库接口

Azure Cosmos DB提供PostgreSQL接口，可以使用标准的PostgreSQL客户端库连接。关键配置：

- 使用SSL加密连接
- 支持标准SQL语法
- 支持Django ORM

## 数据库配置实现

系统根据环境变量自动选择数据库配置：

1. **开发环境**:
   - 默认使用SQLite (文件: `db.sqlite3`)
   - 可通过设置`USE_POSTGRES=True`切换到本地PostgreSQL

2. **测试环境**:
   - 使用本地或专用测试PostgreSQL实例
   - 配置通过环境变量提供

3. **生产环境**:
   - 使用PostgreSQL数据库
   - 通过`DATABASE_URL`或单独的连接参数配置
   - 未来可扩展为使用Azure Cosmos DB (PostgreSQL接口)

## Stripe支付集成

Rush Car Rental使用Stripe处理支付，具体配置如下：

### 密钥管理

系统使用以下环境变量配置Stripe集成：

- `STRIPE_SECRET_KEY`: Stripe API密钥，用于服务器端API调用
- `VITE_STRIPE_PUBLIC_KEY`: Stripe公钥，用于前端Elements集成

### 环境特定配置

1. **开发/测试环境**:
   - 使用Stripe测试密钥（以`sk_test_`和`pk_test_`开头）
   - 支付不会实际扣款
   - 使用Stripe提供的测试卡号（如4242 4242 4242 4242）

2. **生产环境**:
   - 使用Stripe生产密钥（以`sk_live_`和`pk_live_`开头）
   - 处理实际交易
   - 实施额外的安全措施（如Webhook验证）

### 集成特性

1. **支付流程**:
   - 使用Payment Intents API处理一次性支付
   - 支持信用卡和借记卡支付
   - 全面错误处理和状态更新

2. **安全措施**:
   - 所有API密钥通过环境变量管理，不硬编码
   - 敏感信息不存储在服务器上
   - 使用Stripe Elements确保符合PCI合规要求

## 数据迁移策略

从开发环境到生产环境的数据迁移使用Django的标准迁移工具：

1. **开发环境**:
   - 使用`python manage.py makemigrations`创建迁移文件
   - 使用`python manage.py migrate`应用迁移

2. **测试环境**:
   - 使用相同的迁移文件
   - 部署前在测试环境运行`python manage.py migrate`

3. **生产环境**:
   - 部署前运行`python manage.py migrate`应用迁移
   - 需要注意避免数据丢失的操作

## 环境部署指南

### 开发环境设置

1. 克隆代码库
2. 创建`.env`文件并配置：
   ```
   DJANGO_ENVIRONMENT=development
   USE_POSTGRES=False
   ```
3. 运行迁移：`python manage.py migrate`
4. 加载初始数据：`python manage.py setup_data`
5. 运行开发服务器：`python manage.py runserver`

### 测试环境部署

1. 创建`.env`文件并配置：
   ```
   DJANGO_ENVIRONMENT=testing
   USE_POSTGRES=True
   DEV_DB_NAME=rush_car_rental
   DEV_DB_USER=username
   DEV_DB_PASSWORD=password
   DEV_DB_HOST=localhost
   DEV_DB_PORT=5432
   ```
2. 运行迁移：`python manage.py migrate`
3. 加载测试数据：`python manage.py setup_data`
4. 启动测试服务器：`python manage.py runserver 0.0.0.0:8000`

### 生产环境部署

1. 配置生产环境变量：
   ```
   DJANGO_ENVIRONMENT=production
   SECRET_KEY=<安全的随机密钥>
   DATABASE_URL=<数据库连接URL>
   STRIPE_SECRET_KEY=<Stripe生产密钥>
   VITE_STRIPE_PUBLIC_KEY=<Stripe生产公钥>
   ```
2. 部署代码到托管平台（如Azure App Service或Replit）
3. 运行迁移：`python manage.py migrate`
4. 收集静态文件：`python manage.py collectstatic`
5. 重启应用服务

## Replit特定配置

### 环境变量管理

Replit平台自动提供以下环境变量：

- `REPLIT_DEPLOYMENT`: 指示是否是部署版（非空值表示是）
- `REPLIT_DOMAINS`: 逗号分隔的可访问域名列表
- `REPLIT_DEV_DOMAIN`: 开发环境的域名

### Django配置适配

为支持Replit环境，项目进行了以下配置调整：

1. **ALLOWED_HOSTS设置**:
   ```python
   # 从环境变量获取Replit域名
   replit_domains = os.environ.get('REPLIT_DOMAINS', '')
   allowed_hosts = [domain.strip() for domain in replit_domains.split(',') if domain.strip()]
   
   # 添加本地主机
   allowed_hosts.extend(['127.0.0.1', 'localhost'])
   
   # 设置Django的ALLOWED_HOSTS
   ALLOWED_HOSTS = allowed_hosts
   ```

2. **CSRF配置**:
   ```python
   # 配置CSRF信任源
   csrf_trusted_origins = []
   for domain in allowed_hosts:
       if domain not in ['127.0.0.1', 'localhost']:
           csrf_trusted_origins.append(f'https://{domain}')
           csrf_trusted_origins.append(f'http://{domain}')
   
   CSRF_TRUSTED_ORIGINS = csrf_trusted_origins
   ```

3. **日志配置**:
   ```python
   # Replit环境日志配置
   LOGGING = {
       'version': 1,
       'disable_existing_loggers': False,
       'handlers': {
           'file': {
               'level': 'INFO',
               'class': 'logging.FileHandler',
               'filename': os.path.join(BASE_DIR, 'logs/django.log'),
           },
       },
       'loggers': {
           'django': {
               'handlers': ['file'],
               'level': 'INFO',
               'propagate': True,
           },
       },
   }
   ```

### 数据库配置

Replit环境中的数据库配置：

1. **使用环境变量**:
   ```python
   # 使用Replit提供的PostgreSQL
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': os.environ.get('PGDATABASE'),
           'USER': os.environ.get('PGUSER'),
           'PASSWORD': os.environ.get('PGPASSWORD'),
           'HOST': os.environ.get('PGHOST'),
           'PORT': os.environ.get('PGPORT'),
       }
   }
   ```

2. **连接池配置**:
   ```python
   # 针对Replit环境优化连接池
   DATABASES['default']['CONN_MAX_AGE'] = 600  # 连接保持10分钟
   DATABASES['default']['OPTIONS'] = {
       'connect_timeout': 10,
       'keepalives': 1,
       'keepalives_idle': 60,
       'keepalives_interval': 10,
       'keepalives_count': 5,
   }
   ```

### 静态文件处理

在Replit环境中的静态文件配置：

```python
# 静态文件配置
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
```

### 启动配置

Replit通过`.replit`文件配置应用启动方式：

```
run = "python manage.py runserver 0.0.0.0:5000"
```
