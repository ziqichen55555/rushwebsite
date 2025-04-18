# Rush Car Rental Stripe支付集成文档

## 1. 概述

Rush Car Rental 系统使用Stripe作为支付处理服务，提供安全、可靠的在线支付功能。本文档详细说明了Stripe集成的实现方式和使用方法。

## 2. 环境配置

### 2.1 必要的环境变量

系统需要以下环境变量来正确配置Stripe集成：

- `STRIPE_SECRET_KEY`: Stripe API密钥（以`sk_`开头）
- `VITE_STRIPE_PUBLIC_KEY`: Stripe公钥（以`pk_`开头，用于前端）

这些密钥可以在Stripe开发者控制台获取：https://dashboard.stripe.com/apikeys

### 2.2 开发与生产环境

系统区分开发环境和生产环境的Stripe配置：

- **开发环境**: 使用测试密钥（`sk_test_*`和`pk_test_*`）
- **生产环境**: 使用生产密钥（`sk_live_*`和`pk_live_*`）

通过环境变量设置可以在不修改代码的情况下切换环境。

## 3. 支付流程

Rush Car Rental 系统支持两种Stripe支付流程：

### 3.1 直接支付处理

这种方式在我们的网站内完成整个支付过程。

#### 实现步骤：

1. **创建支付意向**:
   ```python
   import stripe
   from django.conf import settings
   
   stripe.api_key = settings.STRIPE_SECRET_KEY
   
   payment_intent = stripe.PaymentIntent.create(
       amount=int(booking.total_cost * 100),  # 金额以分为单位
       currency='aud',
       metadata={'booking_id': booking.id}
   )
   
   # 返回client_secret到前端
   client_secret = payment_intent.client_secret
   ```

2. **前端处理支付**:
   ```html
   <script src="https://js.stripe.com/v3/"></script>
   <script>
     const stripe = Stripe('{{ stripe_public_key }}');
     const elements = stripe.elements();
     
     // 创建支付表单元素
     const card = elements.create('card');
     card.mount('#card-element');
     
     // 处理提交
     const form = document.getElementById('payment-form');
     form.addEventListener('submit', async (event) => {
       event.preventDefault();
       
       const { error, paymentIntent } = await stripe.confirmCardPayment(
         '{{ client_secret }}', {
           payment_method: {
             card: card,
             billing_details: {
               name: '{{ booking.user.get_full_name }}',
             }
           }
         }
       );
       
       if (error) {
         // 显示错误信息
       } else if (paymentIntent.status === 'succeeded') {
         // 支付成功，重定向到成功页面
         window.location.href = '{{ success_url }}';
       }
     });
   </script>
   ```

### 3.2 Stripe托管结账页面

这种方式将用户重定向到Stripe托管的结账页面完成支付。

#### 实现步骤：

1. **创建结账会话**:
   ```python
   import stripe
   from django.conf import settings
   
   stripe.api_key = settings.STRIPE_SECRET_KEY
   
   # 获取域名（针对不同环境）
   domain_url = request.build_absolute_uri('/').rstrip('/')
   
   # 创建结账会话
   checkout_session = stripe.checkout.Session.create(
       payment_method_types=['card'],
       line_items=[{
           'price_data': {
               'currency': 'aud',
               'product_data': {
                   'name': f'Car Rental: {booking.car.get_display_name()}',
                   'description': f'From {booking.pickup_date} to {booking.return_date}',
               },
               'unit_amount': int(booking.total_cost * 100),
           },
           'quantity': 1,
       }],
       mode='payment',
       success_url=f'{domain_url}/bookings/{booking.id}/stripe_success/',
       cancel_url=f'{domain_url}/bookings/{booking.id}/payment/',
       metadata={
           'booking_id': booking.id,
       }
   )
   
   # 重定向到Stripe结账页面
   return redirect(checkout_session.url)
   ```

2. **处理支付成功回调**:
   ```python
   @login_required
   def stripe_success(request, booking_id):
       # 获取预订
       booking = get_object_or_404(Booking, id=booking_id, user=request.user)
       
       # 更新预订状态
       booking.status = 'confirmed'
       booking.save()
       
       # 重定向到预订成功页面
       return redirect('booking_success', booking_id=booking.id)
   ```

## 4. Webhook处理

为了确保支付状态更新，即使用户没有返回到网站，我们实现了Stripe Webhook处理。

### 4.1 配置Webhook

在Stripe开发者控制台中配置Webhook URL：`https://yourdomain.com/webhooks/stripe/`

### 4.2 实现Webhook处理函数

```python
@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        # 无效的请求
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        # 无效的签名
        return HttpResponse(status=400)
    
    # 处理支付事件
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        booking_id = payment_intent['metadata'].get('booking_id')
        
        if booking_id:
            booking = Booking.objects.get(id=booking_id)
            booking.status = 'confirmed'
            booking.save()
    
    return HttpResponse(status=200)
```

## 5. 测试支付

### 5.1 测试卡号

在测试环境中，可以使用以下Stripe测试卡号：

- **成功支付**: 4242 4242 4242 4242
- **需要验证**: 4000 0025 0000 3155
- **支付失败**: 4000 0000 0000 9995

### 5.2 使用测试脚本

项目包含测试脚本`dev/test_stripe.py`，可用于测试整个支付流程：

```bash
python dev/test_stripe.py
```

该脚本会模拟用户创建预订并完成支付的整个流程。

## 6. 错误处理

系统实现了全面的错误处理，以处理支付过程中可能出现的各种情况：

### 6.1 支付失败

当支付失败时，系统会显示适当的错误消息并允许用户重试或选择其他支付方式。

### 6.2 会话超时

如果支付会话超时，系统会创建新的支付会话并保留原有的预订信息。

### 6.3 网络错误

系统实现了自动重试机制，当检测到网络错误时会在后台重试API调用。

## 7. 安全考虑

### 7.1 API密钥保护

- 所有Stripe密钥都通过环境变量存储，不直接硬编码在代码中
- 生产环境中，使用环境变量管理系统（如.env文件）来存储密钥

### 7.2 数据验证

- 所有支付相关的请求都经过严格验证
- 在确认支付前验证预订数据的一致性

### 7.3 HTTPS

所有支付处理都通过HTTPS进行，确保数据传输的安全性。

## 8. 生产环境部署注意事项

1. 确保使用正确的生产环境API密钥
2. 配置Stripe Webhook，并设置适当的事件订阅
3. 实施日志记录和监控，以便及时发现和解决问题
4. 定期检查Stripe Dashboard，确认支付处理正常
5. 配置适当的错误报告机制，及时通知开发团队
