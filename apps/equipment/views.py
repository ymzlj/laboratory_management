"""
设备管理模块视图
"""
import csv
from datetime import datetime, timedelta
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Equipment, EquipmentUsageRecord, EquipmentMaintenance
from .forms import (
    EquipmentForm, EquipmentUsageRecordForm, EquipmentMaintenanceForm,
    EquipmentSearchForm, EquipmentUsageSearchForm, EquipmentMaintenanceSearchForm
)


@login_required
def equipment_index(request):
    """设备管理首页"""
    # 统计数据
    total_equipment = Equipment.objects.count()
    available_equipment = Equipment.objects.filter(status='available').count()
    in_use_equipment = Equipment.objects.filter(status='in_use').count()
    maintenance_equipment = Equipment.objects.filter(status='maintenance').count()
    
    # 需要维护的设备
    maintenance_due = Equipment.objects.filter(
        next_maintenance_date__lte=timezone.now().date()
    ).count()
    
    # 保修过期的设备
    warranty_expired = Equipment.objects.filter(
        warranty_end_date__lt=timezone.now().date()
    ).count()
    
    # 最近使用记录
    recent_usage = EquipmentUsageRecord.objects.select_related(
        'equipment', 'user'
    ).order_by('-start_time')[:10]
    
    # 最近维护记录
    recent_maintenance = EquipmentMaintenance.objects.select_related(
        'equipment', 'maintenance_person'
    ).order_by('-maintenance_date')[:10]
    
    context = {
        'total_equipment': total_equipment,
        'available_equipment': available_equipment,
        'in_use_equipment': in_use_equipment,
        'maintenance_equipment': maintenance_equipment,
        'maintenance_due': maintenance_due,
        'warranty_expired': warranty_expired,
        'recent_usage': recent_usage,
        'recent_maintenance': recent_maintenance,
    }
    
    return render(request, 'equipment/index.html', context)


@login_required
def equipment_list(request):
    """设备列表"""
    form = EquipmentSearchForm(request.GET)
    equipment_list = Equipment.objects.select_related('responsible_person').all()
    
    # 搜索过滤
    if form.is_valid():
        search = form.cleaned_data.get('search')
        if search:
            equipment_list = equipment_list.filter(
                Q(equipment_id__icontains=search) |
                Q(name__icontains=search) |
                Q(model__icontains=search) |
                Q(manufacturer__icontains=search)
            )
        
        status = form.cleaned_data.get('status')
        if status:
            equipment_list = equipment_list.filter(status=status)
        
        manufacturer = form.cleaned_data.get('manufacturer')
        if manufacturer:
            equipment_list = equipment_list.filter(manufacturer__icontains=manufacturer)
        
        location = form.cleaned_data.get('location')
        if location:
            equipment_list = equipment_list.filter(location__icontains=location)
        
        responsible_person = form.cleaned_data.get('responsible_person')
        if responsible_person:
            equipment_list = equipment_list.filter(responsible_person=responsible_person)
        
        maintenance_due = form.cleaned_data.get('maintenance_due')
        if maintenance_due:
            equipment_list = equipment_list.filter(
                next_maintenance_date__lte=timezone.now().date()
            )
        
        warranty_expired = form.cleaned_data.get('warranty_expired')
        if warranty_expired:
            equipment_list = equipment_list.filter(
                warranty_end_date__lt=timezone.now().date()
            )
    
    # 分页
    paginator = Paginator(equipment_list, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # 导出CSV
    if request.GET.get('export') == 'csv':
        return export_equipment_csv(equipment_list)
    
    context = {
        'form': form,
        'page_obj': page_obj,
        'equipment_list': page_obj.object_list,
    }
    
    return render(request, 'equipment/list.html', context)


@login_required
@permission_required('equipment.add_equipment', raise_exception=True)
def equipment_create(request):
    """创建设备"""
    if request.method == 'POST':
        form = EquipmentForm(request.POST, request.FILES)
        if form.is_valid():
            equipment = form.save()
            messages.success(request, f'设备 {equipment.name} 创建成功！')
            return redirect('equipment:detail', pk=equipment.pk)
    else:
        form = EquipmentForm()
    
    context = {
        'form': form,
        'title': '新增设备',
        'action': 'create',
    }
    
    return render(request, 'equipment/form.html', context)


@login_required
def equipment_detail(request, pk):
    """设备详情"""
    equipment = get_object_or_404(Equipment, pk=pk)
    
    # 使用记录
    usage_records = EquipmentUsageRecord.objects.filter(
        equipment=equipment
    ).select_related('user').order_by('-start_time')[:10]
    
    # 维护记录
    maintenance_records = EquipmentMaintenance.objects.filter(
        equipment=equipment
    ).select_related('maintenance_person').order_by('-maintenance_date')[:10]
    
    context = {
        'equipment': equipment,
        'usage_records': usage_records,
        'maintenance_records': maintenance_records,
    }
    
    return render(request, 'equipment/detail.html', context)


@login_required
@permission_required('equipment.change_equipment', raise_exception=True)
def equipment_edit(request, pk):
    """编辑设备"""
    equipment = get_object_or_404(Equipment, pk=pk)
    
    if request.method == 'POST':
        form = EquipmentForm(request.POST, request.FILES, instance=equipment)
        if form.is_valid():
            equipment = form.save()
            messages.success(request, f'设备 {equipment.name} 更新成功！')
            return redirect('equipment:detail', pk=equipment.pk)
    else:
        form = EquipmentForm(instance=equipment)
    
    context = {
        'form': form,
        'equipment': equipment,
        'title': '编辑设备',
        'action': 'edit',
    }
    
    return render(request, 'equipment/form.html', context)


@login_required
@permission_required('equipment.delete_equipment', raise_exception=True)
@require_POST
def equipment_delete(request, pk):
    """删除设备"""
    equipment = get_object_or_404(Equipment, pk=pk)
    equipment_name = equipment.name
    equipment.delete()
    messages.success(request, f'设备 {equipment_name} 删除成功！')
    return redirect('equipment:list')


@login_required
@permission_required('equipment.delete_equipment', raise_exception=True)
@require_POST
def equipment_bulk_delete(request):
    """批量删除设备"""
    equipment_ids = request.POST.getlist('equipment_ids')
    if equipment_ids:
        count = Equipment.objects.filter(id__in=equipment_ids).count()
        Equipment.objects.filter(id__in=equipment_ids).delete()
        messages.success(request, f'成功删除 {count} 个设备！')
    return redirect('equipment:list')


def export_equipment_csv(equipment_list):
    """导出设备CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="equipment_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    response.write('\ufeff')  # BOM for Excel
    
    writer = csv.writer(response)
    writer.writerow([
        '设备编号', '设备名称', '设备型号', '制造商', '序列号',
        '采购日期', '采购价格', '保修期(月)', '保修到期日期',
        '设备状态', '存放位置', '负责人', '技术规格',
        '上次维护日期', '下次维护日期', '维护间隔(天)', '备注'
    ])
    
    for equipment in equipment_list:
        writer.writerow([
            equipment.equipment_id,
            equipment.name,
            equipment.model,
            equipment.manufacturer,
            equipment.serial_number,
            equipment.purchase_date,
            equipment.purchase_price,
            equipment.warranty_period,
            equipment.warranty_end_date,
            equipment.get_status_display(),
            equipment.location,
            equipment.responsible_person.get_full_name() if equipment.responsible_person else '',
            equipment.specifications,
            equipment.last_maintenance_date or '',
            equipment.next_maintenance_date or '',
            equipment.maintenance_interval,
            equipment.remarks,
        ])
    
    return response


# 设备使用记录视图
@login_required
def usage_record_list(request):
    """设备使用记录列表"""
    form = EquipmentUsageSearchForm(request.GET)
    usage_list = EquipmentUsageRecord.objects.select_related(
        'equipment', 'user', 'test_task'
    ).all()
    
    # 搜索过滤
    if form.is_valid():
        search = form.cleaned_data.get('search')
        if search:
            usage_list = usage_list.filter(
                Q(equipment__name__icontains=search) |
                Q(user__username__icontains=search) |
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search) |
                Q(usage_purpose__icontains=search)
            )
        
        equipment = form.cleaned_data.get('equipment')
        if equipment:
            usage_list = usage_list.filter(equipment=equipment)
        
        user = form.cleaned_data.get('user')
        if user:
            usage_list = usage_list.filter(user=user)
        
        start_date = form.cleaned_data.get('start_date')
        if start_date:
            usage_list = usage_list.filter(start_time__date__gte=start_date)
        
        end_date = form.cleaned_data.get('end_date')
        if end_date:
            usage_list = usage_list.filter(start_time__date__lte=end_date)
        
        equipment_condition = form.cleaned_data.get('equipment_condition')
        if equipment_condition:
            usage_list = usage_list.filter(equipment_condition=equipment_condition)
    
    # 分页
    paginator = Paginator(usage_list, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # 导出CSV
    if request.GET.get('export') == 'csv':
        return export_usage_record_csv(usage_list)
    
    context = {
        'form': form,
        'page_obj': page_obj,
        'usage_list': page_obj.object_list,
    }
    
    return render(request, 'equipment/usage_record_list.html', context)


@login_required
@permission_required('equipment.add_equipmentusagerecord', raise_exception=True)
def usage_record_create(request):
    """创建设备使用记录"""
    if request.method == 'POST':
        form = EquipmentUsageRecordForm(request.POST)
        if form.is_valid():
            usage_record = form.save()
            # 更新设备状态为使用中
            equipment = usage_record.equipment
            if equipment.status == 'available':
                equipment.status = 'in_use'
                equipment.save()
            messages.success(request, '设备使用记录创建成功！')
            return redirect('equipment:usage_record_detail', pk=usage_record.pk)
    else:
        form = EquipmentUsageRecordForm()
        # 设置默认值
        form.fields['user'].initial = request.user
        form.fields['start_time'].initial = timezone.now()
    
    context = {
        'form': form,
        'title': '新增设备使用记录',
        'action': 'create',
    }
    
    return render(request, 'equipment/usage_record_form.html', context)


@login_required
def usage_record_detail(request, pk):
    """设备使用记录详情"""
    usage_record = get_object_or_404(
        EquipmentUsageRecord.objects.select_related('equipment', 'user', 'test_task'),
        pk=pk
    )
    
    context = {
        'usage_record': usage_record,
    }
    
    return render(request, 'equipment/usage_record_detail.html', context)


@login_required
@permission_required('equipment.change_equipmentusagerecord', raise_exception=True)
def usage_record_edit(request, pk):
    """编辑设备使用记录"""
    usage_record = get_object_or_404(EquipmentUsageRecord, pk=pk)
    
    if request.method == 'POST':
        form = EquipmentUsageRecordForm(request.POST, instance=usage_record)
        if form.is_valid():
            usage_record = form.save()
            # 如果设置了结束时间且设备状态异常，更新设备状态
            if usage_record.end_time and usage_record.equipment_condition != 'normal':
                equipment = usage_record.equipment
                if usage_record.equipment_condition == 'damaged':
                    equipment.status = 'repair'
                elif usage_record.equipment_condition == 'abnormal':
                    equipment.status = 'maintenance'
                equipment.save()
            messages.success(request, '设备使用记录更新成功！')
            return redirect('equipment:usage_record_detail', pk=usage_record.pk)
    else:
        form = EquipmentUsageRecordForm(instance=usage_record)
    
    context = {
        'form': form,
        'usage_record': usage_record,
        'title': '编辑设备使用记录',
        'action': 'edit',
    }
    
    return render(request, 'equipment/usage_record_form.html', context)


def export_usage_record_csv(usage_list):
    """导出设备使用记录CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="usage_records_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    response.write('\ufeff')  # BOM for Excel
    
    writer = csv.writer(response)
    writer.writerow([
        '设备名称', '使用人', '试验任务', '开始时间', '结束时间',
        '使用目的', '使用说明', '设备状态', '使用时长'
    ])
    
    for usage in usage_list:
        duration = ''
        if usage.usage_duration:
            duration = str(usage.usage_duration)
        
        writer.writerow([
            usage.equipment.name,
            usage.user.get_full_name(),
            usage.test_task.task_name if usage.test_task else '',
            usage.start_time,
            usage.end_time or '',
            usage.usage_purpose,
            usage.usage_notes,
            usage.get_equipment_condition_display(),
            duration,
        ])
    
    return response


# 设备维护记录视图
@login_required
def maintenance_record_list(request):
    """设备维护记录列表"""
    form = EquipmentMaintenanceSearchForm(request.GET)
    maintenance_list = EquipmentMaintenance.objects.select_related(
        'equipment', 'maintenance_person'
    ).all()
    
    # 搜索过滤
    if form.is_valid():
        search = form.cleaned_data.get('search')
        if search:
            maintenance_list = maintenance_list.filter(
                Q(equipment__name__icontains=search) |
                Q(maintenance_person__username__icontains=search) |
                Q(maintenance_person__first_name__icontains=search) |
                Q(maintenance_person__last_name__icontains=search) |
                Q(maintenance_content__icontains=search)
            )
        
        equipment = form.cleaned_data.get('equipment')
        if equipment:
            maintenance_list = maintenance_list.filter(equipment=equipment)
        
        maintenance_type = form.cleaned_data.get('maintenance_type')
        if maintenance_type:
            maintenance_list = maintenance_list.filter(maintenance_type=maintenance_type)
        
        maintenance_person = form.cleaned_data.get('maintenance_person')
        if maintenance_person:
            maintenance_list = maintenance_list.filter(maintenance_person=maintenance_person)
        
        start_date = form.cleaned_data.get('start_date')
        if start_date:
            maintenance_list = maintenance_list.filter(maintenance_date__gte=start_date)
        
        end_date = form.cleaned_data.get('end_date')
        if end_date:
            maintenance_list = maintenance_list.filter(maintenance_date__lte=end_date)
        
        maintenance_result = form.cleaned_data.get('maintenance_result')
        if maintenance_result:
            maintenance_list = maintenance_list.filter(maintenance_result=maintenance_result)
    
    # 分页
    paginator = Paginator(maintenance_list, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # 导出CSV
    if request.GET.get('export') == 'csv':
        return export_maintenance_record_csv(maintenance_list)
    
    context = {
        'form': form,
        'page_obj': page_obj,
        'maintenance_list': page_obj.object_list,
    }
    
    return render(request, 'equipment/maintenance_record_list.html', context)


@login_required
@permission_required('equipment.add_equipmentmaintenance', raise_exception=True)
def maintenance_record_create(request):
    """创建设备维护记录"""
    if request.method == 'POST':
        form = EquipmentMaintenanceForm(request.POST)
        if form.is_valid():
            maintenance_record = form.save()
            # 更新设备维护信息
            equipment = maintenance_record.equipment
            equipment.last_maintenance_date = maintenance_record.maintenance_date
            if maintenance_record.next_maintenance_date:
                equipment.next_maintenance_date = maintenance_record.next_maintenance_date
            else:
                # 根据维护间隔计算下次维护日期
                equipment.next_maintenance_date = (
                    maintenance_record.maintenance_date + 
                    timedelta(days=equipment.maintenance_interval)
                )
            # 如果维护完成，更新设备状态
            if maintenance_record.maintenance_result == 'completed':
                equipment.status = 'available'
            equipment.save()
            messages.success(request, '设备维护记录创建成功！')
            return redirect('equipment:maintenance_record_detail', pk=maintenance_record.pk)
    else:
        form = EquipmentMaintenanceForm()
        # 设置默认值
        form.fields['maintenance_person'].initial = request.user
        form.fields['maintenance_date'].initial = timezone.now().date()
    
    context = {
        'form': form,
        'title': '新增设备维护记录',
        'action': 'create',
    }
    
    return render(request, 'equipment/maintenance_record_form.html', context)


@login_required
def maintenance_record_detail(request, pk):
    """设备维护记录详情"""
    maintenance_record = get_object_or_404(
        EquipmentMaintenance.objects.select_related('equipment', 'maintenance_person'),
        pk=pk
    )
    
    context = {
        'maintenance_record': maintenance_record,
    }
    
    return render(request, 'equipment/maintenance_record_detail.html', context)


@login_required
@permission_required('equipment.change_equipmentmaintenance', raise_exception=True)
def maintenance_record_edit(request, pk):
    """编辑设备维护记录"""
    maintenance_record = get_object_or_404(EquipmentMaintenance, pk=pk)
    
    if request.method == 'POST':
        form = EquipmentMaintenanceForm(request.POST, instance=maintenance_record)
        if form.is_valid():
            maintenance_record = form.save()
            messages.success(request, '设备维护记录更新成功！')
            return redirect('equipment:maintenance_record_detail', pk=maintenance_record.pk)
    else:
        form = EquipmentMaintenanceForm(instance=maintenance_record)
    
    context = {
        'form': form,
        'maintenance_record': maintenance_record,
        'title': '编辑设备维护记录',
        'action': 'edit',
    }
    
    return render(request, 'equipment/maintenance_record_form.html', context)


def export_maintenance_record_csv(maintenance_list):
    """导出设备维护记录CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="maintenance_records_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    response.write('\ufeff')  # BOM for Excel
    
    writer = csv.writer(response)
    writer.writerow([
        '设备名称', '维护类型', '维护日期', '维护人员', '维护内容',
        '更换部件', '维护费用', '维护结果', '下次维护日期', '备注'
    ])
    
    for maintenance in maintenance_list:
        writer.writerow([
            maintenance.equipment.name,
            maintenance.get_maintenance_type_display(),
            maintenance.maintenance_date,
            maintenance.maintenance_person.get_full_name(),
            maintenance.maintenance_content,
            maintenance.parts_replaced,
            maintenance.maintenance_cost,
            maintenance.get_maintenance_result_display(),
            maintenance.next_maintenance_date or '',
            maintenance.remarks,
        ])
    
    return response


@login_required
def equipment_statistics(request):
    """设备统计"""
    # 设备状态统计
    status_stats = Equipment.objects.values('status').annotate(
        count=Count('id')
    ).order_by('status')
    
    # 制造商统计
    manufacturer_stats = Equipment.objects.values('manufacturer').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # 月度维护统计
    from django.db.models import TruncMonth
    maintenance_stats = EquipmentMaintenance.objects.annotate(
        month=TruncMonth('maintenance_date')
    ).values('month').annotate(
        count=Count('id'),
        avg_cost=Avg('maintenance_cost')
    ).order_by('month')
    
    # 设备使用率统计
    usage_stats = EquipmentUsageRecord.objects.values(
        'equipment__name'
    ).annotate(
        usage_count=Count('id')
    ).order_by('-usage_count')[:10]
    
    context = {
        'status_stats': status_stats,
        'manufacturer_stats': manufacturer_stats,
        'maintenance_stats': maintenance_stats,
        'usage_stats': usage_stats,
    }
    
    return render(request, 'equipment/statistics.html', context)