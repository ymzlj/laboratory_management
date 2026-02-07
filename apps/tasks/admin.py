"""
试验任务管理后台配置
"""
from django.contrib import admin
from .models import TestType, TestTypeField, PriorityType, TaskStatus, TestTask


@admin.register(TestType)
class TestTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'description', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'code']
    ordering = ['code']


@admin.register(PriorityType)
class PriorityTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'level', 'description', 'created_at']
    list_filter = ['level', 'created_at']
    search_fields = ['name']
    ordering = ['level']


@admin.register(TaskStatus)
class TaskStatusAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'description', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'code']
    ordering = ['code']


@admin.register(TestTask)
class TestTaskAdmin(admin.ModelAdmin):
    list_display = [
        'task_number', 'task_name', 'test_type', 'priority', 
        'status', 'requester', 'assignee', 'start_date', 'end_date'
    ]
    list_filter = [
        'test_type', 'priority', 'status', 'start_date', 'end_date', 'created_at'
    ]
    search_fields = ['task_number', 'task_name', 'description']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': (
                'task_number', 'task_name', 'test_type', 
                'priority', 'status', 'description'
            )
        }),
        ('人员分配', {
            'fields': ('requester', 'assignee')
        }),
        ('时间安排', {
            'fields': (
                'start_date', 'end_date', 
                'actual_start_date', 'actual_end_date'
            )
        }),
        ('试验大纲', {
            'fields': ('test_outline', 'test_outline_file'),
            'classes': ('collapse',)
        }),
        ('试验报告', {
            'fields': ('test_report', 'test_report_file'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # 编辑现有对象
            return self.readonly_fields + ['task_number']
        return self.readonly_fields
