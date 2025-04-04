# Rush Car Rental API 设计文档

## 目录

1. [API概述](#api概述)
2. [认证机制](#认证机制)
3. [API端点](#api端点)
4. [数据格式](#数据格式)
5. [错误处理](#错误处理)
6. [API扩展方向](#api扩展方向)

## API概述

Rush Car Rental API是一套RESTful API，旨在为客户端应用提供车辆租赁服务的所有功能，包括车辆查询、预订管理和用户账户操作。

### 设计原则

1. **RESTful架构**: 遵循REST架构风格，使用标准HTTP方法
2. **JSON数据交换**: 使用JSON作为数据交换格式
3. **版本控制**: API端点包含版本信息，确保向后兼容性
4. **安全性**: 使用OAuth2和HTTPS确保通信安全
5. **简单性**: 设计简单直观的接口，减少学习成本

## 认证机制

API使用OAuth2认证流程，客户端需要先获取访问令牌才能访问受保护的资源。

### 获取访问令牌

```
POST /api/v1/auth/token
```

请求参数:
- `client_id`: 客户端ID
- `client_secret`: 客户端密钥
- `grant_type`: 授权类型（"password"、"client_credentials"等）
- `username`: 用户名（当grant_type为"password"时需要）
- `password`: 密码（当grant_type为"password"时需要）

响应:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### 刷新访问令牌

```
POST /api/v1/auth/token
```

请求参数:
- `client_id`: 客户端ID
- `client_secret`: 客户端密钥
- `grant_type`: "refresh_token"
- `refresh_token`: 之前获取的刷新令牌

## API端点

### 车辆API

#### 获取车辆列表

```
GET /api/v1/cars
```

查询参数:
- `location_id`: 位置ID（可选）
- `pickup_date`: 取车日期，格式YYYY-MM-DD（可选）
- `return_date`: 还车日期，格式YYYY-MM-DD（可选）
- `category_id`: 车辆类别ID（可选）
- `page`: 页码，默认1
- `limit`: 每页记录数，默认20

响应:
```json
{
  "count": 100,
  "next": "/api/v1/cars?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Toyota Corolla",
      "make": "Toyota",
      "model": "Corolla",
      "year": 2022,
      "category": {
        "id": 1,
        "name": "Economy"
      },
      "daily_rate": "65.00",
      "image_url": "https://example.com/images/corolla.jpg",
      "seats": 5,
      "bags": 2,
      "doors": 4,
      "transmission": "A",
      "air_conditioning": true,
      "is_available": true,
      "comparison_rates": [
        {
          "provider": "CompetitorA",
          "rate": "75.00"
        },
        {
          "provider": "CompetitorB",
          "rate": "72.50"
        }
      ]
    },
    // 更多车辆...
  ]
}
```

#### 获取车辆详情

```
GET /api/v1/cars/{car_id}
```

响应:
```json
{
  "id": 1,
  "name": "Toyota Corolla",
  "make": "Toyota",
  "model": "Corolla",
  "year": 2022,
  "category": {
    "id": 1,
    "name": "Economy",
    "description": "经济型车辆，适合城市旅行"
  },
  "daily_rate": "65.00",
  "image_url": "https://example.com/images/corolla.jpg",
  "seats": 5,
  "bags": 2,
  "doors": 4,
  "transmission": "A",
  "transmission_display": "Automatic",
  "air_conditioning": true,
  "is_available": true,
  "features": [
    "蓝牙连接",
    "倒车摄像头",
    "USB充电接口"
  ],
  "comparison_rates": [
    {
      "provider": "CompetitorA",
      "rate": "75.00"
    },
    {
      "provider": "CompetitorB",
      "rate": "72.50"
    }
  ],
  "available_locations": [
    {
      "id": 1,
      "name": "墨尔本机场",
      "address": "墨尔本机场1号航站楼"
    },
    {
      "id": 2,
      "name": "墨尔本市中心",
      "address": "富兰克林街123号"
    }
  ]
}
```

### 预订API

#### 创建预订

```
POST /api/v1/bookings
```

请求体:
```json
{
  "car_id": 1,
  "pickup_location_id": 1,
  "dropoff_location_id": 2,
  "pickup_date": "2025-05-01",
  "return_date": "2025-05-05",
  "driver_age": 25,
  "options": {
    "damage_waiver": true,
    "extended_area": false,
    "satellite_navigation": true,
    "child_seats": 1,
    "additional_drivers": 0
  }
}
```

响应:
```json
{
  "id": "b12345",
  "status": "pending",
  "total_cost": "450.00",
  "payment_intent_client_secret": "pi_1234_secret_5678",
  "car": {
    "id": 1,
    "name": "Toyota Corolla"
  },
  "pickup_location": {
    "id": 1,
    "name": "墨尔本机场"
  },
  "dropoff_location": {
    "id": 2,
    "name": "墨尔本市中心"
  },
  "pickup_date": "2025-05-01",
  "return_date": "2025-05-05",
  "duration_days": 4,
  "base_cost": "260.00",
  "options_cost": "190.00",
  "options": {
    "damage_waiver": true,
    "extended_area": false,
    "satellite_navigation": true,
    "child_seats": 1,
    "additional_drivers": 0
  }
}
```

#### 获取预订列表

```
GET /api/v1/bookings
```

查询参数:
- `status`: 预订状态（可选，例如"pending"、"confirmed"等）
- `page`: 页码，默认1
- `limit`: 每页记录数，默认20

响应:
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "b12345",
      "car": {
        "id": 1,
        "name": "Toyota Corolla",
        "image_url": "https://example.com/images/corolla.jpg"
      },
      "pickup_location": {
        "id": 1,
        "name": "墨尔本机场"
      },
      "dropoff_location": {
        "id": 2,
        "name": "墨尔本市中心"
      },
      "pickup_date": "2025-05-01",
      "return_date": "2025-05-05",
      "status": "confirmed",
      "total_cost": "450.00"
    },
    // 更多预订...
  ]
}
```

#### 获取预订详情

```
GET /api/v1/bookings/{booking_id}
```

响应:
```json
{
  "id": "b12345",
  "car": {
    "id": 1,
    "name": "Toyota Corolla",
    "make": "Toyota",
    "model": "Corolla",
    "year": 2022,
    "image_url": "https://example.com/images/corolla.jpg"
  },
  "pickup_location": {
    "id": 1,
    "name": "墨尔本机场",
    "address": "墨尔本机场1号航站楼",
    "opening_hours": "Monday-Friday: 8AM-6PM, Saturday: 9AM-5PM, Sunday: Closed"
  },
  "dropoff_location": {
    "id": 2,
    "name": "墨尔本市中心",
    "address": "富兰克林街123号",
    "opening_hours": "Monday-Friday: 8AM-6PM, Saturday: 9AM-5PM, Sunday: Closed"
  },
  "pickup_date": "2025-05-01",
  "return_date": "2025-05-05",
  "booking_date": "2025-04-15T10:30:00Z",
  "status": "confirmed",
  "total_cost": "450.00",
  "base_cost": "260.00",
  "options_cost": "190.00",
  "duration_days": 4,
  "driver_age": 25,
  "options": {
    "damage_waiver": true,
    "extended_area": false,
    "satellite_navigation": true,
    "child_seats": 1,
    "additional_drivers": 0
  }
}
```

#### 取消预订

```
POST /api/v1/bookings/{booking_id}/cancel
```

请求体:
```json
{
  "reason": "change_of_plans",
  "comments": "计划有变，需要取消预订"
}
```

响应:
```json
{
  "id": "b12345",
  "status": "cancelled",
  "cancellation_date": "2025-04-20T15:45:30Z",
  "refund_amount": "405.00",
  "message": "您的预订已成功取消。退款将在3-5个工作日内处理。"
}
```

### 用户API

#### 获取用户信息

```
GET /api/v1/users/me
```

响应:
```json
{
  "id": 123,
  "username": "john_doe",
  "email": "john.doe@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "profile": {
    "phone": "+61412345678",
    "address": "123 Main St, Melbourne",
    "date_of_birth": "1990-01-01",
    "license_number": "DL12345678"
  }
}
```

#### 更新用户信息

```
PUT /api/v1/users/me
```

请求体:
```json
{
  "email": "john.new@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "profile": {
    "phone": "+61412345678",
    "address": "456 New St, Melbourne",
    "date_of_birth": "1990-01-01",
    "license_number": "DL12345678"
  }
}
```

响应: 与获取用户信息响应相同

### 位置API

#### 获取位置列表

```
GET /api/v1/locations
```

查询参数:
- `state_code`: 州代码，例如"VIC"（可选）
- `is_airport`: 是否为机场位置（可选）
- `page`: 页码，默认1
- `limit`: 每页记录数，默认20

响应:
```json
{
  "count": 15,
  "next": "/api/v1/locations?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "墨尔本机场",
      "address": "墨尔本机场1号航站楼",
      "city": "墨尔本",
      "state": {
        "id": 1,
        "name": "维多利亚",
        "code": "VIC"
      },
      "postal_code": "3045",
      "is_airport": true,
      "opening_hours": "Monday-Friday: 8AM-6PM, Saturday: 9AM-5PM, Sunday: Closed",
      "latitude": -37.669,
      "longitude": 144.841
    },
    // 更多位置...
  ]
}
```

#### 获取位置详情

```
GET /api/v1/locations/{location_id}
```

响应:
```json
{
  "id": 1,
  "name": "墨尔本机场",
  "address": "墨尔本机场1号航站楼",
  "city": "墨尔本",
  "state": {
    "id": 1,
    "name": "维多利亚",
    "code": "VIC"
  },
  "postal_code": "3045",
  "phone": "+61390207700",
  "email": "melbourne.airport@rushcarrental.com",
  "is_airport": true,
  "opening_hours": "Monday-Friday: 8AM-6PM, Saturday: 9AM-5PM, Sunday: Closed",
  "latitude": -37.669,
  "longitude": 144.841,
  "available_car_count": 25
}
```

### 支付API

#### 处理支付

```
POST /api/v1/payments/process
```

请求体:
```json
{
  "booking_id": "b12345",
  "payment_method_id": "pm_card_visa"
}
```

响应:
```json
{
  "payment_intent_id": "pi_1234",
  "client_secret": "pi_1234_secret_5678",
  "status": "requires_confirmation",
  "amount": 45000,  // 以分为单位
  "currency": "aud"
}
```

#### 确认支付

```
POST /api/v1/payments/confirm
```

请求体:
```json
{
  "payment_intent_id": "pi_1234"
}
```

响应:
```json
{
  "booking_id": "b12345",
  "payment_status": "succeeded",
  "receipt_url": "https://pay.example.com/receipts/r_1234"
}
```

## 数据格式

### 通用响应格式

所有API响应都遵循以下结构:

#### 成功响应

```json
{
  // 响应数据...
}
```

#### 列表响应

```json
{
  "count": 100,          // 总记录数
  "next": "/api/resource?page=2",  // 下一页URL
  "previous": null,      // 上一页URL
  "results": [
    // 数据项...
  ]
}
```

#### 错误响应

```json
{
  "error": {
    "code": "invalid_request",
    "message": "请求参数无效",
    "details": {
      "field1": ["错误详情1"],
      "field2": ["错误详情2"]
    }
  }
}
```

## 错误处理

### 错误代码

API使用标准HTTP状态码和自定义错误代码来表示错误:

| HTTP状态码 | 错误代码 | 描述 |
|-----------|---------|------|
| 400 | invalid_request | 请求参数无效 |
| 401 | unauthorized | 未授权的请求 |
| 403 | forbidden | 禁止访问 |
| 404 | not_found | 资源未找到 |
| 409 | conflict | 资源冲突 |
| 422 | validation_error | 数据验证错误 |
| 429 | rate_limit_exceeded | 请求频率超过限制 |
| 500 | server_error | 服务器内部错误 |

### 错误响应示例

```json
{
  "error": {
    "code": "validation_error",
    "message": "提供的数据无效",
    "details": {
      "pickup_date": ["取车日期不能早于今天"],
      "return_date": ["还车日期必须晚于取车日期"]
    }
  }
}
```

## API扩展方向

### 1. 高级搜索功能

扩展车辆搜索API，支持更多搜索条件:

```
GET /api/v1/cars/search
```

新增查询参数:
- `transmission`: 变速箱类型（"A"自动，"M"手动）
- `min_seats`: 最小座位数
- `features`: 特定功能（如"bluetooth", "gps"等）
- `fuel_type`: 燃料类型（"petrol", "diesel", "electric"等）

### 2. 评价和评论系统

```
POST /api/v1/bookings/{booking_id}/reviews
```

请求体:
```json
{
  "rating": 4.5,        // 1-5星评分
  "comment": "服务很好，车辆状况良好",
  "aspects": {
    "cleanliness": 5,   // 清洁度评分
    "value": 4,         // 性价比评分
    "service": 5,       // 服务评分
    "car_condition": 4  // 车辆状况评分
  }
}
```

### 3. 会员忠诚度计划

```
GET /api/v1/users/me/loyalty
```

响应:
```json
{
  "tier": "gold",
  "points": 1250,
  "next_tier": "platinum",
  "points_to_next_tier": 750,
  "benefits": [
    "免费升级",
    "额外驾驶员免费",
    "优先取车"
  ],
  "point_history": [
    {
      "date": "2025-03-15",
      "points": 200,
      "description": "完成预订 #b12345"
    },
    {
      "date": "2025-02-20",
      "points": 150,
      "description": "完成预订 #b12340"
    }
  ]
}
```

### 4. 移动应用集成

1. **推送通知API**:
   ```
   POST /api/v1/users/me/notifications/settings
   ```

2. **离线模式支持**:
   - 提供轻量级响应格式
   - 支持增量更新

3. **地理位置API**:
   ```
   GET /api/v1/locations/nearby?lat=-37.813&lng=144.963&radius=10
   ```

### 5. 第三方集成

1. **合作伙伴API**:
   - 酒店和航空公司集成
   - 旅游平台集成

2. **数据分析API**:
   - 获取匿名使用数据
   - 生成报告和洞察

---

本API设计文档旨在提供Rush Car Rental API的全面概述和规范。随着业务需求的变化和技术的发展，API设计可能会相应调整和扩展。
