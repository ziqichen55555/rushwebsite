# Rush Car Rental 环境配置与Azure Cosmos DB集成

## 目录

1. [环境区分设计](#环境区分设计)
2. [Azure Cosmos DB集成](#azure-cosmos-db集成)
3. [数据库配置实现](#数据库配置实现)
4. [数据迁移策略](#数据迁移策略)
5. [环境部署指南](#环境部署指南)

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
   - 使用Azure Cosmos DB (PostgreSQL接口)
   - 通过`DATABASE_URL`或单独的连接参数配置

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

1. 在Azure Portal创建Cosmos DB账户（PostgreSQL接口）
2. 配置生产环境变量：
   ```
   DJANGO_ENVIRONMENT=production
   SECRET_KEY=<安全的随机密钥>
   DATABASE_URL=<Cosmos DB连接URL>
   SITE_DOMAIN=yourdomain.com
   ```
3. 部署代码到Azure App Service
4. 运行迁移：`python manage.py migrate`
5. 收集静态文件：`python manage.py collectstatic`
6. 重启应用服务
