# 2026-02-06 更新部署指南 - 试验数据批量录入与配置功能

本文档整理了 2026-02-06 进行的所有代码变更，并提供了更新生产环境的操作步骤。

---

## 1. 变更内容摘要

本次更新主要涉及以下功能：
1.  **任务列表优化**：增加了“资料状态”列，直观显示大纲、报告和过程记录状态；增加了“试验过程”内容预览；优化了“申请人”显示（包含部门）。
2.  **试验类型管理**：修复了列表分页和搜索功能；新增了“启用批量录入”开关配置。
3.  **批量数据录入重构**：
    *   移除了旧的专用试验数据模型（碟簧、通用等），统一使用新的通用数据结构。
    *   重写了批量录入界面，支持根据字段配置动态生成表单。
    *   实现了字段的“批量录入”与“元数据（单条录入）”的分离展示与编辑。
4.  **Excel 导出升级**：导出内容现在包含所有字段（除文件外），包括富文本过程描述的纯文本转换。

---

## 2. 涉及变更的文件列表


### 后端代码 (Python)
*   `apps/tasks/models.py` (数据模型变更)
*   `apps/tasks/views.py` (视图逻辑变更)
*   `apps/tasks/forms.py` (表单定义变更)
*   `apps/tasks/generic_forms.py` (批量录入表单变更)
*   `apps/tasks/admin.py` (后台管理变更)

### 前端模板 (HTML)
*   `apps/tasks/templates/tasks/task_detail.html` (任务详情页优化)
*   `apps/tasks/templates/tasks/subtask_detail.html` (子任务详情页重构)
*   `apps/tasks/templates/tasks/test_data_list.html` (任务列表页优化)
*   `apps/tasks/templates/tasks/test_type_list.html` (试验类型列表修复)
*   `apps/tasks/templates/tasks/test_type_field_form.html` (字段配置表单增加开关)
*   `apps/tasks/templates/tasks/generic_test_data_list.html` (数据列表显示优化)
*   `apps/tasks/templates/tasks/generic_test_data_entry.html` (批量录入界面优化)

---

## 3. Ubuntu 生产环境更新步骤

请按照以下步骤在你的 Ubuntu 服务器上进行更新。

### 第一步：连接服务器
使用 SSH 连接到你的服务器（使用你提供的账户 `ymz`）：
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

### 第三步：应用数据库变更 (关键)
由于我们修改了数据模型（添加了 `is_batch_input_enabled` 字段和 `meta_data` 字段，删除了旧模型），必须执行数据库迁移。

```bash
cd /opt/laboratory_management

# 1. 激活虚拟环境
source venv/bin/activate

# 2. 生成迁移文件 (如果本地没有提交 migrations 文件夹)
python manage.py makemigrations

# 3. 应用迁移到数据库
python manage.py migrate
```

### 第四步：重启服务
更新代码后，需要重启 Gunicorn 和 Celery 服务使更改生效。

```bash
# 重启 Web 服务
sudo systemctl restart gunicorn_lab

# 重启后台任务服务 (如果有)
sudo systemctl restart celery_worker

# 检查服务状态确保启动成功
sudo systemctl status gunicorn_lab
```

### 第五步：验证更新
1.  打开浏览器访问系统。
2.  进入 **“试验类型管理”** -> **“字段配置”**，尝试编辑一个字段，确认是否有 **“启用批量录入”** 开关。
3.  进入 **“任务管理”**，查看列表是否显示了新的 **“资料状态”** 列。
4.  进入任意子任务详情，确认是否有 **“批量数据录入”** 和 **“试验参数”** (元数据) 的分离显示。

---

## 4. 注意事项
*   **数据兼容性**：此次更新删除了旧的 `DiscSpringTestData` 等表。如果生产环境中有重要的旧试验数据，建议在执行 `migrate` 前先备份数据库。
    *   备份命令：`mysqldump -u lab_user -p laboratory_test_management > backup_20260206.sql`
*   **浏览器缓存**：如果页面样式或 JS 行为异常，请尝试 `Ctrl + F5` 强制刷新浏览器缓存。
