# Rush Car Rental 开发模式与 CRUD 开发指南

## 一、项目开发模式总结

根据项目代码和文档，Rush Car Rental 采用了以下开发模式：

### 1. 多环境分层架构

项目采用分层环境架构，具体包括：
- **开发环境**：使用 SQLite 数据库，便于快速开发和本地测试
- **测试环境**：用于集成测试和功能测试
- **生产环境**：使用 PostgreSQL 数据库，适合高负载和数据持久性

通过环境变量 `RUSH_ENVIRONMENT` 控制切换，实现了同一代码库在不同环境下的灵活部署。

### 2. 模块化设计

项目按功能划分为多个独立模块：
- **accounts**: 用户认证和个人资料管理
- **bookings**: 预订流程和支付处理
- **cars**: 车辆信息和搜索功能
- **locations**: 地点管理
- **pages**: 静态页面内容

每个模块都有自己的 models、views、forms 和 templates，保持了高内聚低耦合的设计原则。

### 3. 渐进式功能开发

项目采用渐进式开发策略，先实现核心功能，再逐步添加高级特性：
1. 基础框架搭建 (Django + Bootstrap)
2. 用户认证系统
3. 车辆搜索和展示
4. 预订流程实现
5. 驾驶员信息管理
6. 支付集成

这种方法确保了项目可以在任何阶段都有可用的功能。

### 4. 适应性支付集成

支付系统采用了适应性设计：
- 在开发环境中使用 MockStripe 类模拟支付流程
- 在生产环境中连接真实的 Stripe API
- 通过环境变量控制切换，无需修改代码

这种设计使开发人员可以在没有 Stripe 密钥的情况下进行完整的功能测试。

### 5. 用户体验驱动设计

整个项目以用户体验为中心：
- 简化的预订流程，减少点击步骤
- 驾驶员信息的自动保存和重用
- 响应式设计，适配各种设备
- 详细的错误反馈和操作指导

### 6. 综合测试策略

项目包含多层次的测试策略：
- **test_db_config.py**: 测试数据库配置
- 模型单元测试
- 视图功能测试
- 集成测试

### 7. 文档驱动开发

项目重视文档：
- **dev/driver_information_integration.md**: 功能设计文档
- **dev/project_setup.md**: 项目安装与设置指南

文档不仅记录已完成的工作，也指导后续开发，确保代码质量和一致性。

### 8. 后端渲染+前端增强

技术栈选择上：
- 使用 Django 的模板系统进行主要页面渲染
- 使用 Bootstrap 5 框架提供响应式 UI
- 使用 JavaScript 增强用户交互体验
- 在需要高度交互的页面（如支付）集成现代前端库（如 Stripe.js）

这种混合模式既保持了开发效率，又满足了现代用户界面的需求。

### 9. 持续集成与部署

系统设计考虑了持续集成和部署：
- 使用环境变量管理敏感配置
- 支持容器化部署
- 日志系统设计便于监控

### 10. 安全优先原则

项目注重安全实践：
- 敏感信息通过环境变量管理
- 集成第三方安全支付系统
- 用户认证和授权机制
- CSRF 保护和表单验证

## 二、CRUD 开发指南

对于 Rush Car Rental 项目，如果有新的需求需要实现 CRUD（创建、读取、更新、删除）功能，应该遵循以下开发流程：

### 1. 数据模型设计

#### 步骤 1.1: 模型定义
1. 在相应的应用中的 `models.py` 文件中定义新模型
2. 遵循现有项目的命名约定和字段类型选择

```python
# 示例：在 cars/models.py 中添加 Maintenance 模型
from django.db import models
from django.utils.translation import gettext_lazy as _

class Maintenance(models.Model):
    MAINTENANCE_STATUS = [
        ('scheduled', _('Scheduled')),
        ('in_progress', _('In Progress')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
    ]
    
    car = models.ForeignKey('Car', on_delete=models.CASCADE, related_name='maintenance_records')
    maintenance_type = models.CharField(_('Maintenance Type'), max_length=100)
    description = models.TextField(_('Description'))
    scheduled_date = models.DateField(_('Scheduled Date'))
    completion_date = models.DateField(_('Completion Date'), null=True, blank=True)
    status = models.CharField(_('Status'), max_length=20, choices=MAINTENANCE_STATUS, default='scheduled')
    cost = models.DecimalField(_('Cost'), max_digits=10, decimal_places=2, default=0)
    performed_by = models.CharField(_('Performed By'), max_length=100, blank=True)
    notes = models.TextField(_('Notes'), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Maintenance Record')
        verbose_name_plural = _('Maintenance Records')
    
    def __str__(self):
        return f"{self.car.make} {self.car.model} - {self.maintenance_type} ({self.scheduled_date})"
```

#### 步骤 1.2: 执行数据库迁移
```bash
python manage.py makemigrations
python manage.py migrate
```

#### 步骤 1.3: 在管理界面注册模型
```python
# cars/admin.py
from django.contrib import admin
from .models import Car, CarFeature, Maintenance

class MaintenanceAdmin(admin.ModelAdmin):
    list_display = ('car', 'maintenance_type', 'scheduled_date', 'status', 'cost')
    list_filter = ('status', 'maintenance_type', 'scheduled_date')
    search_fields = ('car__make', 'car__model', 'maintenance_type', 'description')
    date_hierarchy = 'scheduled_date'
    
admin.site.register(Maintenance, MaintenanceAdmin)
```

### 2. 表单设计

为新的模型创建表单类：

```python
# cars/forms.py
from django import forms
from .models import Maintenance

class MaintenanceForm(forms.ModelForm):
    class Meta:
        model = Maintenance
        fields = ['car', 'maintenance_type', 'description', 'scheduled_date', 
                 'completion_date', 'status', 'cost', 'performed_by', 'notes']
        widgets = {
            'scheduled_date': forms.DateInput(attrs={'type': 'date'}),
            'completion_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        scheduled_date = cleaned_data.get('scheduled_date')
        completion_date = cleaned_data.get('completion_date')
        
        if completion_date and scheduled_date and completion_date < scheduled_date:
            raise forms.ValidationError("Completion date cannot be earlier than scheduled date.")
        
        return cleaned_data
```

### 3. URL 设计

在应用的 `urls.py` 文件中添加新的 URL 路由：

```python
# cars/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # 现有 URL 路由
    path('maintenance/', views.maintenance_list, name='maintenance_list'),
    path('maintenance/create/', views.maintenance_create, name='maintenance_create'),
    path('maintenance/<int:maintenance_id>/', views.maintenance_detail, name='maintenance_detail'),
    path('maintenance/<int:maintenance_id>/update/', views.maintenance_update, name='maintenance_update'),
    path('maintenance/<int:maintenance_id>/delete/', views.maintenance_delete, name='maintenance_delete'),
]
```

### 4. 视图实现

实现 CRUD 操作的视图函数：

```python
# cars/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.translation import gettext as _
from .models import Maintenance, Car
from .forms import MaintenanceForm

# 列表视图（Read - 列表）
@login_required
def maintenance_list(request):
    maintenance_records = Maintenance.objects.all().order_by('-scheduled_date')
    return render(request, 'cars/maintenance_list.html', {
        'maintenance_records': maintenance_records,
        'title': _('Maintenance Records')
    })

# 详情视图（Read - 单条）
@login_required
def maintenance_detail(request, maintenance_id):
    maintenance = get_object_or_404(Maintenance, id=maintenance_id)
    return render(request, 'cars/maintenance_detail.html', {
        'maintenance': maintenance,
        'title': _('Maintenance Details')
    })

# 创建视图（Create）
@login_required
@permission_required('cars.add_maintenance', raise_exception=True)
def maintenance_create(request):
    if request.method == 'POST':
        form = MaintenanceForm(request.POST)
        if form.is_valid():
            maintenance = form.save()
            messages.success(request, _('Maintenance record created successfully.'))
            return redirect('maintenance_detail', maintenance_id=maintenance.id)
    else:
        # 预填充车辆选择（如果从车辆详情页进入）
        initial_data = {}
        if 'car_id' in request.GET:
            try:
                car = Car.objects.get(id=request.GET['car_id'])
                initial_data['car'] = car
            except Car.DoesNotExist:
                pass
        
        form = MaintenanceForm(initial=initial_data)
    
    return render(request, 'cars/maintenance_form.html', {
        'form': form,
        'title': _('Add Maintenance Record'),
        'submit_text': _('Create')
    })

# 更新视图（Update）
@login_required
@permission_required('cars.change_maintenance', raise_exception=True)
def maintenance_update(request, maintenance_id):
    maintenance = get_object_or_404(Maintenance, id=maintenance_id)
    
    if request.method == 'POST':
        form = MaintenanceForm(request.POST, instance=maintenance)
        if form.is_valid():
            form.save()
            messages.success(request, _('Maintenance record updated successfully.'))
            return redirect('maintenance_detail', maintenance_id=maintenance.id)
    else:
        form = MaintenanceForm(instance=maintenance)
    
    return render(request, 'cars/maintenance_form.html', {
        'form': form,
        'maintenance': maintenance,
        'title': _('Update Maintenance Record'),
        'submit_text': _('Update')
    })

# 删除视图（Delete）
@login_required
@permission_required('cars.delete_maintenance', raise_exception=True)
def maintenance_delete(request, maintenance_id):
    maintenance = get_object_or_404(Maintenance, id=maintenance_id)
    
    if request.method == 'POST':
        car_id = maintenance.car.id  # 保存一下车辆 ID 用于重定向
        maintenance.delete()
        messages.success(request, _('Maintenance record deleted successfully.'))
        
        # 如果是从车辆详情页来的，返回车辆详情页
        if 'next' in request.GET and request.GET['next'] == 'car_detail':
            return redirect('car_detail', car_id=car_id)
        return redirect('maintenance_list')
    
    return render(request, 'cars/maintenance_confirm_delete.html', {
        'maintenance': maintenance,
        'title': _('Delete Maintenance Record')
    })
```

### 5. 模板设计

在 `templates/cars/` 目录下创建以下模板：

#### 列表页模板 (maintenance_list.html)
```html
{% extends 'base.html' %}

{% block title %}{{ title }} - Rush Car Rental{% endblock %}

{% block content %}
<!-- 面包屑导航 -->
<div class="breadcrumb-container py-2">
    <div class="container">
        <nav aria-label="breadcrumb">
            <ol class="breadcrumb breadcrumb-custom mb-0">
                <li class="breadcrumb-item">
                    <a href="{% url 'home' %}" class="breadcrumb-home">
                        <i class="fas fa-home"></i> Home
                    </a>
                </li>
                <li class="breadcrumb-item active" aria-current="page">
                    <i class="fas fa-tools"></i> {{ title }}
                </li>
            </ol>
        </nav>
    </div>
</div>

<section class="py-5">
    <div class="container">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h1 class="h2">{{ title }}</h1>
            {% if perms.cars.add_maintenance %}
            <a href="{% url 'maintenance_create' %}" class="btn btn-warning">
                <i class="fas fa-plus me-1"></i> Add New Record
            </a>
            {% endif %}
        </div>
        
        <!-- 筛选器 -->
        <div class="card shadow mb-4">
            <div class="card-header bg-light">
                <h5 class="mb-0">Filter Records</h5>
            </div>
            <div class="card-body">
                <form method="get" class="row g-3">
                    <div class="col-md-4">
                        <label class="form-label">Status</label>
                        <select name="status" class="form-select">
                            <option value="">All Statuses</option>
                            <option value="scheduled" {% if request.GET.status == 'scheduled' %}selected{% endif %}>Scheduled</option>
                            <option value="in_progress" {% if request.GET.status == 'in_progress' %}selected{% endif %}>In Progress</option>
                            <option value="completed" {% if request.GET.status == 'completed' %}selected{% endif %}>Completed</option>
                            <option value="cancelled" {% if request.GET.status == 'cancelled' %}selected{% endif %}>Cancelled</option>
                        </select>
                    </div>
                    <div class="col-md-4">
                        <label class="form-label">Car Model</label>
                        <input type="text" name="car_model" class="form-control" value="{{ request.GET.car_model }}">
                    </div>
                    <div class="col-md-4">
                        <label class="form-label">Maintenance Type</label>
                        <input type="text" name="maintenance_type" class="form-control" value="{{ request.GET.maintenance_type }}">
                    </div>
                    <div class="col-12 text-end">
                        <button type="submit" class="btn btn-primary">
                            <i class="fas fa-filter me-1"></i> Apply Filters
                        </button>
                        <a href="{% url 'maintenance_list' %}" class="btn btn-outline-secondary">
                            <i class="fas fa-times me-1"></i> Clear Filters
                        </a>
                    </div>
                </form>
            </div>
        </div>
        
        <!-- 记录列表 -->
        <div class="card shadow">
            <div class="card-body p-0">
                {% if maintenance_records %}
                <div class="table-responsive">
                    <table class="table table-hover mb-0">
                        <thead class="table-light">
                            <tr>
                                <th>Car</th>
                                <th>Maintenance Type</th>
                                <th>Scheduled Date</th>
                                <th>Status</th>
                                <th>Cost</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for record in maintenance_records %}
                            <tr>
                                <td>
                                    <a href="{% url 'car_detail' record.car.id %}">
                                        {{ record.car.make }} {{ record.car.model }}
                                    </a>
                                </td>
                                <td>{{ record.maintenance_type }}</td>
                                <td>{{ record.scheduled_date|date:"M d, Y" }}</td>
                                <td>
                                    <span class="badge {% if record.status == 'scheduled' %}bg-primary{% elif record.status == 'in_progress' %}bg-warning text-dark{% elif record.status == 'completed' %}bg-success{% else %}bg-danger{% endif %}">
                                        {{ record.get_status_display }}
                                    </span>
                                </td>
                                <td>${{ record.cost }}</td>
                                <td>
                                    <a href="{% url 'maintenance_detail' record.id %}" class="btn btn-sm btn-outline-secondary">
                                        <i class="fas fa-eye"></i>
                                    </a>
                                    {% if perms.cars.change_maintenance %}
                                    <a href="{% url 'maintenance_update' record.id %}" class="btn btn-sm btn-outline-primary">
                                        <i class="fas fa-edit"></i>
                                    </a>
                                    {% endif %}
                                    {% if perms.cars.delete_maintenance %}
                                    <a href="{% url 'maintenance_delete' record.id %}" class="btn btn-sm btn-outline-danger">
                                        <i class="fas fa-trash"></i>
                                    </a>
                                    {% endif %}
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
                {% else %}
                <div class="text-center py-5">
                    <div class="mb-3">
                        <i class="fas fa-tools fa-3x text-muted"></i>
                    </div>
                    <h4>No maintenance records found</h4>
                    <p class="text-muted">No records match your criteria or no records have been added yet.</p>
                    {% if perms.cars.add_maintenance %}
                    <a href="{% url 'maintenance_create' %}" class="btn btn-warning">
                        <i class="fas fa-plus me-1"></i> Add First Record
                    </a>
                    {% endif %}
                </div>
                {% endif %}
            </div>
        </div>
    </div>
</section>
{% endblock %}
```

#### 表单模板 (maintenance_form.html)
```html
{% extends 'base.html' %}

{% block title %}{{ title }} - Rush Car Rental{% endblock %}

{% block content %}
<!-- 面包屑导航 -->
<div class="breadcrumb-container py-2">
    <div class="container">
        <nav aria-label="breadcrumb">
            <ol class="breadcrumb breadcrumb-custom mb-0">
                <li class="breadcrumb-item">
                    <a href="{% url 'home' %}" class="breadcrumb-home">
                        <i class="fas fa-home"></i> Home
                    </a>
                </li>
                <li class="breadcrumb-item">
                    <a href="{% url 'maintenance_list' %}">
                        <i class="fas fa-tools"></i> Maintenance Records
                    </a>
                </li>
                <li class="breadcrumb-item active" aria-current="page">
                    {{ title }}
                </li>
            </ol>
        </nav>
    </div>
</div>

<section class="py-5">
    <div class="container">
        <div class="row">
            <div class="col-md-8 mx-auto">
                <div class="card shadow">
                    <div class="card-header bg-warning text-dark">
                        <h4 class="mb-0">{{ title }}</h4>
                    </div>
                    <div class="card-body">
                        <form method="post" class="needs-validation" novalidate>
                            {% csrf_token %}
                            
                            {% if form.non_field_errors %}
                            <div class="alert alert-danger">
                                {{ form.non_field_errors }}
                            </div>
                            {% endif %}
                            
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label for="{{ form.car.id_for_label }}" class="form-label">Car <span class="text-danger">*</span></label>
                                    {{ form.car }}
                                    {% if form.car.errors %}
                                    <div class="invalid-feedback d-block">
                                        {{ form.car.errors }}
                                    </div>
                                    {% endif %}
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label for="{{ form.maintenance_type.id_for_label }}" class="form-label">Maintenance Type <span class="text-danger">*</span></label>
                                    {{ form.maintenance_type }}
                                    {% if form.maintenance_type.errors %}
                                    <div class="invalid-feedback d-block">
                                        {{ form.maintenance_type.errors }}
                                    </div>
                                    {% endif %}
                                </div>
                            </div>
                            
                            <div class="mb-3">
                                <label for="{{ form.description.id_for_label }}" class="form-label">Description <span class="text-danger">*</span></label>
                                {{ form.description }}
                                {% if form.description.errors %}
                                <div class="invalid-feedback d-block">
                                    {{ form.description.errors }}
                                </div>
                                {% endif %}
                            </div>
                            
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label for="{{ form.scheduled_date.id_for_label }}" class="form-label">Scheduled Date <span class="text-danger">*</span></label>
                                    {{ form.scheduled_date }}
                                    {% if form.scheduled_date.errors %}
                                    <div class="invalid-feedback d-block">
                                        {{ form.scheduled_date.errors }}
                                    </div>
                                    {% endif %}
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label for="{{ form.status.id_for_label }}" class="form-label">Status <span class="text-danger">*</span></label>
                                    {{ form.status }}
                                    {% if form.status.errors %}
                                    <div class="invalid-feedback d-block">
                                        {{ form.status.errors }}
                                    </div>
                                    {% endif %}
                                </div>
                            </div>
                            
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label for="{{ form.completion_date.id_for_label }}" class="form-label">Completion Date</label>
                                    {{ form.completion_date }}
                                    {% if form.completion_date.errors %}
                                    <div class="invalid-feedback d-block">
                                        {{ form.completion_date.errors }}
                                    </div>
                                    {% endif %}
                                    <div class="form-text">Leave blank if not completed yet</div>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label for="{{ form.cost.id_for_label }}" class="form-label">Cost <span class="text-danger">*</span></label>
                                    {{ form.cost }}
                                    {% if form.cost.errors %}
                                    <div class="invalid-feedback d-block">
                                        {{ form.cost.errors }}
                                    </div>
                                    {% endif %}
                                </div>
                            </div>
                            
                            <div class="mb-3">
                                <label for="{{ form.performed_by.id_for_label }}" class="form-label">Performed By</label>
                                {{ form.performed_by }}
                                {% if form.performed_by.errors %}
                                <div class="invalid-feedback d-block">
                                    {{ form.performed_by.errors }}
                                </div>
                                {% endif %}
                            </div>
                            
                            <div class="mb-3">
                                <label for="{{ form.notes.id_for_label }}" class="form-label">Notes</label>
                                {{ form.notes }}
                                {% if form.notes.errors %}
                                <div class="invalid-feedback d-block">
                                    {{ form.notes.errors }}
                                </div>
                                {% endif %}
                            </div>
                            
                            <div class="d-flex justify-content-between mt-4">
                                <a href="{% if maintenance %}{% url 'maintenance_detail' maintenance.id %}{% else %}{% url 'maintenance_list' %}{% endif %}" class="btn btn-outline-secondary">
                                    <i class="fas fa-arrow-left me-1"></i> Cancel
                                </a>
                                <button type="submit" class="btn btn-warning">
                                    <i class="fas fa-save me-1"></i> {{ submit_text }}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>
</section>
{% endblock %}

{% block extra_js %}
<script>
document.addEventListener('DOMContentLoaded', function() {
    // 添加Bootstrap样式到所有表单元素
    document.querySelectorAll('input:not([type="checkbox"]), select, textarea').forEach(function(element) {
        element.classList.add('form-control');
    });
    
    // 检查状态更改，如果选择了"已完成"，则显示完成日期字段
    const statusSelect = document.querySelector('select[name="status"]');
    const completionDateField = document.querySelector('input[name="completion_date"]');
    
    function updateCompletionDateField() {
        if (statusSelect.value === 'completed' && !completionDateField.value) {
            // 如果状态是完成但没有完成日期，自动填入今天的日期
            const today = new Date();
            const year = today.getFullYear();
            const month = String(today.getMonth() + 1).padStart(2, '0');
            const day = String(today.getDate()).padStart(2, '0');
            completionDateField.value = `${year}-${month}-${day}`;
        }
    }
    
    if (statusSelect && completionDateField) {
        statusSelect.addEventListener('change', updateCompletionDateField);
    }
});
</script>
{% endblock %}
```

#### 详情页模板 (maintenance_detail.html)
```html
{% extends 'base.html' %}

{% block title %}{{ title }} - Rush Car Rental{% endblock %}

{% block content %}
<!-- 面包屑导航 -->
<div class="breadcrumb-container py-2">
    <div class="container">
        <nav aria-label="breadcrumb">
            <ol class="breadcrumb breadcrumb-custom mb-0">
                <li class="breadcrumb-item">
                    <a href="{% url 'home' %}" class="breadcrumb-home">
                        <i class="fas fa-home"></i> Home
                    </a>
                </li>
                <li class="breadcrumb-item">
                    <a href="{% url 'maintenance_list' %}">
                        <i class="fas fa-tools"></i> Maintenance Records
                    </a>
                </li>
                <li class="breadcrumb-item active" aria-current="page">
                    {{ maintenance.maintenance_type }}
                </li>
            </ol>
        </nav>
    </div>
</div>

<section class="py-5">
    <div class="container">
        <div class="row">
            <div class="col-md-8">
                <div class="card shadow">
                    <div class="card-header bg-warning text-dark d-flex justify-content-between align-items-center">
                        <h4 class="mb-0">Maintenance Details</h4>
                        <div>
                            {% if perms.cars.change_maintenance %}
                            <a href="{% url 'maintenance_update' maintenance.id %}" class="btn btn-sm btn-dark">
                                <i class="fas fa-edit me-1"></i> Edit
                            </a>
                            {% endif %}
                            {% if perms.cars.delete_maintenance %}
                            <a href="{% url 'maintenance_delete' maintenance.id %}" class="btn btn-sm btn-outline-danger">
                                <i class="fas fa-trash me-1"></i> Delete
                            </a>
                            {% endif %}
                        </div>
                    </div>
                    <div class="card-body">
                        <div class="row mb-4">
                            <div class="col-md-6">
                                <h5 class="mb-3">Maintenance Information</h5>
                                <p class="mb-2"><strong>Maintenance Type:</strong> {{ maintenance.maintenance_type }}</p>
                                <p class="mb-2"><strong>Status:</strong> 
                                    <span class="badge {% if maintenance.status == 'scheduled' %}bg-primary{% elif maintenance.status == 'in_progress' %}bg-warning text-dark{% elif maintenance.status == 'completed' %}bg-success{% else %}bg-danger{% endif %}">
                                        {{ maintenance.get_status_display }}
                                    </span>
                                </p>
                                <p class="mb-2"><strong>Scheduled Date:</strong> {{ maintenance.scheduled_date|date:"F d, Y" }}</p>
                                {% if maintenance.completion_date %}
                                <p class="mb-2"><strong>Completion Date:</strong> {{ maintenance.completion_date|date:"F d, Y" }}</p>
                                {% endif %}
                                <p class="mb-2"><strong>Cost:</strong> ${{ maintenance.cost }}</p>
                                {% if maintenance.performed_by %}
                                <p class="mb-2"><strong>Performed By:</strong> {{ maintenance.performed_by }}</p>
                                {% endif %}
                            </div>
                            <div class="col-md-6">
                                <h5 class="mb-3">Car Information</h5>
                                <p class="mb-2"><strong>Car:</strong> 
                                    <a href="{% url 'car_detail' maintenance.car.id %}">
                                        {{ maintenance.car.make }} {{ maintenance.car.model }} ({{ maintenance.car.year }})
                                    </a>
                                </p>
                                <p class="mb-2"><strong>Category:</strong> {{ maintenance.car.get_category_display }}</p>
                                <p class="mb-2"><strong>Daily Rate:</strong> ${{ maintenance.car.daily_rate }}</p>
                                <p class="mb-2"><strong>Current Status:</strong> 
                                    {% if maintenance.car.is_available %}
                                    <span class="badge bg-success">Available</span>
                                    {% else %}
                                    <span class="badge bg-danger">Not Available</span>
                                    {% endif %}
                                </p>
                            </div>
                        </div>
                        
                        <h5 class="border-top pt-3 mb-3">Description</h5>
                        <div class="p-3 bg-light rounded mb-4">
                            <p class="mb-0">{{ maintenance.description|linebreaks }}</p>
                        </div>
                        
                        {% if maintenance.notes %}
                        <h5 class="mb-3">Notes</h5>
                        <div class="p-3 bg-light rounded">
                            <p class="mb-0">{{ maintenance.notes|linebreaks }}</p>
                        </div>
                        {% endif %}
                        
                        <div class="text-muted mt-4">
                            <small>
                                Created: {{ maintenance.created_at|date:"F d, Y H:i" }}<br>
                                Last Updated: {{ maintenance.updated_at|date:"F d, Y H:i" }}
                            </small>
                        </div>
                    </div>
                    <div class="card-footer bg-light">
                        <div class="d-flex justify-content-between">
                            <a href="{% url 'maintenance_list' %}" class="btn btn-outline-secondary">
                                <i class="fas fa-arrow-left me-1"></i> Back to List
                            </a>
                            <a href="{% url 'car_detail' maintenance.car.id %}" class="btn btn-outline-primary">
                                <i class="fas fa-car me-1"></i> View Car
                            </a>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="col-md-4">
                <!-- 相关维护记录 -->
                <div class="card shadow mb-4">
                    <div class="card-header bg-light">
                        <h5 class="mb-0">Related Maintenance</h5>
                    </div>
                    <div class="card-body p-0">
                        {% with related_records=maintenance.car.maintenance_records.all|dictsortreversed:"scheduled_date" %}
                        {% if related_records.count > 1 %}
                        <div class="list-group list-group-flush">
                            {% for record in related_records %}
                            {% if record.id != maintenance.id %}
                            <a href="{% url 'maintenance_detail' record.id %}" class="list-group-item list-group-item-action d-flex justify-content-between align-items-center">
                                <div>
                                    <h6 class="mb-1">{{ record.maintenance_type }}</h6>
                                    <small class="text-muted">{{ record.scheduled_date|date:"M d, Y" }}</small>
                                </div>
                                <span class="badge {% if record.status == 'scheduled' %}bg-primary{% elif record.status == 'in_progress' %}bg-warning text-dark{% elif record.status == 'completed' %}bg-success{% else %}bg-danger{% endif %}">
                                    {{ record.get_status_display }}
                                </span>
                            </a>
                            {% if forloop.counter == 5 %}
                            {% comment %}只显示最多5条相关记录{% endcomment %}
                            {% break %}
                            {% endif %}
                            {% endif %}
                            {% endfor %}
                        </div>
                        {% if related_records.count > 6 %}
                        <div class="text-center py-2">
                            <a href="{% url 'maintenance_list' %}?car_id={{ maintenance.car.id }}" class="btn btn-sm btn-outline-secondary">
                                View All ({{ related_records.count|add:"-1" }})
                            </a>
                        </div>
                        {% endif %}
                        {% else %}
                        <div class="text-center py-4">
                            <p class="text-muted mb-0">No other maintenance records for this car.</p>
                        </div>
                        {% endif %}
                        {% endwith %}
                    </div>
                </div>
                
                <!-- 快速操作 -->
                <div class="card shadow">
                    <div class="card-header bg-light">
                        <h5 class="mb-0">Quick Actions</h5>
                    </div>
                    <div class="card-body">
                        <div class="d-grid gap-2">
                            {% if maintenance.status == 'scheduled' %}
                            <button type="button" class="btn btn-warning" onclick="updateStatus('in_progress')">
                                <i class="fas fa-tools me-1"></i> Mark as In Progress
                            </button>
                            {% elif maintenance.status == 'in_progress' %}
                            <button type="button" class="btn btn-success" onclick="updateStatus('completed')">
                                <i class="fas fa-check me-1"></i> Mark as Completed
                            </button>
                            {% endif %}
                            
                            {% if maintenance.status != 'cancelled' and maintenance.status != 'completed' %}
                            <button type="button" class="btn btn-outline-danger" onclick="updateStatus('cancelled')">
                                <i class="fas fa-ban me-1"></i> Cancel Maintenance
                            </button>
                            {% endif %}
                            
                            {% if perms.cars.add_maintenance %}
                            <a href="{% url 'maintenance_create' %}?car_id={{ maintenance.car.id }}" class="btn btn-outline-primary">
                                <i class="fas fa-plus me-1"></i> Add New for This Car
                            </a>
                            {% endif %}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</section>

<!-- 状态更新表单 -->
<form id="status-update-form" method="post" action="{% url 'maintenance_update' maintenance.id %}" style="display: none;">
    {% csrf_token %}
    <input type="hidden" name="car" value="{{ maintenance.car.id }}">
    <input type="hidden" name="maintenance_type" value="{{ maintenance.maintenance_type }}">
    <input type="hidden" name="description" value="{{ maintenance.description }}">
    <input type="hidden" name="scheduled_date" value="{{ maintenance.scheduled_date|date:'Y-m-d' }}">
    <input type="hidden" name="cost" value="{{ maintenance.cost }}">
    <input type="hidden" name="performed_by" value="{{ maintenance.performed_by }}">
    <input type="hidden" name="notes" value="{{ maintenance.notes }}">
    <input type="hidden" name="status" id="status-field" value="{{ maintenance.status }}">
    {% if maintenance.completion_date %}
    <input type="hidden" name="completion_date" value="{{ maintenance.completion_date|date:'Y-m-d' }}">
    {% endif %}
</form>
{% endblock %}

{% block extra_js %}
<script>
function updateStatus(newStatus) {
    if (newStatus === 'completed') {
        // 如果标记为完成，自动填入今天的日期
        const today = new Date();
        const year = today.getFullYear();
        const month = String(today.getMonth() + 1).padStart(2, '0');
        const day = String(today.getDate()).padStart(2, '0');
        
        // 检查表单是否已有完成日期输入框
        let completionDateInput = document.querySelector('#status-update-form input[name="completion_date"]');
        
        if (!completionDateInput) {
            completionDateInput = document.createElement('input');
            completionDateInput.type = 'hidden';
            completionDateInput.name = 'completion_date';
            document.querySelector('#status-update-form').appendChild(completionDateInput);
        }
        
        completionDateInput.value = `${year}-${month}-${day}`;
    }
    
    document.querySelector('#status-field').value = newStatus;
    document.querySelector('#status-update-form').submit();
}
</script>
{% endblock %}
```

#### 删除确认模板 (maintenance_confirm_delete.html)
```html
{% extends 'base.html' %}

{% block title %}{{ title }} - Rush Car Rental{% endblock %}

{% block content %}
<!-- 面包屑导航 -->
<div class="breadcrumb-container py-2">
    <div class="container">
        <nav aria-label="breadcrumb">
            <ol class="breadcrumb breadcrumb-custom mb-0">
                <li class="breadcrumb-item">
                    <a href="{% url 'home' %}" class="breadcrumb-home">
                        <i class="fas fa-home"></i> Home
                    </a>
                </li>
                <li class="breadcrumb-item">
                    <a href="{% url 'maintenance_list' %}">
                        <i class="fas fa-tools"></i> Maintenance Records
                    </a>
                </li>
                <li class="breadcrumb-item">
                    <a href="{% url 'maintenance_detail' maintenance.id %}">
                        {{ maintenance.maintenance_type }}
                    </a>
                </li>
                <li class="breadcrumb-item active" aria-current="page">
                    Delete
                </li>
            </ol>
        </nav>
    </div>
</div>

<section class="py-5">
    <div class="container">
        <div class="row">
            <div class="col-md-6 mx-auto">
                <div class="card shadow">
                    <div class="card-header bg-danger text-white">
                        <h4 class="mb-0">Delete Maintenance Record</h4>
                    </div>
                    <div class="card-body">
                        <div class="text-center mb-4">
                            <i class="fas fa-exclamation-triangle fa-3x text-warning mb-3"></i>
                            <h5>Are you sure you want to delete this maintenance record?</h5>
                            <p class="text-muted">This action cannot be undone.</p>
                        </div>
                        
                        <div class="alert alert-secondary">
                            <h6 class="mb-2">Record Details:</h6>
                            <p class="mb-1"><strong>Car:</strong> {{ maintenance.car.make }} {{ maintenance.car.model }}</p>
                            <p class="mb-1"><strong>Maintenance Type:</strong> {{ maintenance.maintenance_type }}</p>
                            <p class="mb-1"><strong>Scheduled Date:</strong> {{ maintenance.scheduled_date|date:"F d, Y" }}</p>
                            <p class="mb-0"><strong>Status:</strong> {{ maintenance.get_status_display }}</p>
                        </div>
                        
                        <form method="post">
                            {% csrf_token %}
                            <div class="d-flex justify-content-between mt-4">
                                <a href="{% url 'maintenance_detail' maintenance.id %}" class="btn btn-outline-secondary">
                                    <i class="fas fa-arrow-left me-1"></i> Cancel
                                </a>
                                <button type="submit" class="btn btn-danger">
                                    <i class="fas fa-trash me-1"></i> Delete Record
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>
</section>
{% endblock %}
```

### 6. JavaScript 增强功能 (可选)

为了增强用户体验，可以添加一些 JavaScript 功能：

- AJAX 筛选和分页
- 表单动态验证
- 拖放排序等

### 7. 模型和表单的验证和测试

编写单元测试来验证模型和表单的功能：

```python
# cars/tests.py
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from .models import Car, Maintenance
from .forms import MaintenanceForm
from datetime import date, timedelta

class MaintenanceModelTest(TestCase):
    def setUp(self):
        self.car = Car.objects.create(
            make="Toyota",
            model="Camry",
            year=2022,
            category="comfort",
            daily_rate=70.00,
            is_available=True
        )
        
    def test_maintenance_creation(self):
        maintenance = Maintenance.objects.create(
            car=self.car,
            maintenance_type="Oil Change",
            description="Regular oil change and filter replacement",
            scheduled_date=date.today(),
            status="scheduled",
            cost=45.00
        )
        self.assertEqual(maintenance.car, self.car)
        self.assertEqual(maintenance.status, "scheduled")
        self.assertEqual(str(maintenance), f"Toyota Camry - Oil Change ({date.today()})")

class MaintenanceFormTest(TestCase):
    def setUp(self):
        self.car = Car.objects.create(
            make="Toyota",
            model="Camry",
            year=2022,
            category="comfort",
            daily_rate=70.00,
            is_available=True
        )
        
    def test_valid_form(self):
        form_data = {
            'car': self.car.id,
            'maintenance_type': "Brake Replacement",
            'description': "Replace front brake pads",
            'scheduled_date': date.today(),
            'status': "scheduled",
            'cost': 250.00
        }
        form = MaintenanceForm(data=form_data)
        self.assertTrue(form.is_valid())
        
    def test_invalid_completion_date(self):
        # 测试完成日期早于计划日期的情况
        form_data = {
            'car': self.car.id,
            'maintenance_type': "Brake Replacement",
            'description': "Replace front brake pads",
            'scheduled_date': date.today(),
            'completion_date': date.today() - timedelta(days=2),
            'status': "completed",
            'cost': 250.00
        }
        form = MaintenanceForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('Completion date cannot be earlier than scheduled date', str(form.errors))

class MaintenanceViewsTest(TestCase):
    def setUp(self):
        # 创建测试用户和权限
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')
        
        # 为用户添加必要的权限
        content_type = ContentType.objects.get_for_model(Maintenance)
        permissions = Permission.objects.filter(content_type=content_type)
        for perm in permissions:
            self.user.user_permissions.add(perm)
        
        # 创建测试数据
        self.car = Car.objects.create(
            make="Toyota",
            model="Camry",
            year=2022,
            category="comfort",
            daily_rate=70.00,
            is_available=True
        )
        
        self.maintenance = Maintenance.objects.create(
            car=self.car,
            maintenance_type="Oil Change",
            description="Regular oil change and filter replacement",
            scheduled_date=date.today(),
            status="scheduled",
            cost=45.00
        )
        
    def test_maintenance_list_view(self):
        response = self.client.get(reverse('maintenance_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Oil Change")
        self.assertContains(response, "Toyota Camry")
        
    def test_maintenance_detail_view(self):
        response = self.client.get(reverse('maintenance_detail', args=[self.maintenance.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Oil Change")
        self.assertContains(response, "Regular oil change and filter replacement")
        
    def test_maintenance_create_view(self):
        # 测试 GET 请求
        response = self.client.get(reverse('maintenance_create'))
        self.assertEqual(response.status_code, 200)
        
        # 测试有效的 POST 请求
        post_data = {
            'car': self.car.id,
            'maintenance_type': "Tire Rotation",
            'description': "Rotate tires for even wear",
            'scheduled_date': date.today().strftime('%Y-%m-%d'),
            'status': "scheduled",
            'cost': 30.00
        }
        response = self.client.post(reverse('maintenance_create'), post_data)
        # 测试重定向（成功创建后）
        self.assertEqual(response.status_code, 302)
        # 确认记录已创建
        self.assertTrue(Maintenance.objects.filter(maintenance_type="Tire Rotation").exists())
        
    def test_maintenance_update_view(self):
        # 测试 GET 请求
        response = self.client.get(reverse('maintenance_update', args=[self.maintenance.id]))
        self.assertEqual(response.status_code, 200)
        
        # 测试有效的 POST 请求
        post_data = {
            'car': self.car.id,
            'maintenance_type': "Oil Change",
            'description': "Updated description",
            'scheduled_date': date.today().strftime('%Y-%m-%d'),
            'status': "in_progress",
            'cost': 50.00  # 更新价格
        }
        response = self.client.post(reverse('maintenance_update', args=[self.maintenance.id]), post_data)
        # 测试重定向（成功更新后）
        self.assertEqual(response.status_code, 302)
        
        # 重新加载记录并验证更新
        self.maintenance.refresh_from_db()
        self.assertEqual(self.maintenance.status, "in_progress")
        self.assertEqual(self.maintenance.cost, 50.00)
        
    def test_maintenance_delete_view(self):
        # 测试 GET 请求（确认页面）
        response = self.client.get(reverse('maintenance_delete', args=[self.maintenance.id]))
        self.assertEqual(response.status_code, 200)
        
        # 测试 POST 请求（确认删除）
        response = self.client.post(reverse('maintenance_delete', args=[self.maintenance.id]))
        self.assertEqual(response.status_code, 302)  # 重定向
        
        # 确认记录已删除
        self.assertFalse(Maintenance.objects.filter(id=self.maintenance.id).exists())
```

## 三、扩展功能实现指南

在 Rush Car Rental 项目中，除了基本的 CRUD 操作外，还可以实现以下扩展功能：

### 1. 高级搜索和筛选

实现更复杂的搜索和筛选功能，如日期范围筛选、多条件组合筛选等。

### 2. 导入/导出功能

添加数据导入/导出功能，支持 CSV/Excel 格式。

### 3. 数据可视化

使用图表和仪表板展示数据分析结果，如维护成本趋势、车辆可用性统计等。

### 4. 批量操作

实现批量编辑、批量删除等功能，提高管理效率。

### 5. API 开发

开发 RESTful API，允许其他系统集成和访问数据。

## 四、最佳实践

在 Rush Car Rental 项目中实施 CRUD 功能时，请遵循以下最佳实践：

### 1. 代码组织

- 保持视图函数简洁，复杂逻辑移至服务层或辅助函数
- 遵循 DRY（Don't Repeat Yourself）原则，减少代码重复
- 使用模板继承减少 HTML 重复

### 2. 安全实践

- 始终验证用户权限
- 防止 CSRF 攻击
- 避免 SQL 注入
- 输入验证和数据清洗

### 3. 用户体验

- 提供清晰的成功/错误消息
- 合理使用分页和延迟加载
- 响应式设计适配不同设备
- 保持 UI 一致性

### 4. 性能优化

- 使用 Django ORM 的 select_related 和 prefetch_related 减少数据库查询
- 缓存频繁访问的数据
- 优化图片和静态资源

### 5. 测试和部署

- 为所有功能编写单元测试和集成测试
- 使用持续集成保证代码质量
- 阶段性部署，避免大规模更改

## 五、总结

Rush Car Rental 项目采用了模块化、渐进式的开发模式，结合了后端渲染和前端增强的混合架构。在实现新的 CRUD 功能时，应该遵循项目现有的设计模式和代码风格，确保新功能与现有系统无缝集成。

通过遵循本文档中的开发指南和最佳实践，可以高效地实现高质量的 CRUD 功能，同时保持代码的可维护性和可扩展性。