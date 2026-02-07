from django.apps import AppConfig


class TestDataConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.test_data'
    verbose_name = '试验数据管理'