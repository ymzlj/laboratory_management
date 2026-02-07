import os
from celery import Celery

# 设置 Django 的 settings 模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'laboratory_management.settings')

app = Celery('laboratory_management')

# 使用 Django 的 settings 文件配置 Celery
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自动发现任务模块
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
