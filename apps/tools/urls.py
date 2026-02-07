from django.urls import path
from . import views

app_name = 'tools'

urlpatterns = [
    # 工具列表
    path('', views.tool_list, name='list'),
    
    # 新增工具
    path('create/', views.tool_create, name='create'),
    
    # 工具详情
    path('<int:pk>/', views.tool_detail, name='detail'),
    
    # 编辑工具
    path('<int:pk>/edit/', views.tool_edit, name='edit'),
    
    # 删除工具
    path('<int:pk>/delete/', views.tool_delete, name='delete'),
    
    # 批量删除
    path('bulk-delete/', views.tool_bulk_delete, name='bulk_delete'),
]
