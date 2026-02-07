from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def report_list(request):
    """报表列表页面"""
    # 临时实现，后续可以扩展
    context = {
        'title': '统计报表',
    }
    return render(request, 'base.html', context)