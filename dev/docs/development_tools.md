# Rush Car Rental 开发工具文档

## 1. 概述

Rush Car Rental 系统包含一系列开发和调试工具，这些工具不影响用户界面，仅用于开发、测试和系统维护。本文档详细介绍了这些工具的使用方法和功能。

## 2. 调试命令

### 2.1 环境信息命令 (`show_env`)

#### 功能
显示当前系统的环境信息，包括Python版本、Django版本、数据库配置、已安装应用等。

#### 用法
```bash
python manage.py show_env [--full]
```

#### 参数
- `--full`: 显示完整信息，包括环境变量（敏感信息会被隐藏）

#### 示例输出
```
=== 系统环境信息 (2023-04-08 10:15:30) ===
Python版本: 3.9.7 (default, Sep 16 2021, 13:09:58)
Django版本: 4.2.7
运行环境: development
调试模式: 开启
时区: UTC
语言: en-us

数据库引擎: postgresql
数据库名称: rush_car_rental
...
```

### 2.2 数据库统计命令 (`db_stats`)

#### 功能
显示数据库统计信息，包括表记录数、表结构、查询性能等。

#### 用法
```bash
python manage.py db_stats [--app APP_NAME] [--detail] [--query-stats]
```

#### 参数
- `--app`: 指定应用名称，仅显示该应用的数据库统计
- `--detail`: 显示详细信息，包括表结构
- `--query-stats`: 显示查询性能统计（仅在DEBUG=True时有效）

#### 示例输出
```
=== 数据库信息 ===
引擎: postgresql
名称: rush_car_rental
用户: postgres
主机: localhost

=== 表统计信息 ===
accounts.Profile (accounts_profile):
  - 记录数: 25
  - 查询时间: 0.0050秒

cars.Car (cars_car):
  - 记录数: 42
  - 查询时间: 0.0032秒
...
```

## 3. Stripe 测试工具

### 3.1 支付流程测试 (`test_stripe.py`)

#### 功能
测试Stripe支付集成功能，支持两种支付流程：
1. 标准支付流程
2. Stripe托管结账页面

#### 用法
```bash
python dev/test_stripe.py
```

#### 测试流程
1. 创建测试用户和预订
2. 模拟支付处理
3. 验证预订状态变更
4. 输出测试结果

#### 示例输出
```
==================================================
🚗 Rush Car Rental - Stripe集成测试
==================================================

=== 测试支付流程 ===
✅ 登录成功: test_user_a1b2c3d4
✅ 创建预订成功: ID 42, 总金额 350.00
✅ 访问支付页面成功
✅ 处理支付请求成功
✅ 支付成功回调处理成功
✅ 预订状态已更新为 confirmed

🎉 支付流程测试成功!
...
```

## 4. 输出格式化

所有调试命令均支持以下输出格式化选项：

### 4.1 文本格式 (默认)
```bash
python manage.py show_env
```

### 4.2 JSON格式
```bash
python manage.py show_env --format=json
```

### 4.3 输出到文件
```bash
python manage.py show_env --output=env_info.txt
```

## 5. 注意事项

1. 调试命令仅应在开发和测试环境中使用，不建议在生产环境使用
2. 某些命令可能会产生大量输出，请谨慎使用
3. 显示环境变量时，敏感信息（包含"secret"、"password"、"key"或"token"关键字）会被自动隐藏
4. 数据库统计命令可能会对数据库性能产生影响，特别是在数据量大的情况下

## 6. 扩展开发工具

开发人员可以通过以下步骤扩展开发工具：

1. 在 `dev/management/commands/` 目录下创建新的命令文件
2. 继承 `DebugBaseCommand` 基类以获取通用功能
3. 实现 `handle` 方法处理命令逻辑
4. 注册命令到 Django 管理命令系统
