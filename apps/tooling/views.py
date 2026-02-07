import csv
import json
from datetime import datetime, timedelta
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, Count, Sum, Avg
from django.utils import timezone
from django.core.paginator import Paginator
from django.forms import modelform_factory

from .models import Tooling, ToolingUsageRecord, ToolingMaintenance
from .forms import ToolingForm, ToolingUsageRecordForm, ToolingMaintenanceForm, ToolingSearchForm


class ToolingIndexView(LoginRequiredMixin, TemplateView):
    """工装管理首页"""
    template_name = 'tooling/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 工装统计
        tooling_stats = {
            'total': Tooling.objects.count(),
            'available': Tooling.objects.filter(status='available').count(),
            'in_use': Tooling.objects.filter(status='in_use').count(),
            'maintenance': Tooling.objects.filter(status='maintenance').count(),
        }
        
        # 维护和校准过期警告
        today = timezone.now().date()
        maintenance_due = Tooling.objects.filter(
            next_maintenance_date__lte=today
        ).count()
        
        calibration_overdue = ToolingMaintenance.objects.filter(
            maintenance_type='calibration',
            calibration_due_date__lt=today
        ).count()
        
        # 最近使用记录
        recent_usage = ToolingUsageRecord.objects.select_related(
            'tooling', 'user'
        ).order_by('-start_time')[:5]
        
        # 最近维护记录
        recent_maintenance = ToolingMaintenance.objects.select_related(
            'tooling', 'maintainer'
        ).order_by('-maintenance_date')[:5]
        
        context.update({
            'tooling_stats': tooling_stats,
            'maintenance_due': maintenance_due,
            'calibration_overdue': calibration_overdue,
            'recent_usage': recent_usage,
            'recent_maintenance': recent_maintenance,
        })
        
        return context


class ToolingListView(LoginRequiredMixin, ListView):
    """工装列表"""
    model = Tooling
    template_name = 'tooling/list.html'
    context_object_name = 'toolings'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Tooling.objects.all()
        self.form = ToolingSearchForm(self.request.GET)
        
        if self.form.is_valid():
            data = self.form.cleaned_data
            
            # 搜索
            search = data.get('search')
            if search:
                queryset = queryset.filter(
                    Q(name__icontains=search) |
                    Q(tooling_id__icontains=search) |
                    Q(model__icontains=search) |
                    Q(manufacturer__icontains=search)
                )
            
            # 状态筛选
            status = data.get('status')
            if status:
                queryset = queryset.filter(status=status)
            
            # 制造商筛选
            manufacturer = data.get('manufacturer')
            if manufacturer:
                queryset = queryset.filter(manufacturer__icontains=manufacturer)
            
            # 位置筛选
            location = data.get('location')
            if location:
                queryset = queryset.filter(location__icontains=location)
            
            # 负责人筛选
            responsible_person = data.get('responsible_person')
            if responsible_person:
                queryset = queryset.filter(responsible_person__username__icontains=responsible_person)
            
            # 需要维护筛选
            needs_maintenance = data.get('needs_maintenance')
            if needs_maintenance:
                today = timezone.now().date()
                queryset = queryset.filter(next_maintenance_date__lte=today)
            
            # 校准过期筛选
            calibration_overdue = data.get('calibration_overdue')
            if calibration_overdue:
                today = timezone.now().date()
                overdue_toolings = ToolingMaintenance.objects.filter(
                    maintenance_type='calibration',
                    calibration_due_date__lt=today
                ).values_list('tooling_id', flat=True)
                queryset = queryset.filter(id__in=overdue_toolings)
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form
        return context


class ToolingDetailView(LoginRequiredMixin, DetailView):
    """工装详情"""
    model = Tooling
    template_name = 'tooling/detail.html'
    context_object_name = 'tooling'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tooling = self.get_object()
        
        # 使用统计
        usage_stats = {
            'total_usage': ToolingUsageRecord.objects.filter(tooling=tooling).count(),
            'total_duration': ToolingUsageRecord.objects.filter(
                tooling=tooling,
                end_time__isnull=False
            ).aggregate(
                total=Sum('duration_hours')
            )['total'] or 0,
        }
        
        # 维护统计
        maintenance_stats = {
            'total_maintenance': ToolingMaintenance.objects.filter(tooling=tooling).count(),
            'completed_maintenance': ToolingMaintenance.objects.filter(
                tooling=tooling,
                maintenance_result='completed'
            ).count(),
            'total_cost': ToolingMaintenance.objects.filter(
                tooling=tooling
            ).aggregate(total=Sum('maintenance_cost'))['total'] or 0,
        }
        
        # 最近使用记录
        recent_usage = ToolingUsageRecord.objects.filter(
            tooling=tooling
        ).select_related('user').order_by('-start_time')[:5]
        
        # 最近维护记录
        recent_maintenance = ToolingMaintenance.objects.filter(
            tooling=tooling
        ).select_related('maintainer').order_by('-maintenance_date')[:5]
        
        context.update({
            'usage_stats': usage_stats,
            'maintenance_stats': maintenance_stats,
            'recent_usage': recent_usage,
            'recent_maintenance': recent_maintenance,
        })
        
        return context


class ToolingCreateView(LoginRequiredMixin, CreateView):
    """创建工装"""
    model = Tooling
    form_class = ToolingForm
    template_name = 'tooling/form.html'
    
    def form_valid(self, form):
        messages.success(self.request, '工装创建成功！')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('tooling:detail', kwargs={'pk': self.object.pk})


class ToolingUpdateView(LoginRequiredMixin, UpdateView):
    """编辑工装"""
    model = Tooling
    form_class = ToolingForm
    template_name = 'tooling/form.html'
    
    def form_valid(self, form):
        messages.success(self.request, '工装信息更新成功！')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('tooling:detail', kwargs={'pk': self.object.pk})


class ToolingDeleteView(LoginRequiredMixin, DeleteView):
    """删除工装"""
    model = Tooling
    success_url = reverse_lazy('tooling:list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, '工装删除成功！')
        return super().delete(request, *args, **kwargs)


class ToolingExportView(LoginRequiredMixin, ListView):
    """导出工装列表"""
    model = Tooling
    
    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="toolings.csv"'
        response.write('\ufeff')  # BOM for Excel
        
        writer = csv.writer(response)
        writer.writerow([
            '工装编号', '工装名称', '型号', '制造商', '状态', '位置',
            '负责人', '采购日期', '采购价格', '下次维护日期'
        ])
        
        for tooling in self.get_queryset():
            writer.writerow([
                tooling.tooling_id,
                tooling.name,
                tooling.model,
                tooling.manufacturer,
                tooling.get_status_display(),
                tooling.location,
                tooling.responsible_person.get_full_name() if tooling.responsible_person else '',
                tooling.purchase_date.strftime('%Y-%m-%d') if tooling.purchase_date else '',
                tooling.purchase_price or '',
                tooling.next_maintenance_date.strftime('%Y-%m-%d') if tooling.next_maintenance_date else '',
            ])
        
        return response


# 使用记录视图
class UsageRecordListView(LoginRequiredMixin, ListView):
    """使用记录列表"""
    model = ToolingUsageRecord
    template_name = 'tooling/usage_record_list.html'
    context_object_name = 'records'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = ToolingUsageRecord.objects.select_related(
            'tooling', 'user', 'task'
        ).all()
        
        # 搜索
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(tooling__name__icontains=search) |
                Q(tooling__tooling_id__icontains=search) |
                Q(user__username__icontains=search) |
                Q(purpose__icontains=search)
            )
        
        # 工装筛选
        tooling = self.request.GET.get('tooling')
        if tooling:
            queryset = queryset.filter(tooling_id=tooling)
        
        # 使用人筛选
        user = self.request.GET.get('user')
        if user:
            queryset = queryset.filter(user__username__icontains=user)
        
        # 关联任务筛选
        task = self.request.GET.get('task')
        if task:
            queryset = queryset.filter(task_id=task)
        
        # 使用后状态筛选
        status_after_use = self.request.GET.get('status_after_use')
        if status_after_use:
            queryset = queryset.filter(status_after_use=status_after_use)
        
        # 日期范围筛选
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        if start_date:
            queryset = queryset.filter(start_time__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(start_time__date__lte=end_date)
        
        # 仅显示使用中
        in_use_only = self.request.GET.get('in_use_only')
        if in_use_only:
            queryset = queryset.filter(end_time__isnull=True)
        
        return queryset.order_by('-start_time')


class UsageRecordDetailView(LoginRequiredMixin, DetailView):
    """使用记录详情"""
    model = ToolingUsageRecord
    template_name = 'tooling/usage_record_detail.html'
    context_object_name = 'record'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        record = self.get_object()
        
        # 该工装的其他使用记录
        other_records = ToolingUsageRecord.objects.filter(
            tooling=record.tooling
        ).exclude(id=record.id).select_related('user').order_by('-start_time')[:10]
        
        context['other_usage_records'] = other_records
        return context


class UsageRecordCreateView(LoginRequiredMixin, CreateView):
    """创建使用记录"""
    model = ToolingUsageRecord
    form_class = ToolingUsageRecordForm
    template_name = 'tooling/usage_record_form.html'
    
    def get_initial(self):
        initial = super().get_initial()
        initial['user'] = self.request.user
        initial['start_time'] = timezone.now()
        
        # 如果指定了工装ID
        tooling_id = self.request.GET.get('tooling')
        if tooling_id:
            initial['tooling'] = tooling_id
        
        return initial
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, '使用记录创建成功！')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('tooling:usage_record_detail', kwargs={'pk': self.object.pk})


class UsageRecordUpdateView(LoginRequiredMixin, UpdateView):
    """编辑使用记录"""
    model = ToolingUsageRecord
    form_class = ToolingUsageRecordForm
    template_name = 'tooling/usage_record_form.html'
    
    def form_valid(self, form):
        messages.success(self.request, '使用记录更新成功！')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('tooling:usage_record_detail', kwargs={'pk': self.object.pk})


class UsageRecordDeleteView(LoginRequiredMixin, DeleteView):
    """删除使用记录"""
    model = ToolingUsageRecord
    success_url = reverse_lazy('tooling:usage_record_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, '使用记录删除成功！')
        return super().delete(request, *args, **kwargs)


class UsageRecordExportView(LoginRequiredMixin, ListView):
    """导出使用记录"""
    model = ToolingUsageRecord
    
    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="usage_records.csv"'
        response.write('\ufeff')  # BOM for Excel
        
        writer = csv.writer(response)
        writer.writerow([
            '工装名称', '工装编号', '使用人', '开始时间', '结束时间',
            '使用时长(小时)', '使用目的', '关联任务', '使用后状态'
        ])
        
        for record in self.get_queryset():
            writer.writerow([
                record.tooling.name,
                record.tooling.tooling_id,
                record.user.get_full_name() or record.user.username,
                record.start_time.strftime('%Y-%m-%d %H:%M'),
                record.end_time.strftime('%Y-%m-%d %H:%M') if record.end_time else '使用中',
                record.duration_hours or '',
                record.purpose,
                record.task.name if record.task else '',
                record.get_status_after_use_display() if record.status_after_use else '',
            ])
        
        return response


# 维护记录视图
class MaintenanceRecordListView(LoginRequiredMixin, ListView):
    """维护记录列表"""
    model = ToolingMaintenance
    template_name = 'tooling/maintenance_record_list.html'
    context_object_name = 'records'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = ToolingMaintenance.objects.select_related(
            'tooling', 'maintainer'
        ).all()
        
        # 搜索
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(tooling__name__icontains=search) |
                Q(tooling__tooling_id__icontains=search) |
                Q(maintainer__username__icontains=search) |
                Q(maintenance_content__icontains=search)
            )
        
        # 工装筛选
        tooling = self.request.GET.get('tooling')
        if tooling:
            queryset = queryset.filter(tooling_id=tooling)
        
        # 维护类型筛选
        maintenance_type = self.request.GET.get('maintenance_type')
        if maintenance_type:
            queryset = queryset.filter(maintenance_type=maintenance_type)
        
        # 维护结果筛选
        maintenance_result = self.request.GET.get('maintenance_result')
        if maintenance_result:
            queryset = queryset.filter(maintenance_result=maintenance_result)
        
        # 维护人员筛选
        maintainer = self.request.GET.get('maintainer')
        if maintainer:
            queryset = queryset.filter(maintainer__username__icontains=maintainer)
        
        # 日期范围筛选
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        if start_date:
            queryset = queryset.filter(maintenance_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(maintenance_date__lte=end_date)
        
        # 仅显示校准过期
        calibration_overdue = self.request.GET.get('calibration_overdue')
        if calibration_overdue:
            today = timezone.now().date()
            queryset = queryset.filter(
                maintenance_type='calibration',
                calibration_due_date__lt=today
            )
        
        return queryset.order_by('-maintenance_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 统计信息
        stats = {
            'total': ToolingMaintenance.objects.count(),
            'completed': ToolingMaintenance.objects.filter(maintenance_result='completed').count(),
            'pending': ToolingMaintenance.objects.filter(maintenance_result='pending').count(),
            'calibration_overdue': ToolingMaintenance.objects.filter(
                maintenance_type='calibration',
                calibration_due_date__lt=timezone.now().date()
            ).count(),
        }
        
        context['stats'] = stats
        return context


class MaintenanceRecordDetailView(LoginRequiredMixin, DetailView):
    """维护记录详情"""
    model = ToolingMaintenance
    template_name = 'tooling/maintenance_record_detail.html'
    context_object_name = 'record'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        record = self.get_object()
        
        # 工装维护统计
        tooling_stats = {
            'total_maintenance': ToolingMaintenance.objects.filter(tooling=record.tooling).count(),
            'completed_maintenance': ToolingMaintenance.objects.filter(
                tooling=record.tooling,
                maintenance_result='completed'
            ).count(),
            'pending_maintenance': ToolingMaintenance.objects.filter(
                tooling=record.tooling,
                maintenance_result='pending'
            ).count(),
            'total_cost': ToolingMaintenance.objects.filter(
                tooling=record.tooling
            ).aggregate(total=Sum('maintenance_cost'))['total'] or 0,
        }
        
        # 该工装的其他维护记录
        other_records = ToolingMaintenance.objects.filter(
            tooling=record.tooling
        ).exclude(id=record.id).select_related('maintainer').order_by('-maintenance_date')[:10]
        
        context.update({
            'tooling_stats': tooling_stats,
            'other_maintenance_records': other_records,
            'today': timezone.now().date(),
        })
        
        return context


class MaintenanceRecordCreateView(LoginRequiredMixin, CreateView):
    """创建维护记录"""
    model = ToolingMaintenance
    form_class = ToolingMaintenanceForm
    template_name = 'tooling/maintenance_record_form.html'
    
    def get_initial(self):
        initial = super().get_initial()
        initial['maintainer'] = self.request.user
        initial['maintenance_date'] = timezone.now().date()
        
        # 如果指定了工装ID
        tooling_id = self.request.GET.get('tooling')
        if tooling_id:
            initial['tooling'] = tooling_id
        
        return initial
    
    def form_valid(self, form):
        form.instance.maintainer = self.request.user
        messages.success(self.request, '维护记录创建成功！')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('tooling:maintenance_record_detail', kwargs={'pk': self.object.pk})


class MaintenanceRecordUpdateView(LoginRequiredMixin, UpdateView):
    """编辑维护记录"""
    model = ToolingMaintenance
    form_class = ToolingMaintenanceForm
    template_name = 'tooling/maintenance_record_form.html'
    
    def form_valid(self, form):
        messages.success(self.request, '维护记录更新成功！')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('tooling:maintenance_record_detail', kwargs={'pk': self.object.pk})


class MaintenanceRecordDeleteView(LoginRequiredMixin, DeleteView):
    """删除维护记录"""
    model = ToolingMaintenance
    success_url = reverse_lazy('tooling:maintenance_record_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, '维护记录删除成功！')
        return super().delete(request, *args, **kwargs)


class MaintenanceRecordExportView(LoginRequiredMixin, ListView):
    """导出维护记录"""
    model = ToolingMaintenance
    
    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="maintenance_records.csv"'
        response.write('\ufeff')  # BOM for Excel
        
        writer = csv.writer(response)
        writer.writerow([
            '工装名称', '工装编号', '维护类型', '维护日期', '维护人员',
            '维护内容', '维护费用', '维护结果', '校准证书', '校准到期日期'
        ])
        
        for record in self.get_queryset():
            writer.writerow([
                record.tooling.name,
                record.tooling.tooling_id,
                record.get_maintenance_type_display(),
                record.maintenance_date.strftime('%Y-%m-%d'),
                record.maintainer.get_full_name() or record.maintainer.username,
                record.maintenance_content,
                record.maintenance_cost or '',
                record.get_maintenance_result_display(),
                record.calibration_certificate or '',
                record.calibration_due_date.strftime('%Y-%m-%d') if record.calibration_due_date else '',
            ])
        
        return response


# AJAX接口
@login_required
def get_tooling_info(request, tooling_id):
    """获取工装信息"""
    try:
        tooling = get_object_or_404(Tooling, id=tooling_id)
        data = {
            'id': tooling.id,
            'name': tooling.name,
            'tooling_id': tooling.tooling_id,
            'model': tooling.model,
            'manufacturer': tooling.manufacturer,
            'status': tooling.status,
            'status_display': tooling.get_status_display(),
            'location': tooling.location,
            'responsible_person': tooling.responsible_person.get_full_name() if tooling.responsible_person else '',
        }
        return JsonResponse({'success': True, 'data': data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def calculate_usage_duration(request):
    """计算使用时长"""
    try:
        start_time = request.GET.get('start_time')
        end_time = request.GET.get('end_time')
        
        if start_time and end_time:
            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            
            duration = end_dt - start_dt
            duration_hours = duration.total_seconds() / 3600
            
            return JsonResponse({
                'success': True,
                'duration_hours': round(duration_hours, 2)
            })
        
        return JsonResponse({'success': False, 'error': '缺少时间参数'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def suggest_next_maintenance(request):
    """建议下次维护日期"""
    try:
        maintenance_type = request.GET.get('maintenance_type')
        maintenance_result = request.GET.get('maintenance_result')
        
        if maintenance_result == 'completed':
            today = timezone.now().date()
            
            # 根据维护类型建议间隔
            intervals = {
                'routine': 30,      # 例行维护：30天
                'preventive': 90,   # 预防性维护：90天
                'corrective': 60,   # 纠正性维护：60天
                'calibration': 365, # 校准：365天
            }
            
            interval = intervals.get(maintenance_type, 90)
            next_date = today + timedelta(days=interval)
            
            return JsonResponse({
                'success': True,
                'next_maintenance_date': next_date.strftime('%Y-%m-%d')
            })
        
        return JsonResponse({'success': True, 'next_maintenance_date': ''})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})