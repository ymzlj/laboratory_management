"""
试验数据模块URL配置
"""
from django.urls import path
from . import views

app_name = 'test_data'

urlpatterns = [
    # 试验数据首页
    path('', views.test_data_index, name='index'),
    
    # 试验数据统计
    path('statistics/', views.test_data_statistics, name='statistics'),
    
    # 试验数据列表
    path('<str:data_type>/', views.test_data_list, name='list'),
    
    # 创建试验数据
    path('<str:data_type>/create/', views.test_data_create, name='create'),
    
    # 试验数据详情
    path('<str:data_type>/<int:pk>/', views.test_data_detail, name='detail'),
    
    # 编辑试验数据
    path('<str:data_type>/<int:pk>/edit/', views.test_data_edit, name='edit'),
    
    # 删除试验数据
    path('<str:data_type>/<int:pk>/delete/', views.test_data_delete, name='delete'),
    
    # 批量删除试验数据
    path('<str:data_type>/bulk-delete/', views.test_data_bulk_delete, name='bulk_delete'),
]
