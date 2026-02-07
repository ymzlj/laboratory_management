"""
设备管理模块URL配置
"""
from django.urls import path
from . import views

app_name = 'equipment'

urlpatterns = [
    # 设备管理首页
    path('', views.equipment_index, name='index'),
    
    # 设备管理
    path('list/', views.equipment_list, name='list'),
    path('create/', views.equipment_create, name='create'),
    path('<int:pk>/', views.equipment_detail, name='detail'),
    path('<int:pk>/edit/', views.equipment_edit, name='edit'),
    path('<int:pk>/delete/', views.equipment_delete, name='delete'),
    path('bulk-delete/', views.equipment_bulk_delete, name='bulk_delete'),
    
    # 设备使用记录
    path('usage-records/', views.usage_record_list, name='usage_record_list'),
    path('usage-records/create/', views.usage_record_create, name='usage_record_create'),
    path('usage-records/<int:pk>/', views.usage_record_detail, name='usage_record_detail'),
    path('usage-records/<int:pk>/edit/', views.usage_record_edit, name='usage_record_edit'),
    
    # 设备维护记录
    path('maintenance-records/', views.maintenance_record_list, name='maintenance_record_list'),
    path('maintenance-records/create/', views.maintenance_record_create, name='maintenance_record_create'),
    path('maintenance-records/<int:pk>/', views.maintenance_record_detail, name='maintenance_record_detail'),
    path('maintenance-records/<int:pk>/edit/', views.maintenance_record_edit, name='maintenance_record_edit'),
    
    # 统计报表
    path('statistics/', views.equipment_statistics, name='statistics'),
]