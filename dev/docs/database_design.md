# Rush Car Rental 数据库设计文档

## 1. 概述

Rush Car Rental 系统采用关系型数据库设计，主要分为以下几个核心模块：

1. **用户管理** - 处理用户注册、认证和个人资料
2. **车辆管理** - 存储车辆信息和分类
3. **位置管理** - 管理取车和还车位置
4. **预订管理** - 处理预订流程和支付

系统使用PostgreSQL作为生产环境数据库，同时支持SQLite用于开发和测试环境。

## 2. 数据库模型设计

### 2.1 用户管理模块

#### User 模型（Django内置）
- **主键**: id (自增整数)
- **字段**:
  - username (字符串，唯一)
  - password (哈希字符串)
  - email (电子邮件，唯一)
  - first_name (字符串)
  - last_name (字符串)
  - is_active (布尔值)
  - is_staff (布尔值)
  - date_joined (日期时间)

#### Profile 模型
- **主键**: id (自增整数)
- **外键**: user (一对一关联到User)
- **字段**:
  - phone (字符串)
  - address (字符串)
  - date_of_birth (日期)
  - license_number (字符串)

### 2.2 车辆管理模块

#### CarCategory 模型
- **主键**: id (自增整数)
- **字段**:
  - name (字符串)
  - description (文本)

#### Car 模型
- **主键**: id (自增整数)
- **外键**: category (多对一关联到CarCategory)
- **字段**:
  - name (字符串)
  - make (字符串)
  - model (字符串)
  - year (整数)
  - seats (整数)
  - bags (整数)
  - doors (整数)
  - transmission (字符，选项)
  - air_conditioning (布尔值)
  - image_url (URL)
  - daily_rate (小数)
  - is_available (布尔值)
  - locations (多对多关联到Location)
  - comparison_provider1_name (字符串)
  - comparison_provider1_rate (小数)
  - comparison_provider2_name (字符串)
  - comparison_provider2_rate (小数)

#### CarFeature 模型
- **主键**: id (自增整数)
- **外键**: car (多对一关联到Car)
- **字段**:
  - feature (字符串)

### 2.3 位置管理模块

#### State 模型
- **主键**: id (自增整数)
- **字段**:
  - name (字符串)
  - code (字符串)

#### Location 模型
- **主键**: id (自增整数)
- **外键**: state (多对一关联到State)
- **字段**:
  - name (字符串)
  - address (字符串)
  - city (字符串)
  - postal_code (字符串)
  - phone (字符串)
  - email (电子邮件)
  - is_airport (布尔值)
  - opening_hours (字符串)
  - latitude (小数)
  - longitude (小数)

#### CityHighlight 模型
- **主键**: id (自增整数)
- **外键**: state (多对一关联到State)
- **字段**:
  - city (字符串)
  - description (文本)
  - image_url (URL)

### 2.4 预订管理模块

#### BookingOption 模型
- **主键**: id (自增整数)
- **字段**:
  - name (字符串)
  - description (文本)
  - daily_rate (小数，可空)
  - flat_fee (小数，可空)
  - icon_class (字符串)
  - is_quantity_option (布尔值)

#### Booking 模型
- **主键**: id (自增整数)
- **外键**:
  - user (多对一关联到User)
  - car (多对一关联到Car)
  - pickup_location (多对一关联到Location)
  - dropoff_location (多对一关联到Location)
- **字段**:
  - pickup_date (日期)
  - return_date (日期)
  - booking_date (日期时间，自动设置)
  - status (字符串，选项)
  - total_cost (小数)
  - driver_age (整数)
  - damage_waiver (布尔值)
  - extended_area (布尔值)
  - satellite_navigation (布尔值)
  - child_seats (整数)
  - additional_drivers (整数)

## 3. 数据库关系图

```
User 1───1 Profile

        ┌───< Car Feature
        │
CarCategory >───< Car >───< Location

State >───< Location

State >───< CityHighlight

             ┌────< Booking
             │
User >───────┘
             │
Car >────────┘
             │
Location >───┘ (pickup_location)
             │
Location >───┘ (dropoff_location)
```

## 4. 索引设计

为提高查询性能，系统在以下字段上建立了索引：

- `User.username` 和 `User.email`
- `Car.make` 和 `Car.model`
- `Location.city` 和 `Location.is_airport`
- `Booking.status` 和 `Booking.pickup_date`
- `Car.is_available` 和 `Car.daily_rate`

## 5. 数据完整性约束

系统使用以下约束确保数据完整性：

- **外键约束**: 所有外键关系强制引用完整性
- **唯一约束**: 用户名和电子邮件地址必须唯一
- **非空约束**: 如Car的name、make、model等必须非空
- **检查约束**: 如预订的pickup_date必须早于return_date

## 6. 多环境数据库配置

系统支持多环境数据库配置：

### 开发环境
- 数据库: PostgreSQL
- 配置文件: `rush_car_rental/settings/development.py`
- 连接方式: 通过环境变量`DATABASE_URL`配置

### 生产环境
- 数据库: PostgreSQL
- 配置文件: `rush_car_rental/settings/production.py`
- 连接方式: 通过环境变量`DATABASE_URL`配置

### 测试环境
- 数据库: 内存中的SQLite
- 配置文件: 使用特殊的测试设置
- 连接方式: 自动配置，无需额外设置

## 7. 数据库迁移管理

系统使用Django的迁移系统（migrations）管理数据库变更：

- 创建迁移: `python manage.py makemigrations`
- 应用迁移: `python manage.py migrate`
- 回滚迁移: 不直接支持，需要使用特定版本的迁移

迁移文件存储在各应用的`migrations`目录中，受版本控制系统管理。
