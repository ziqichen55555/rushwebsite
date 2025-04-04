# Rush Car Rental - 现代化车辆租赁平台

Rush Car Rental是一个基于Django 4.x和Bootstrap 5.x构建的完整车辆租赁平台，提供全面的用户体验，包括车辆选择、预订和支付处理。应用程序提供详细的政策文档，并具有增强的用户界面设计。

## 📋 目录

- [技术栈](#技术栈)
- [特性](#特性)
- [项目结构](#项目结构)
- [核心组件](#核心组件)
- [数据模型](#数据模型)
- [运行本地开发环境](#运行本地开发环境)
- [部署指南](#部署指南)
- [环境变量和安全性](#环境变量和安全性)
- [管理员账户](#管理员账户)

## 🛠️ 技术栈

- **后端**: Django 4.x
- **前端**: Bootstrap 5.x, JavaScript, HTML5, CSS3
- **数据库**: PostgreSQL
- **支付处理**: Stripe API
- **认证**: Django内置认证系统

## ✨ 特性

### 用户功能
- 🔐 用户注册和认证（登录、注册、登出）
- 👤 用户个人资料和预订历史管理
- 🚗 基于多种条件的车辆搜索（位置、日期、车型等）
- 💰 透明的价格比较（与竞争对手的价格对比）
- 📅 车辆预订管理系统
- 💳 Stripe集成支付处理

### 管理功能
- 📊 全面的管理界面
- 🚙 车辆库存管理
- 📍 租赁地点管理
- 📝 预订和用户数据管理
- 💼 额外选项和定价策略配置

### 信息页面
- 📜 租赁条款与条件
- 💸 退款政策
- 📝 取车指南
- 🔄 还车指南
- ℹ️ 关于我们

## 🗂️ 项目结构

```
rush_car_rental/
├── accounts/             # 用户账户管理
├── bookings/             # 预订处理和管理
├── cars/                 # 车辆信息和管理
├── locations/            # 租赁位置管理
├── pages/                # 静态信息页面
├── rush_car_rental/      # 主项目设置
├── static/               # 静态文件（CSS, JS, 图片）
├── templates/            # HTML模板
│   ├── accounts/         # 账户相关模板
│   ├── bookings/         # 预订相关模板
│   ├── cars/             # 车辆相关模板
│   ├── locations/        # 地点相关模板
│   ├── pages/            # 信息页面模板
│   └── base.html         # 基础模板
└── manage.py             # Django管理命令
```

## 🔧 核心组件

### 1. 用户认证系统
- 基于Django的内置认证系统
- 扩展了用户个人资料，包含额外信息（电话、地址、出生日期、驾照号码）
- 自动创建用户个人资料（使用Django信号）

### 2. 车辆搜索与展示
- 高级搜索功能，支持多条件搜索
- 车辆详情页展示全面信息
- 价格比较功能，与竞争对手价格对比

### 3. 预订流程
- 多步骤预订流程
  1. 搜索可用车辆
  2. 选择车辆
  3. 添加额外选项（如损伤豁免、导航系统等）
  4. 确认预订
  5. 支付处理
  6. 预订确认

### 4. 支付处理
- 集成Stripe支付系统
- 安全处理支付信息
- 支持模拟支付功能（开发环境）

### 5. 管理界面
- 定制的Django管理界面
- 全面的数据管理功能
- 角色权限管理

## 📊 数据模型

### 主要数据模型

#### 用户模型 (User & Profile)
```python
# 标准Django用户模型 + 个人资料扩展
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True)
    address = models.CharField(max_length=255, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    license_number = models.CharField(max_length=30, blank=True)
```

#### 车辆模型 (Car & CarCategory)
```python
class Car(models.Model):
    name = models.CharField(max_length=100)
    make = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    year = models.PositiveIntegerField()
    category = models.ForeignKey(CarCategory, on_delete=models.CASCADE)
    seats = models.PositiveIntegerField()
    bags = models.PositiveIntegerField()
    doors = models.PositiveIntegerField()
    transmission = models.CharField(max_length=1, choices=TRANSMISSION_CHOICES)
    air_conditioning = models.BooleanField(default=True)
    image_url = models.URLField()
    daily_rate = models.DecimalField(max_digits=8, decimal_places=2)
    is_available = models.BooleanField(default=True)
    locations = models.ManyToManyField(Location, related_name='available_cars')
    # 价格比较字段
    comparison_provider1_name = models.CharField(max_length=50, blank=True)
    comparison_provider1_rate = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    comparison_provider2_name = models.CharField(max_length=50, blank=True)
    comparison_provider2_rate = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
```

#### 地点模型 (Location & State)
```python
class Location(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    postal_code = models.CharField(max_length=20)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    is_airport = models.BooleanField(default=False)
    opening_hours = models.CharField(max_length=255, default='Monday-Friday: 8AM-6PM, Saturday: 9AM-5PM, Sunday: Closed')
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
```

#### 预订模型 (Booking)
```python
class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    pickup_location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='pickup_bookings')
    dropoff_location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='dropoff_bookings')
    pickup_date = models.DateField()
    return_date = models.DateField()
    booking_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    driver_age = models.PositiveIntegerField()
    
    # 额外选项
    damage_waiver = models.BooleanField(default=False)
    extended_area = models.BooleanField(default=False)
    satellite_navigation = models.BooleanField(default=False)
    child_seats = models.PositiveIntegerField(default=0)
    additional_drivers = models.PositiveIntegerField(default=0)
```

#### 预订选项模型 (BookingOption)
```python
class BookingOption(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    daily_rate = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    flat_fee = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    icon_class = models.CharField(max_length=50, default="fas fa-car")
    is_quantity_option = models.BooleanField(default=False)
```

## 🚀 运行本地开发环境

### 前提条件
- Python 3.8+
- PostgreSQL

### 步骤

1. 克隆仓库并进入项目目录
2. 创建虚拟环境并激活
3. 安装依赖
4. 设置环境变量（SECRET_KEY, DATABASE_URL, STRIPE_SECRET_KEY等）
5. 运行数据库迁移
6. 创建超级用户
7. 加载初始数据
8. 启动开发服务器

## 🌐 部署指南

### 使用Replit部署

1. 确保所有测试都已通过
2. 点击Replit界面中的Deploy按钮
3. 按照提示完成部署过程

### 传统部署选项

1. 安装Gunicorn
2. 配置Nginx
3. 设置服务文件
4. 启动服务

## 🔐 环境变量和安全性

重要的环境变量:

- SECRET_KEY: Django的密钥
- DEBUG: 调试模式开关
- DATABASE_URL: 数据库连接URL
- STRIPE_SECRET_KEY: Stripe私钥
- VITE_STRIPE_PUBLIC_KEY: Stripe公钥

## 👨‍💼 管理员账户

默认管理员账户:
- 用户名: admin
- 密码: adminpassword

**注意**: 在生产环境中，请务必更改默认管理员密码。

---

© 2025 Rush Car Rental. 保留所有权利。
