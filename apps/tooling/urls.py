from django.urls import path
from . import views

app_name = 'tooling'

urlpatterns = [
    # 工装管理首页
    path('', views.ToolingIndexView.as_view(), name='index'),
    
    # 工装管理
    path('list/', views.ToolingListView.as_view(), name='list'),
    path('create/', views.ToolingCreateView.as_view(), name='create'),
    path('<int:pk>/', views.ToolingDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.ToolingUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.ToolingDeleteView.as_view(), name='delete'),
    path('export/', views.ToolingExportView.as_view(), name='export'),
    
    # 工装使用记录
    path('usage-records/', views.UsageRecordListView.as_view(), name='usage_record_list'),
    path('usage-records/create/', views.UsageRecordCreateView.as_view(), name='usage_record_create'),
    path('usage-records/<int:pk>/', views.UsageRecordDetailView.as_view(), name='usage_record_detail'),
    path('usage-records/<int:pk>/edit/', views.UsageRecordUpdateView.as_view(), name='usage_record_edit'),
    path('usage-records/<int:pk>/delete/', views.UsageRecordDeleteView.as_view(), name='usage_record_delete'),
    path('usage-records/export/', views.UsageRecordExportView.as_view(), name='usage_record_export'),
    
    # 工装维护记录
    path('maintenance-records/', views.MaintenanceRecordListView.as_view(), name='maintenance_record_list'),
    path('maintenance-records/create/', views.MaintenanceRecordCreateView.as_view(), name='maintenance_record_create'),
    path('maintenance-records/<int:pk>/', views.MaintenanceRecordDetailView.as_view(), name='maintenance_record_detail'),
    path('maintenance-records/<int:pk>/edit/', views.MaintenanceRecordUpdateView.as_view(), name='maintenance_record_edit'),
    path('maintenance-records/<int:pk>/delete/', views.MaintenanceRecordDeleteView.as_view(), name='maintenance_record_delete'),
    path('maintenance-records/export/', views.MaintenanceRecordExportView.as_view(), name='maintenance_record_export'),
    
    # AJAX接口
    path('ajax/tooling-info/<int:tooling_id>/', views.get_tooling_info, name='ajax_tooling_info'),
    path('ajax/calculate-usage-duration/', views.calculate_usage_duration, name='ajax_calculate_usage_duration'),
    path('ajax/suggest-next-maintenance/', views.suggest_next_maintenance, name='ajax_suggest_next_maintenance'),
]