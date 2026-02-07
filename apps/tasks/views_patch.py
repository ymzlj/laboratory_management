from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
import json
from .models import TestTask, TestTaskProcessHistory

# ==================== 试验过程描述管理 ====================

@login_required
@require_http_methods(["POST"])
def task_process_update(request, task_id):
    """更新试验过程描述（自动保存）"""
    task = get_object_or_404(TestTask, id=task_id)
    
    # 权限检查：只有负责人、管理员、主管可以编辑
    # 并且任务状态不能是已归档
    if task.status.code == 'archived':
        return JsonResponse({'success': False, 'message': '任务已归档，无法编辑'})

    if not (request.user == task.assignee or request.user.role in ['manager', 'admin']):
        return JsonResponse({'success': False, 'message': '权限不足'})
        
    try:
        data = json.loads(request.body)
        content = data.get('content', '')
        
        # 简单字数校验
        if len(content) > 5000: # 稍微放宽一点后端限制
             return JsonResponse({'success': False, 'message': '内容超过长度限制'})

        # 只有内容变更时才保存
        if content != task.test_process_description:
            # 保存历史记录
            # 只有当上一次历史记录不是同一个人的最近一次（避免频繁自动保存产生垃圾数据）
            # 或者简单点：每次变更都存，但前端debounce控制频率
            TestTaskProcessHistory.objects.create(
                task=task,
                content=content,
                updated_by=request.user
            )
            
            task.test_process_description = content
            task.save(update_fields=['test_process_description', 'updated_at'])
            
        return JsonResponse({'success': True, 'message': '已保存'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@login_required
def task_process_history(request, task_id):
    """获取试验过程历史记录"""
    task = get_object_or_404(TestTask, id=task_id)
    history_list = task.process_history.select_related('updated_by').all()[:20] # 最近20条
    
    data = []
    for h in history_list:
        data.append({
            'id': h.id,
            'updated_by': h.updated_by.username if h.updated_by else '未知',
            'created_at': h.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'content': h.content  # 返回完整内容以便恢复或查看
        })
        
    return JsonResponse({'success': True, 'history': data})
