# 驾驶员信息集成设计文档

## 概述

本文档描述了 Rush Car Rental 系统中驾驶员信息管理的改进，使系统能够在预订流程中重用用户的驾驶员信息，并将新添加的驾驶员信息保存到用户的个人资料中。

## 功能改进

### 1. 在预订流程中显示已保存的驾驶员信息

在预订流程的驾驶员信息页面，系统现在会检查用户个人资料中是否已有保存的驾驶员信息。如果有，系统会显示已保存的驾驶员信息，允许用户选择使用现有的驾驶员信息或创建新的驾驶员信息。

### 2. 将新添加的驾驶员信息保存到用户个人资料

当用户在预订过程中添加新的驾驶员信息时，系统会自动将这些信息添加到用户的个人资料中。这样用户在下次预订时就可以重用这些信息，无需重新输入。

### 3. 主驾驶员标记

系统支持将一个驾驶员标记为主驾驶员，主驾驶员会在用户的个人资料和预订过程中被自动选中，简化用户体验。

## 技术实现

### 视图层改进

1. `add_drivers` 视图函数增强：
   - 从用户个人资料中获取已保存的驾驶员信息
   - 处理用户选择使用现有驾驶员信息的请求
   - 将所选驾驶员信息与预订关联

2. `process_payment` 和 `stripe_success` 视图函数改进：
   - 在支付成功后，将新添加的驾驶员信息保存到用户个人资料中
   - 如果是主驾驶员，更新用户资料中的主驾驶员设置

### 模板改进

1. `drivers.html` 模板改进：
   - 添加已保存驾驶员信息的展示区域
   - 允许用户选择现有驾驶员或添加新驾驶员
   - 修复模板语法错误，确保所有模板块标签正确配对

### 表单和表单集改进

1. `DriverFormSet` 配置优化：
   - 将 `extra` 参数从 0 调整为 1，确保始终有一个表单实例可用
   - 保留 `max_num=1` 和 `validate_max=True` 设置，确保每次只能添加一个驾驶员

## 代码示例

### 驾驶员表单集定义

```python
# 创建驾驶员表单集，默认只需要一个驾驶员信息
DriverFormSet = formset_factory(DriverForm, extra=1, can_delete=False, max_num=1, validate_max=True)
```

### 视图层处理用户已有驾驶员信息

```python
# 获取用户已保存的驾驶员信息
user_drivers = []
using_existing_driver = False
selected_driver_id = None

if request.user.is_authenticated and hasattr(request.user, 'profile'):
    # 获取用户资料中的驾驶员信息
    from .models import Driver
    user_drivers = request.user.profile.drivers.all()
```

### 处理选择现有驾驶员

```python
# 检查是否使用了现有驾驶员
if 'use_existing_driver' in request.POST and request.POST['use_existing_driver']:
    try:
        selected_driver_id = int(request.POST['use_existing_driver'])
        selected_driver = Driver.objects.get(id=selected_driver_id)
        
        # 确保驾驶员属于当前用户
        if selected_driver in user_drivers:
            # 创建一个临时驾驶员数据字典
            driver_data = {
                'first_name': selected_driver.first_name,
                'last_name': selected_driver.last_name,
                'email': selected_driver.email,
                # ...其他驾驶员字段...
            }
            
            # 存储驾驶员数据
            temp_booking.temp_drivers_data = [driver_data]
            temp_booking.existing_driver_id = selected_driver_id
            using_existing_driver = True
            
            # 跳转到下一步
            return redirect('add_options', temp_booking_id=temp_booking_id)
    except (ValueError, Driver.DoesNotExist):
        messages.error(request, "Invalid driver selection.")
```

### 将新驾驶员信息添加到用户个人资料

```python
# 如果用户登录且没有选择使用现有的驾驶员信息，则为其保存驾驶员信息到用户资料
if request.user.is_authenticated and not hasattr(temp_booking, 'existing_driver_id'):
    if driver.is_primary:
        # 如果这是主驾驶员，首先取消用户现有的主驾驶员
        request.user.profile.drivers.filter(is_primary=True).update(is_primary=False)
    
    # 将驾驶员添加到用户资料
    request.user.profile.drivers.add(driver)
    logger.info(f"已将驾驶员 {driver.get_full_name()} 添加到用户 {request.user.username} 的资料")
```

## 模板改进说明

1. 驾驶员信息展示区域：
   ```html
   {% if user_drivers %}
   <!-- 显示已保存的驾驶员选项 -->
   <div class="mb-4">
       <h5 class="border-bottom pb-2 mb-3">Your Saved Driver Information</h5>
       
       <form method="post" class="mb-4">
           {% csrf_token %}
           <div class="row">
               {% for driver in user_drivers %}
               <div class="col-md-6 mb-3">
                   <div class="card h-100 {% if driver.is_primary %}border-warning{% endif %}">
                       <div class="card-header bg-light">
                           <div class="form-check">
                               <input class="form-check-input" type="radio" name="use_existing_driver" 
                                   id="driver-{{ driver.id }}" value="{{ driver.id }}"
                                   {% if driver.is_primary %}checked{% endif %}>
                               <label class="form-check-label" for="driver-{{ driver.id }}">
                                   <strong>{{ driver.get_full_name }}</strong>
                                   {% if driver.is_primary %}
                                   <span class="badge bg-warning text-dark ms-2">Primary</span>
                                   {% endif %}
                               </label>
                           </div>
                       </div>
                       <div class="card-body">
                           <p class="mb-1"><small><strong>License:</strong> {{ driver.license_number }}</small></p>
                           <p class="mb-1"><small><strong>Mobile:</strong> {{ driver.mobile }}</small></p>
                           <p class="mb-1"><small><strong>Email:</strong> {{ driver.email }}</small></p>
                       </div>
                   </div>
               </div>
               {% endfor %}
           </div>
           
           <div class="d-grid gap-2">
               <button type="submit" class="btn btn-primary">
                   <i class="fas fa-user-check me-1"></i> Use Selected Driver
               </button>
           </div>
       </form>
       
       <div class="text-center mb-4">
           <p>- OR -</p>
           <button class="btn btn-outline-secondary btn-sm" type="button" 
                   onclick="document.getElementById('new-driver-form').style.display = 'block'; this.style.display = 'none';">
               <i class="fas fa-plus me-1"></i> Add New Driver
           </button>
       </div>
   </div>
   
   <div id="new-driver-form" {% if user_drivers %}style="display: none;"{% endif %}>
   {% endif %}
   ```

2. 模板块标签修复：
   ```html
   {% block content %}
   <!-- 内容部分 -->
   {% endblock %}
   
   {% block extra_js %}
   <!-- JavaScript 代码 -->
   {% endblock %}
   
   {% block extra_css %}
   <!-- CSS 样式 -->
   {% endblock %}
   ```

## 测试情况

通过测试，确认以下功能正常工作：

1. 用户可以在预订流程中查看和选择已有的驾驶员信息
2. 用户可以在预订流程中添加新的驾驶员信息
3. 新添加的驾驶员信息会自动保存到用户的个人资料中
4. 主驾驶员在用户个人资料中会被自动标记

## 结论

此次改进通过允许用户重用现有的驾驶员信息，简化了预订流程，提高了用户体验。同时，自动保存驾驶员信息到用户个人资料的功能，减少了用户在多次预订时的重复输入，使整个系统更加高效和易用。

解决的模板语法错误确保了系统的稳定性，修复了 TemplateSyntaxError 错误，保持了原有的UI设计不变。