"""
试验任务管理URL配置
"""
from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    # 任务列表和仪表板
    path('', views.task_list, name='task_list'),
    path('dashboard/', views.task_dashboard, name='dashboard'),
    path('my-tasks/', views.my_tasks, name='my_tasks'),
    
    # 任务CRUD操作
    path('create/', views.task_create, name='task_create'),
    path('<int:task_id>/', views.task_detail, name='task_detail'),
    path('<int:task_id>/edit/', views.task_edit, name='task_edit'),
    path('<int:task_id>/delete/', views.task_delete, name='task_delete'),
    
    # 任务管理操作
    path('<int:task_id>/assign/', views.task_assign, name='task_assign'),
    path('<int:task_id>/status-update/', views.task_status_update, name='task_status_update'),
    path('<int:task_id>/process/update/', views.task_process_update, name='task_process_update'),
    path('<int:task_id>/process/history/', views.task_process_history, name='task_process_history'),
    
    # 试验任务报告管理
    path('<int:task_id>/report/upload/', views.task_report_upload, name='task_report_upload'),
    path('report/<int:report_id>/delete/', views.task_report_delete, name='task_report_delete'),
    
    # 试验类型管理
    path('test-types/', views.test_type_list, name='test_type_list'),
    path('test-types/create/', views.test_type_create, name='test_type_create'),
    path('test-types/<int:pk>/', views.test_type_detail, name='test_type_detail'),
    path('test-types/<int:pk>/update/', views.test_type_update, name='test_type_update'),
    path('test-types/<int:pk>/delete/', views.test_type_delete, name='test_type_delete'),
    path('api/test-types/sub-types/', views.get_sub_test_types, name='get_sub_test_types'), # New API
    
    # 试验类型字段配置
    path('test-types/<int:test_type_id>/fields/create/', views.test_type_field_create, name='test_type_field_create'),
    path('test-type-fields/<int:field_id>/edit/', views.test_type_field_edit, name='test_type_field_edit'),
    path('test-type-fields/<int:field_id>/delete/', views.test_type_field_delete, name='test_type_field_delete'),
    path('test-type-fields/<int:field_id>/image/delete/', views.test_type_field_image_delete, name='test_type_field_image_delete'),
    
    # 子任务管理
    path('<int:task_id>/decompose/', views.task_decompose, name='task_decompose'),
    path('subtask/<int:subtask_id>/', views.subtask_detail, name='subtask_detail'),
    path('subtask/<int:subtask_id>/data/edit/', views.subtask_data_edit, name='subtask_data_edit'),
    path('subtask/<int:subtask_id>/delete/', views.subtask_delete, name='subtask_delete'),
    
    # 通用批量试验数据管理（适用于所有试验类型）
    path('subtask/<int:subtask_id>/generic-data/entry/', views.generic_test_data_entry, name='generic_test_data_entry'),
    path('subtask/<int:subtask_id>/generic-data/list/', views.generic_test_data_list, name='generic_test_data_list'),
    path('generic-data/<int:data_id>/delete/', views.generic_test_data_delete, name='generic_test_data_delete'),
    path('subtask/<int:subtask_id>/generic-data/template/download/', views.download_generic_test_template, name='download_generic_test_template'),
    
    # 试验数据管理
    path('test-data/', views.test_data_list, name='test_data_list'),
    path('test-data/search/', views.test_data_search, name='test_data_search'),
    path('test-data/<int:data_id>/edit/', views.test_data_edit, name='test_data_edit'),
    path('test-data/<int:data_id>/delete/', views.test_data_delete, name='test_data_delete'),
]
