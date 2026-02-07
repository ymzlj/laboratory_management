# 2026-02-06 生产环境更新部署文档 (最终版)

## 1. 更新内容概述
本次更新包含以下重要修复和优化：
1.  **修复**：试验任务编辑界面报错 `BaseModelForm.__init__() got an unexpected keyword argument 'user'`。
2.  **修复**：子任务详情界面模板渲染报错 `'SubTaskDataForm' object has no attribute 'get'`。
3.  **优化**：通用批量数据录入性能优化（大幅提升加载速度）。
4.  **功能**：试验类型字段配置新增“是否启用批量录入”开关。
5.  **交互**：修复浏览器返回按钮导致“批量录入”按钮状态卡死的问题。
6.  **UI**：子任务详情界面正确区分“试验参数”与“批量数据列表”。

## 2. 涉及文件清单
请将以下文件上传至服务器对应目录（覆盖原文件）：

### 后端代码 (Python)
- `apps/tasks/forms.py` (修复表单初始化参数错误)
- `apps/tasks/views.py` (视图逻辑优化与修复)
- `apps/tasks/models.py` (模型字段更新)
- `apps/tasks/generic_forms.py` (表单集性能优化)
- `apps/tasks/templatetags/task_extras.py` (模板标签增强)

### 前端模板 (HTML)
- `apps/tasks/templates/tasks/subtask_detail.html` (子任务详情页交互修复)
- `apps/tasks/templates/tasks/test_type_detail.html` (字段配置列表修复)
- `apps/tasks/templates/tasks/test_type_field_form.html` (新增开关控件)

## 3. Ubuntu 部署操作说明

### 第一步：备份（可选但推荐）
```bash
# 假设项目目录为 /opt/laboratory_management
cd /opt/laboratory_management
cp -r apps apps_backup_20260206
```

### 第二步：上传文件
请通过 FTP/SFTP 工具将本地修改后的文件上传覆盖服务器上的对应文件。

### 第三步：执行数据库迁移
由于涉及 `models.py` 的变更（新增字段），必须执行迁移。
```bash
# 进入项目目录
cd /opt/laboratory_management

# 激活虚拟环境 (根据实际情况调整路径)
source venv/bin/activate

# 执行迁移
python manage.py makemigrations
python manage.py migrate
```
*注意：如果提示 `OperationalError: Unknown column...`，说明迁移未应用，请务必执行上述命令。*

### 第四步：重启服务
更新代码后需要重启应用服务以生效。
```bash
# 重启 Gunicorn 服务 (服务名为 gunicorn_lab)
sudo systemctl restart gunicorn_lab

# 重启 Celery 服务 (如果有)
sudo systemctl restart celery_lab_worker

# 或者手动重启 (如果是测试运行)
# pkill -f runserver
# python manage.py runserver 0.0.0.0:8000
```

### 第五步：验证
1. 访问 `/tasks/1/edit/` 确认是否不再报错。
2. 访问子任务详情页，确认页面加载正常且无 AttributeError。
3. 检查“批量录入”功能是否流畅。
