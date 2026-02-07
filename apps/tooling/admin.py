from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone

from .models import Tooling, ToolingUsageRecord, ToolingMaintenance


@admin.register(Tooling)
class ToolingAdmin(admin.ModelAdmin):
    """工装管理"""
    list_display = [
        'tooling_id', 'name', 'model', 'manufacturer', 'status_badge',
        'location', 'responsible_person', 'maintenance_status', 'created_at'
    ]
    list_filter = [
        'status', 'manufacturer', 'location', 'responsible_person',
        'created_at', 'updated_at'
    ]
    search_fields = [
        'tooling_id', 'name', 'model', 'manufacturer', 'location'
    ]
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': (
                'tooling_id', 'name', 'model', 'manufacturer', 'status',
                'location', 'responsible_person'
            )
        }),
        ('采购信息', {
            'fields': (
                'purchase_date', 'purchase_price', 'type'
            ),
            'classes': ('collapse',)
        }),
        ('技术规格', {
            'fields': (
                'specifications', 'material', 'dimensions', 'weight', 'max_load',
                'operating_temperature_min', 'operating_temperature_max'
            ),
            'classes': ('collapse',)
        }),
        ('维护信息', {
            'fields': (
                'last_maintenance_date', 'maintenance_interval',
                'next_maintenance_date'
            ),
            'classes': ('collapse',)
        }),
        ('其他信息', {
            'fields': ('remarks', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        """状态徽章"""
        colors = {
            'available': 'success',
            'in_use': 'warning',
            'maintenance': 'danger',
            'retired': 'secondary'
        }
        color = colors.get(obj.status, 'secondary')
        return format_html(
            '<span class="badge badge-{}">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = '状态'
    
    def maintenance_status(self, obj):
        """维护状态"""
        if obj.is_maintenance_due():
            return format_html(
                '<span class="badge badge-danger">需要维护</span>'
            )
        elif obj.next_maintenance_date:
            days_left = (obj.next_maintenance_date - timezone.now().date()).days
            if days_left <= 7:
                return format_html(
                    '<span class="badge badge-warning">{}天后维护</span>',
                    days_left
                )
            else:
                return format_html(
                    '<span class="badge badge-success">正常</span>'
                )
        return format_html('<span class="badge badge-secondary">未设置</span>')
    maintenance_status.short_description = '维护状态'
    
    actions = ['mark_as_available', 'mark_as_maintenance', 'export_selected']
    
    def mark_as_available(self, request, queryset):
        """标记为可用"""
        updated = queryset.update(status='available')
        self.message_user(request, f'已将 {updated} 个工装标记为可用。')
    mark_as_available.short_description = '标记为可用'
    
    def mark_as_maintenance(self, request, queryset):
        """标记为维护中"""
        updated = queryset.update(status='maintenance')
        self.message_user(request, f'已将 {updated} 个工装标记为维护中。')
    mark_as_maintenance.short_description = '标记为维护中'


@admin.register(ToolingUsageRecord)
class ToolingUsageRecordAdmin(admin.ModelAdmin):
    """工装使用记录管理"""
    list_display = [
        'tooling', 'user', 'test_task', 'start_time', 'end_time',
        'duration_display', 'tooling_condition', 'created_at'
    ]
    list_filter = [
        'tooling', 'user', 'test_task', 'tooling_condition',
        'start_time', 'created_at'
    ]
    search_fields = [
        'tooling__name', 'tooling__tooling_id', 'user__username',
        'test_task__name', 'usage_purpose'
    ]
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': (
                'tooling', 'user', 'task', 'purpose'
            )
        }),
        ('使用时间', {
            'fields': (
                'start_time', 'end_time', 'duration_hours'
            )
        }),
        ('使用详情', {
            'fields': (
                'usage_instructions', 'load_applied', 'temperature',
                'status_after_use'
            ),
            'classes': ('collapse',)
        }),
        ('系统信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def duration_display(self, obj):
        """使用时长显示"""
        if obj.duration_hours:
            return f'{obj.duration_hours:.1f}小时'
        elif obj.end_time is None:
            return format_html('<span class="badge badge-warning">使用中</span>')
        return '-'
    duration_display.short_description = '使用时长'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'tooling', 'user', 'task'
        )


@admin.register(ToolingMaintenance)
class ToolingMaintenanceAdmin(admin.ModelAdmin):
    """工装维护记录管理"""
    list_display = [
        'tooling', 'maintenance_type_badge', 'maintenance_date',
        'maintenance_person', 'maintenance_result_badge', 'maintenance_cost',
        'calibration_status', 'created_at'
    ]
    list_filter = [
        'maintenance_type', 'maintenance_result', 'maintenance_person',
        'maintenance_date', 'created_at'
    ]
    search_fields = [
        'tooling__name', 'tooling__tooling_id', 'maintenance_person__username',
        'maintenance_content', 'calibration_certificate'
    ]
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': (
                'tooling', 'maintenance_person', 'maintenance_type', 'maintenance_date'
            )
        }),
        ('维护详情', {
            'fields': (
                'maintenance_content', 'replaced_parts', 'maintenance_cost'
            )
        }),
        ('维护结果', {
            'fields': (
                'maintenance_result', 'next_maintenance_date'
            )
        }),
        ('校准信息', {
            'fields': (
                'calibration_certificate', 'calibration_due_date'
            ),
            'classes': ('collapse',)
        }),
        ('其他信息', {
            'fields': ('notes', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def maintenance_type_badge(self, obj):
        """维护类型徽章"""
        colors = {
            'routine': 'info',
            'preventive': 'success',
            'corrective': 'warning',
            'calibration': 'primary'
        }
        color = colors.get(obj.maintenance_type, 'secondary')
        return format_html(
            '<span class="badge badge-{}">{}</span>',
            color,
            obj.get_maintenance_type_display()
        )
    maintenance_type_badge.short_description = '维护类型'
    
    def maintenance_result_badge(self, obj):
        """维护结果徽章"""
        colors = {
            'completed': 'success',
            'pending': 'warning',
            'failed': 'danger'
        }
        color = colors.get(obj.maintenance_result, 'secondary')
        return format_html(
            '<span class="badge badge-{}">{}</span>',
            color,
            obj.get_maintenance_result_display()
        )
    maintenance_result_badge.short_description = '维护结果'
    
    def calibration_status(self, obj):
        """校准状态"""
        if obj.maintenance_type == 'calibration' and obj.calibration_due_date:
            today = timezone.now().date()
            if obj.calibration_due_date < today:
                return format_html(
                    '<span class="badge badge-danger">已过期</span>'
                )
            elif (obj.calibration_due_date - today).days <= 30:
                return format_html(
                    '<span class="badge badge-warning">即将过期</span>'
                )
            else:
                return format_html(
                    '<span class="badge badge-success">有效</span>'
                )
        return '-'
    calibration_status.short_description = '校准状态'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'tooling', 'maintenance_person'
        )
    
    actions = ['mark_as_completed', 'mark_as_pending']
    
    def mark_as_completed(self, request, queryset):
        """标记为已完成"""
        updated = queryset.update(maintenance_result='completed')
        self.message_user(request, f'已将 {updated} 条维护记录标记为已完成。')
    mark_as_completed.short_description = '标记为已完成'
    
    def mark_as_pending(self, request, queryset):
        """标记为待完成"""
        updated = queryset.update(maintenance_result='pending')
        self.message_user(request, f'已将 {updated} 条维护记录标记为待完成。')
    mark_as_pending.short_description = '标记为待完成'


# 自定义管理站点标题
admin.site.site_header = '试验室管理系统 - 工装管理'
admin.site.site_title = '工装管理'
admin.site.index_title = '工装管理控制台'