from django.apps import AppConfig


class DevConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dev'
    verbose_name = '开发工具'