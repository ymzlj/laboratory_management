# 2026-02-06 补充更新部署指南 - 试验数据批量录入优化与修复

本文档整理了 2026-02-06 下午进行的补充更新内容，包括批量录入性能优化、字段显示修复和交互逻辑改进。请在之前的部署基础上追加更新以下文件。

---

## 1. 变更内容摘要

本次补充更新主要修复了以下问题并进行了优化：
1.  **子任务详情页修复**：
    *   修复了“试验参数”区域输入框不显示的问题（解决了 `custom_` 前缀导致的字段匹配错误）。
    *   修复了 `AttributeError: 'SubTaskDataForm' object has no attribute 'get'` 报错。
    *   实现了“批量录入”与“单条参数”的严格分离：关闭“启用批量录入”的字段现在正确显示为独立输入框，且不会出现在批量列表中。
2.  **批量录入性能优化**：
    *   重构了 `generic_test_data_entry` 视图和 `create_generic_test_data_formset` 函数。
    *   移除了每次请求动态创建 Form 类的开销，改用 `form_kwargs` 传递参数。
    *   增加了数据库查询优化 (`select_related`)，减少了页面加载时的数据库查询次数，提升跳转速度。
3.  **模板标签增强**：
    *   增强了 `get_item` 过滤器，使其同时支持字典查找和 Django Form 字段查找。

---

## 2. 涉及变更的文件列表

请将以下文件上传到服务器覆盖原文件：

### 后端代码 (Python)
*   `apps/tasks/views.py` (批量录入视图优化、子任务详情视图逻辑调整)
*   `apps/tasks/generic_forms.py` (表单集工厂函数重构)
*   `apps/tasks/templatetags/task_extras.py` (模板过滤器增强)

### 前端模板 (HTML)
*   `apps/tasks/templates/tasks/subtask_detail.html` (子任务详情页修复字段显示)
*   `apps/tasks/templates/tasks/test_type_detail.html` (试验类型详情页显示优化)

---

## 3. Ubuntu 生产环境更新步骤

请按照以下步骤在你的 Ubuntu 服务器上进行更新。

### 第一步：连接服务器
```bash
ssh ymz@192.168.1.241
# 输入密码: 123456
```

### 第二步：上传代码
**方法 A (推荐)**：如果你在本地使用了 Git，请提交代码并在服务器拉取：
```bash
cd /opt/laboratory_management
git pull
```

**方法 B**：如果你是直接复制文件，请使用 SCP 或 WinSCP 将上述列表中的文件上传到服务器对应的 `/opt/laboratory_management/` 目录下，覆盖原文件。

### 第三步：重启服务 (必须)
由于修改了 Python 代码（视图和表单逻辑），必须重启 Web 服务才能生效。

```bash
# 重启 Web 服务
sudo systemctl restart gunicorn_lab

# 检查服务状态
sudo systemctl status gunicorn_lab
```

### 第四步：验证更新
1.  **验证字段显示**：进入一个子任务详情页，确认“试验参数”区域的输入框是否正常显示。
2.  **验证批量录入速度**：点击“批量数据录入”按钮，感受页面跳转速度是否有所提升。
3.  **验证功能**：尝试修改一个试验参数并保存，确认数据能正常更新。

---

## 4. 注意事项
*   本次更新**不涉及数据库模型变更**，因此**不需要**执行 `python manage.py migrate`。
*   如果页面显示异常，请强制刷新浏览器缓存 (`Ctrl + F5`)。
