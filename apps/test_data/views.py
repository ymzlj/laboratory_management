"""
试验数据模块视图
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
import csv
from datetime import datetime

from .models import (
    AntiSlipTestData, MetalImpactTestData, MetalTensileTestData,
    CompressionTestData, FatigueTestData, HardnessTestData,
    CreepTestData, CorrosionTestData
)
from .forms import (
    AntiSlipTestDataForm, MetalImpactTestDataForm, MetalTensileTestDataForm,
    CompressionTestDataForm, FatigueTestDataForm, HardnessTestDataForm,
    CreepTestDataForm, CorrosionTestDataForm, TestDataSearchForm
)


# 试验数据类型映射
TEST_DATA_MODELS = {
    'anti_slip': AntiSlipTestData,
    'metal_impact': MetalImpactTestData,
    'metal_tensile': MetalTensileTestData,
    'compression': CompressionTestData,
    'fatigue': FatigueTestData,
    'hardness': HardnessTestData,
    'creep': CreepTestData,
    'corrosion': CorrosionTestData,
}

TEST_DATA_FORMS = {
    'anti_slip': AntiSlipTestDataForm,
    'metal_impact': MetalImpactTestDataForm,
    'metal_tensile': MetalTensileTestDataForm,
    'compression': CompressionTestDataForm,
    'fatigue': FatigueTestDataForm,
    'hardness': HardnessTestDataForm,
    'creep': CreepTestDataForm,
    'corrosion': CorrosionTestDataForm,
}

TEST_DATA_NAMES = {
    'anti_slip': '防滑试验',
    'metal_impact': '金属冲击试验',
    'metal_tensile': '金属拉伸试验',
    'compression': '压缩试验',
    'fatigue': '疲劳试验',
    'hardness': '硬度试验',
    'creep': '蠕变试验',
    'corrosion': '腐蚀试验',
}


@login_required
def test_data_index(request):
    """试验数据首页"""
    # 统计各类试验数据数量
    stats = {}
    for key, model in TEST_DATA_MODELS.items():
        stats[key] = {
            'name': TEST_DATA_NAMES[key],
            'count': model.objects.count(),
            'recent_count': model.objects.filter(
                created_at__gte=datetime.now().replace(day=1)
            ).count()
        }
    
    # 最近的试验数据
    recent_data = []
    for key, model in TEST_DATA_MODELS.items():
        recent_items = model.objects.select_related('test_task', 'tester').order_by('-created_at')[:3]
        for item in recent_items:
            recent_data.append({
                'type': TEST_DATA_NAMES[key],
                'type_key': key,
                'item': item
            })
    
    # 按创建时间排序
    recent_data.sort(key=lambda x: x['item'].created_at, reverse=True)
    recent_data = recent_data[:10]  # 只显示最近10条
    
    context = {
        'stats': stats,
        'recent_data': recent_data,
    }
    return render(request, 'test_data/index.html', context)


@login_required
def test_data_list(request, data_type):
    """试验数据列表"""
    if data_type not in TEST_DATA_MODELS:
        messages.error(request, '无效的试验数据类型')
        return redirect('test_data:index')
    
    model = TEST_DATA_MODELS[data_type]
    form = TestDataSearchForm(request.GET)
    
    # 获取查询集
    queryset = model.objects.select_related('test_task', 'tester').order_by('-created_at')
    
    # 应用搜索过滤
    if form.is_valid():
        search = form.cleaned_data.get('search')
        if search:
            queryset = queryset.filter(
                Q(sample_id__icontains=search) |
                Q(tester__username__icontains=search) |
                Q(tester__first_name__icontains=search) |
                Q(tester__last_name__icontains=search)
            )
        
        test_task = form.cleaned_data.get('test_task')
        if test_task:
            queryset = queryset.filter(test_task=test_task)
        
        tester = form.cleaned_data.get('tester')
        if tester:
            queryset = queryset.filter(tester=tester)
        
        date_from = form.cleaned_data.get('date_from')
        if date_from:
            queryset = queryset.filter(test_date__gte=date_from)
        
        date_to = form.cleaned_data.get('date_to')
        if date_to:
            queryset = queryset.filter(test_date__lte=date_to)
        
        result = form.cleaned_data.get('result')
        if result:
            queryset = queryset.filter(result=result)
    
    # 分页
    paginator = Paginator(queryset, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # 导出CSV
    if request.GET.get('export') == 'csv':
        return export_test_data_csv(queryset, data_type)
    
    context = {
        'data_type': data_type,
        'data_name': TEST_DATA_NAMES[data_type],
        'form': form,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
    }
    return render(request, 'test_data/list.html', context)


@login_required
@permission_required('test_data.add_testdata', raise_exception=True)
def test_data_create(request, data_type):
    """创建试验数据"""
    if data_type not in TEST_DATA_FORMS:
        messages.error(request, '无效的试验数据类型')
        return redirect('test_data:index')
    
    form_class = TEST_DATA_FORMS[data_type]
    
    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            test_data = form.save(commit=False)
            if not test_data.tester_id:
                test_data.tester = request.user
            test_data.save()
            messages.success(request, f'{TEST_DATA_NAMES[data_type]}数据创建成功')
            return redirect('test_data:detail', data_type=data_type, pk=test_data.pk)
    else:
        form = form_class()
    
    context = {
        'form': form,
        'data_type': data_type,
        'data_name': TEST_DATA_NAMES[data_type],
        'action': 'create'
    }
    return render(request, 'test_data/form.html', context)


@login_required
def test_data_detail(request, data_type, pk):
    """试验数据详情"""
    if data_type not in TEST_DATA_MODELS:
        messages.error(request, '无效的试验数据类型')
        return redirect('test_data:index')
    
    model = TEST_DATA_MODELS[data_type]
    test_data = get_object_or_404(
        model.objects.select_related('test_task', 'tester'),
        pk=pk
    )
    
    context = {
        'test_data': test_data,
        'data_type': data_type,
        'data_name': TEST_DATA_NAMES[data_type],
    }
    return render(request, 'test_data/detail.html', context)


@login_required
@permission_required('test_data.change_testdata', raise_exception=True)
def test_data_edit(request, data_type, pk):
    """编辑试验数据"""
    if data_type not in TEST_DATA_MODELS:
        messages.error(request, '无效的试验数据类型')
        return redirect('test_data:index')
    
    model = TEST_DATA_MODELS[data_type]
    form_class = TEST_DATA_FORMS[data_type]
    test_data = get_object_or_404(model, pk=pk)
    
    if request.method == 'POST':
        form = form_class(request.POST, instance=test_data)
        if form.is_valid():
            form.save()
            messages.success(request, f'{TEST_DATA_NAMES[data_type]}数据更新成功')
            return redirect('test_data:detail', data_type=data_type, pk=test_data.pk)
    else:
        form = form_class(instance=test_data)
    
    context = {
        'form': form,
        'test_data': test_data,
        'data_type': data_type,
        'data_name': TEST_DATA_NAMES[data_type],
        'action': 'edit'
    }
    return render(request, 'test_data/form.html', context)


@login_required
@permission_required('test_data.delete_testdata', raise_exception=True)
@require_http_methods(["POST"])
def test_data_delete(request, data_type, pk):
    """删除试验数据"""
    if data_type not in TEST_DATA_MODELS:
        return JsonResponse({'success': False, 'message': '无效的试验数据类型'})
    
    model = TEST_DATA_MODELS[data_type]
    test_data = get_object_or_404(model, pk=pk)
    
    try:
        test_data.delete()
        return JsonResponse({'success': True, 'message': '删除成功'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'删除失败：{str(e)}'})


@login_required
@require_http_methods(["POST"])
def test_data_bulk_delete(request, data_type):
    """批量删除试验数据"""
    if data_type not in TEST_DATA_MODELS:
        return JsonResponse({'success': False, 'message': '无效的试验数据类型'})
    
    if not request.user.has_perm('test_data.delete_testdata'):
        return JsonResponse({'success': False, 'message': '权限不足'})
    
    import json
    data = json.loads(request.body)
    ids = data.get('ids', [])
    
    if not ids:
        return JsonResponse({'success': False, 'message': '请选择要删除的数据'})
    
    model = TEST_DATA_MODELS[data_type]
    
    try:
        deleted_count = model.objects.filter(id__in=ids).delete()[0]
        return JsonResponse({
            'success': True,
            'message': f'成功删除 {deleted_count} 条数据'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'删除失败：{str(e)}'})


def export_test_data_csv(queryset, data_type):
    """导出试验数据为CSV"""
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{TEST_DATA_NAMES[data_type]}_data_{datetime.now().strftime("%Y%m%d")}.csv"'
    
    # 添加BOM以支持Excel正确显示中文
    response.write('\ufeff')
    
    writer = csv.writer(response)
    
    # 根据数据类型写入不同的表头
    if data_type == 'anti_slip':
        writer.writerow([
            '样品编号', '试验日期', '试验员', '温度(°C)', '湿度(%)',
            '摩擦系数', '防滑阻力(N)', '试验结果', '备注', '创建时间'
        ])
        for item in queryset:
            writer.writerow([
                item.sample_id, item.test_date, item.tester.get_full_name(),
                item.temperature, item.humidity, item.friction_coefficient,
                item.slip_resistance, item.result, item.remarks, item.created_at
            ])
    elif data_type == 'metal_impact':
        writer.writerow([
            '样品编号', '试验日期', '试验员', '温度(°C)', '冲击能量(J)',
            '冲击强度(J/cm²)', '断裂类型', '试验结果', '备注', '创建时间'
        ])
        for item in queryset:
            writer.writerow([
                item.sample_id, item.test_date, item.tester.get_full_name(),
                item.temperature, item.impact_energy, item.impact_strength,
                item.fracture_type, item.result, item.remarks, item.created_at
            ])
    elif data_type == 'metal_tensile':
        writer.writerow([
            '样品编号', '试验日期', '试验员', '温度(°C)', '应变速率(s⁻¹)',
            '抗拉强度(MPa)', '屈服强度(MPa)', '延伸率(%)', '弹性模量(GPa)',
            '试验结果', '备注', '创建时间'
        ])
        for item in queryset:
            writer.writerow([
                item.sample_id, item.test_date, item.tester.get_full_name(),
                item.temperature, item.strain_rate, item.tensile_strength,
                item.yield_strength, item.elongation, item.elastic_modulus,
                item.result, item.remarks, item.created_at
            ])
    # 可以继续添加其他数据类型的导出格式...
    
    return response


@login_required
def test_data_statistics(request):
    """试验数据统计"""
    from django.db.models import Count, Avg
    from datetime import datetime, timedelta
    
    # 按类型统计
    type_stats = []
    for key, model in TEST_DATA_MODELS.items():
        total = model.objects.count()
        this_month = model.objects.filter(
            created_at__gte=datetime.now().replace(day=1)
        ).count()
        type_stats.append({
            'name': TEST_DATA_NAMES[key],
            'key': key,
            'total': total,
            'this_month': this_month
        })
    
    # 按试验员统计
    tester_stats = []
    for key, model in TEST_DATA_MODELS.items():
        stats = model.objects.values(
            'tester__username', 'tester__first_name', 'tester__last_name'
        ).annotate(count=Count('id')).order_by('-count')[:5]
        
        for stat in stats:
            name = stat['tester__first_name'] or stat['tester__username']
            tester_stats.append({
                'name': name,
                'type': TEST_DATA_NAMES[key],
                'count': stat['count']
            })
    
    # 按月份统计（最近12个月）
    monthly_stats = {}
    for i in range(12):
        month_start = (datetime.now().replace(day=1) - timedelta(days=30*i)).replace(day=1)
        month_end = (month_start.replace(month=month_start.month+1) if month_start.month < 12 
                    else month_start.replace(year=month_start.year+1, month=1))
        
        month_key = month_start.strftime('%Y-%m')
        monthly_stats[month_key] = {}
        
        for key, model in TEST_DATA_MODELS.items():
            count = model.objects.filter(
                created_at__gte=month_start,
                created_at__lt=month_end
            ).count()
            monthly_stats[month_key][key] = count
    
    context = {
        'type_stats': type_stats,
        'tester_stats': tester_stats,
        'monthly_stats': monthly_stats,
    }
    return render(request, 'test_data/statistics.html', context)
