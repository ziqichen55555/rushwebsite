# Rush Car Rental - 项目安装与设置指南

## 项目概述

Rush Car Rental 是一个现代化的汽车租赁平台，提供全面的车辆租赁体验，集成了先进的支付功能和以用户为中心的设计。该系统使用 Django 5.x 作为后端框架，Bootstrap 5.x 作为前端框架，并集成了 Stripe 支付网关。

### 主要功能
- 用户认证（注册、登录、登出）
- 车辆搜索和筛选
- 预订管理
- 驾驶员信息管理
- 支付处理（使用 Stripe）
- 价格比较
- 多环境支持（开发、测试、生产）

## 安装要求

### 系统要求
- Python 3.11+
- PostgreSQL 数据库（用于生产环境）
- SQLite（用于开发/测试环境）
- Node.js 和 npm（用于前端资源）

### 依赖项
- Django 5.x
- dj-database-url
- django-crispy-forms
- django-redis
- django-storages
- django-widget-tweaks
- pillow
- psycopg2-binary
- python-dotenv
- stripe
- @stripe/react-stripe-js (前端)
- @stripe/stripe-js (前端)

## 安装步骤

### 1. 克隆项目

```bash
git clone https://github.com/yourusername/rush-car-rental.git
cd rush-car-rental
```

### 2. 创建虚拟环境

```bash
python -m venv venv
source venv/bin/activate  # 在 Windows 上使用: venv\Scripts\activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
npm install  # 安装前端依赖
```

### 4. 环境配置

创建 `.env` 文件并配置环境变量：

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置以下环境变量：

```
# 数据库配置
DATABASE_URL=postgres://username:password@localhost:5432/rush_car_rental

# Stripe 配置
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
VITE_STRIPE_PUBLIC_KEY=pk_test_your_stripe_public_key

# Django 配置
SECRET_KEY=your_django_secret_key
DEBUG=True
```

### 5. 数据库设置

#### 开发环境 (SQLite)

无需额外设置，系统将使用项目根目录下的 `db.sqlite3` 文件。

#### 生产环境 (PostgreSQL)

确保在 `.env` 文件中正确配置了 `DATABASE_URL`，然后运行：

```bash
python manage.py migrate
```

### 6. 静态文件

收集静态文件：

```bash
python manage.py collectstatic
```

### 7. 创建超级用户

```bash
python manage.py createsuperuser
```

### 8. 加载初始数据

系统提供了初始数据加载脚本，可以加载汽车类别、地点和演示车辆：

```bash
python setup_data.py
```

## 运行项目

### 开发环境

```bash
python manage.py runserver
```

访问 http://localhost:8000 即可看到网站。

### 生产环境

在生产环境中，可以使用 Gunicorn 作为 WSGI 服务器：

```bash
gunicorn rush_car_rental.wsgi:application
```

推荐使用 Nginx 作为反向代理服务器。

## 项目结构

```
rush_car_rental/
├── accounts/               # 用户账户相关功能
├── bookings/               # 预订管理
├── cars/                   # 汽车管理
├── dev/                    # 开发文档
├── locations/              # 地点管理
├── pages/                  # 静态页面
├── rush_car_rental/        # 项目主配置
├── static/                 # 静态文件
├── templates/              # HTML 模板
├── manage.py               # Django 管理脚本
├── setup_data.py           # 初始数据加载脚本
└── requirements.txt        # Python 依赖项
```

## 环境切换

项目支持多种运行环境：

1. **开发环境**：默认环境，使用 SQLite 数据库
2. **测试环境**：用于测试，使用临时数据库
3. **生产环境**：用于部署，使用 PostgreSQL 数据库

通过设置环境变量 `RUSH_ENVIRONMENT` 来切换环境：

```bash
# 开发环境
export RUSH_ENVIRONMENT=development

# 测试环境
export RUSH_ENVIRONMENT=testing

# 生产环境
export RUSH_ENVIRONMENT=production
```

## Stripe 支付集成

项目集成了 Stripe 支付功能，需要进行以下配置：

1. 创建 Stripe 账户并获取 API 密钥
2. 在 `.env` 文件中配置以下变量：
   - `STRIPE_SECRET_KEY` - Stripe 私钥
   - `VITE_STRIPE_PUBLIC_KEY` - Stripe 公钥

### 测试支付

在开发环境中，如果没有配置有效的 Stripe 密钥，系统将自动切换到模拟支付模式。这种模式可以测试支付流程，但不会发送实际的支付请求。

### 生产环境支付

在生产环境中，确保配置了正确的 Stripe 密钥。系统将使用 Stripe 托管的结账页面处理实际支付。

## 驾驶员信息管理

系统实现了驾驶员信息管理功能，允许用户：

1. 在个人资料中添加多个驾驶员信息
2. 在预订过程中重用已保存的驾驶员信息
3. 设置并管理主驾驶员

## 多语言支持

系统使用 Django 的国际化功能提供多语言支持：

```bash
# 创建新的翻译文件
python manage.py makemessages -l zh_CN

# 编译翻译文件
python manage.py compilemessages
```

## 故障排除

### 数据库连接问题

如果遇到数据库连接问题，请检查：

1. `.env` 文件中的数据库配置是否正确
2. PostgreSQL 服务是否正在运行
3. 数据库用户权限是否配置正确

可以使用提供的测试脚本验证数据库配置：

```bash
python test_db_config.py
```

### Stripe 支付问题

如果 Stripe 支付不工作，请检查：

1. Stripe API 密钥是否正确
2. 网络连接是否正常
3. 查看日志文件中的具体错误信息

### 模板渲染错误

如果遇到模板渲染错误，特别是与模板块标签相关的错误，请确保所有的 `{% block %}` 标签都有对应的 `{% endblock %}` 标签。

## 日志记录

系统使用结构化日志记录，日志文件存储在 `logs/` 目录下。

在开发环境中，可以通过控制台查看详细的日志信息。

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 发起 Pull Request

### 代码风格

项目遵循 PEP 8 风格指南。提交代码前，请运行 linter：

```bash
flake8
```

## 许可证

[待定] - 请指定项目的许可证

## 联系方式

如有问题，请联系项目维护者：[your-email@example.com]