"""
Rush Car Rental 系统设置

根据环境变量 DJANGO_ENVIRONMENT 加载对应的设置文件:
- development: 开发环境 (默认)
- testing: 测试环境
- production: 生产环境
"""
import os
from pathlib import Path

# 获取环境类型
environment = os.environ.get('DJANGO_ENVIRONMENT', 'development')

# 根据环境类型导入不同的设置
if environment == 'production':
    from .production import *
elif environment == 'testing':
    from .testing import *
else:
    # 默认使用本地开发环境设置
    try:
        from .local import *
    except ImportError:
        from .development import *