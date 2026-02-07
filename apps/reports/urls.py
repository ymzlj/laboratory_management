from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    # 添加一个默认的报表列表URL，以解决NoReverseMatch错误
    path('', views.report_list, name='report_list'),
]