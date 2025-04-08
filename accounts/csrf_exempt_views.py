"""
为账户相关视图提供CSRF豁免装饰器
"""
from django.views.decorators.csrf import csrf_exempt

# 登录视图的CSRF豁免装饰器
def csrf_exempt_login(view_func):
    """
    为登录视图提供CSRF豁免
    这是必要的因为有时在Replit环境中CSRF验证会失败
    """
    return csrf_exempt(view_func)
