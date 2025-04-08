# Rush Car Rental Stripe 支付集成指南

## 概述

本文档详细说明了 Rush Car Rental 系统与 Stripe 支付平台的集成实现，包括支付流程、API 使用、配置要求以及安全最佳实践。

## 环境配置

### 必要的环境变量

Rush Car Rental 系统使用以下环境变量与 Stripe 进行集成：

```
STRIPE_SECRET_KEY=sk_test_...      # Stripe API密钥（服务器端）
VITE_STRIPE_PUBLIC_KEY=pk_test_... # Stripe公钥（前端使用）
```

这些密钥可以从 Stripe 控制面板获取：
- 测试环境：使用以 `sk_test_` 和 `pk_test_` 开头的密钥
- 生产环境：使用以 `sk_live_` 和 `pk_live_` 开头的密钥

### 密钥管理

- **开发环境**：密钥存储在项目根目录的 `.env` 文件中
- **生产环境**：密钥通过环境变量安全传递，不应硬编码在代码中

## 支付流程实现

Rush Car Rental 使用 Stripe 的支付意图 (Payment Intent) API 实现完整的支付流程：

### 服务器端实现

服务器端代码位于 `bookings/views.py` 中，主要实现以下功能：

1. **创建支付意图**

```python
def create_payment_intent(booking):
    """为预订创建Stripe支付意图"""
    try:
        intent = stripe.PaymentIntent.create(
            amount=int(booking.total_cost * 100),  # 转换为分
            currency="aud",
            metadata={
                "booking_id": booking.id,
                "user_id": booking.user.id,
                "car": f"{booking.car.make} {booking.car.model}"
            }
        )
        return intent
    except Exception as e:
        logger.error(f"创建支付意图失败: {str(e)}")
        raise
```

2. **处理支付成功回调**

```python
def process_successful_payment(booking_id, payment_intent_id):
    """处理成功的支付"""
    try:
        booking = Booking.objects.get(id=booking_id)
        
        # 验证支付意图
        payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        
        if payment_intent.status == "succeeded":
            booking.status = "confirmed"
            booking.save()
            
            # 发送确认邮件等后续操作
            send_booking_confirmation(booking)
            
            return True
    except Exception as e:
        logger.error(f"处理支付失败: {str(e)}")
    
    return False
```

### 客户端实现

客户端支付组件位于 `templates/bookings/payment.html` 中，使用 Stripe Elements JS 库实现：

```html
{% block content %}
<div class="container py-5">
    <h2 class="mb-4">确认支付</h2>
    
    <div class="card shadow-sm">
        <div class="card-body">
            <h5 class="card-title">订单摘要</h5>
            <p>车辆: {{ temp_booking.car.get_display_name }}</p>
            <p>取车: {{ temp_booking.pickup_location.name }} - {{ temp_booking.pickup_date }}</p>
            <p>还车: {{ temp_booking.dropoff_location.name }} - {{ temp_booking.return_date }}</p>
            <p class="font-weight-bold">总金额: ${{ temp_booking.total_cost|floatformat:2 }}</p>
            
            <div id="payment-element" class="mb-3">
                <!-- Stripe Elements将在此处渲染 -->
            </div>
            
            <button id="submit-button" class="btn btn-primary btn-block">
                确认支付
            </button>
            
            <div id="payment-message" class="mt-2 text-center" style="display:none;"></div>
        </div>
    </div>
</div>

<script src="https://js.stripe.com/v3/"></script>
<script>
    // 初始化Stripe
    const stripe = Stripe('{{ stripe_public_key }}');
    const clientSecret = '{{ client_secret }}';
    
    // 创建支付表单
    const elements = stripe.elements({
        clientSecret: clientSecret
    });
    const paymentElement = elements.create('payment');
    paymentElement.mount('#payment-element');
    
    // 处理提交
    const form = document.getElementById('payment-form');
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // 禁用提交按钮以防止多次点击
        document.getElementById('submit-button').disabled = true;
        
        // 确认支付
        const {error} = await stripe.confirmPayment({
            elements,
            confirmParams: {
                return_url: '{{ success_url }}',
            }
        });
        
        if (error) {
            const messageDiv = document.getElementById('payment-message');
            messageDiv.textContent = error.message;
            messageDiv.style.display = 'block';
            document.getElementById('submit-button').disabled = false;
        }
    });
</script>
{% endblock %}
```

## 支付流程

Rush Car Rental 的支付流程如下：

1. **创建预订**：用户选择车辆和日期，系统创建临时预订记录。

2. **选择附加选项**：用户选择额外服务（如保险、GPS等），系统计算总价。

3. **初始化支付**：
   - 服务器创建 Stripe PaymentIntent
   - 返回 client_secret 到前端

4. **收集支付信息**：
   - 前端使用 Stripe Elements 渲染支付表单
   - 用户输入信息并提交

5. **处理支付**：
   - Stripe 处理支付并返回结果
   - 成功时重定向到成功页面
   - 失败时显示错误消息

6. **确认预订**：
   - 服务器验证支付成功
   - 更新预订状态为已确认
   - 发送确认邮件给用户

## Stripe Webhook 处理 (计划中)

为了处理异步支付事件和提高可靠性，Rush Car Rental 计划实现 Stripe Webhook 处理：

```python
@csrf_exempt
def stripe_webhook(request):
    """处理来自Stripe的webhook事件"""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)
    
    # 处理事件
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        booking_id = payment_intent['metadata']['booking_id']
        process_successful_payment(booking_id, payment_intent['id'])
    
    return HttpResponse(status=200)
```

## 测试与开发

### 使用测试密钥

在开发和测试环境中，应始终使用 Stripe 测试密钥（以 `sk_test_` 和 `pk_test_` 开头）。

### 测试卡号

可以使用以下测试卡号进行支付测试：

| 卡号                 | 描述             |
|---------------------|------------------|
| 4242 4242 4242 4242 | 成功支付         |
| 4000 0000 0000 0002 | 卡拒绝           |
| 4000 0000 0000 9995 | 余额不足         |
| 4000 0000 0000 3220 | 3D Secure 认证   |

### 本地测试

在本地开发环境中测试 Stripe 集成，确保：

1. `.env` 文件中包含必要的环境变量
2. 使用测试密钥和测试卡号
3. 使用正确的货币和金额
4. 检查支付状态和错误处理
5. 验证数据库状态更新

## 安全最佳实践

1. **服务器端验证**：所有支付处理逻辑应在服务器端实现，不要在客户端执行关键业务逻辑。

2. **使用 HTTPS**：所有支付相关页面必须使用 HTTPS 协议。

3. **环境变量管理**：API 密钥应通过环境变量传递，不应硬编码在源代码中。

4. **日志与监控**：记录所有支付相关事件，但不要记录敏感信息（如完整的卡号）。

5. **错误处理**：实现健壮的错误处理逻辑，避免暴露敏感信息。

6. **定期审计**：定期审查支付流程和代码，确保符合 PCI DSS 要求。

## 问题排查

### 常见支付错误

| 错误代码               | 描述                           | 解决方案                    |
|-----------------------|-------------------------------|----------------------------|
| authentication_required | 需要额外认证                   | 提示用户完成 3D Secure 认证  |
| card_declined         | 卡被拒绝                       | 提示用户尝试其他支付方式      |
| expired_card          | 卡已过期                       | 提示用户更新卡信息          |
| incorrect_cvc         | CVC 不正确                    | 提示用户检查 CVC           |
| processing_error      | 处理支付时出错                 | 建议用户稍后重试            |

### 调试技巧

1. **检查 Stripe Dashboard**：Stripe 控制面板提供详细的交易日志和错误信息。

2. **查看服务器日志**：检查应用程序日志中的支付相关错误。

3. **验证配置**：确保环境变量和 Stripe 配置正确。

4. **测试模式**：使用 Stripe 测试模式和测试卡进行故障排除。

## 未来计划

1. **实现订阅支持**：为常客计划添加 Stripe Subscription API 支持。

2. **增强退款流程**：完善退款处理流程和相关用户界面。

3. **多币种支持**：添加多币种支付支持，特别是对国际客户。

4. **支付方式扩展**：除信用卡外，增加更多支付方式（如 Apple Pay、Google Pay）。

---

本文档提供了 Rush Car Rental 系统 Stripe 支付集成的详细说明。随着业务需求变化，可能会更新支付流程和实现方式。