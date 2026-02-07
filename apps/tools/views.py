from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.http import HttpResponse
import csv

from .models import Tool
from .forms import ToolForm, ToolSearchForm

@login_required
def tool_list(request):
    """工具列表"""
    form = ToolSearchForm(request.GET)
    tools = Tool.objects.select_related('responsible_person').all()
    
    # 搜索过滤
    if form.is_valid():
        search = form.cleaned_data.get('search')
        if search:
            tools = tools.filter(
                Q(tool_id__icontains=search) |
                Q(name__icontains=search) |
                Q(model__icontains=search)
            )
        
        status = form.cleaned_data.get('status')
        if status:
            tools = tools.filter(status=status)
            
        type_ = form.cleaned_data.get('type')
        if type_:
            tools = tools.filter(type__icontains=type_)
            
        location = form.cleaned_data.get('location')
        if location:
            tools = tools.filter(location__icontains=location)

    # 导出CSV
    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="tools_{timezone.now().strftime("%Y%m%d%H%M")}.csv"'
        response.write('\ufeff')  # UTF-8 BOM

        writer = csv.writer(response)
        writer.writerow(['工具编号', '名称', '类型', '型号', '制造商', '状态', '位置', '负责人', '采购日期', '下次校准日期'])

        for tool in tools:
            writer.writerow([
                tool.tool_id,
                tool.name,
                tool.type,
                tool.model,
                tool.manufacturer,
                tool.get_status_display(),
                tool.location,
                tool.responsible_person.get_full_name() if tool.responsible_person else '',
                tool.purchase_date,
                tool.next_calibration_date or ''
            ])
        return response

    # 分页
    paginator = Paginator(tools, 20)  # 每页20条
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'form': form,
        'page_obj': page_obj,
        'tools': page_obj,  # 兼容性变量
    }
    return render(request, 'tools/tool_list.html', context)

@login_required
def tool_detail(request, pk):
    """工具详情"""
    tool = get_object_or_404(Tool, pk=pk)
    context = {
        'tool': tool,
    }
    return render(request, 'tools/tool_detail.html', context)

@login_required
def tool_create(request):
    """新增工具"""
    if request.method == 'POST':
        form = ToolForm(request.POST)
        if form.is_valid():
            tool = form.save()
            messages.success(request, f'工具 "{tool.name}" 已成功创建')
            return redirect('tools:list')
    else:
        form = ToolForm()
    
    context = {
        'form': form,
        'title': '新增工具'
    }
    return render(request, 'tools/tool_form.html', context)

@login_required
def tool_edit(request, pk):
    """编辑工具"""
    tool = get_object_or_404(Tool, pk=pk)
    if request.method == 'POST':
        form = ToolForm(request.POST, instance=tool)
        if form.is_valid():
            tool = form.save()
            messages.success(request, f'工具 "{tool.name}" 已成功更新')
            return redirect('tools:detail', pk=tool.pk)
    else:
        form = ToolForm(instance=tool)
    
    context = {
        'form': form,
        'title': '编辑工具',
        'tool': tool
    }
    return render(request, 'tools/tool_form.html', context)

@login_required
@require_POST
def tool_delete(request, pk):
    """删除工具"""
    tool = get_object_or_404(Tool, pk=pk)
    name = tool.name
    tool.delete()
    messages.success(request, f'工具 "{name}" 已成功删除')
    return redirect('tools:list')

@login_required
@require_POST
def tool_bulk_delete(request):
    """批量删除工具"""
    tool_ids = request.POST.getlist('tool_ids')
    if tool_ids:
        deleted_count, _ = Tool.objects.filter(id__in=tool_ids).delete()
        messages.success(request, f'成功删除了 {deleted_count} 个工具')
    else:
        messages.warning(request, '未选择任何工具')
    return redirect('tools:list')
