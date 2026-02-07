# 2026-02-06 生产环境更新部署文档 (最终版 - 补充 7)

## 1. 修复内容
本次更新主要为“已录入数据”列表页添加以下功能：
1.  **分页功能**：数据量大时自动分页显示（每页20条），提高页面加载速度。
2.  **导出功能**：增加“导出Excel”按钮，可将已录入的全部数据导出为 Excel 文件。

## 2. 涉及文件清单
请将以下文件上传至服务器对应目录（覆盖原文件）：

### 后端代码 (Python)
- `apps/tasks/views.py` (generic_test_data_list 增加分页和导出逻辑)

### 前端模板 (HTML)
- `apps/tasks/templates/tasks/generic_test_data_list.html` (增加分页控件和导出按钮)

## 3. 部署操作说明

### 第一步：上传文件
请将 `apps/tasks/views.py` 和 `apps/tasks/templates/tasks/generic_test_data_list.html` 上传覆盖服务器上的同名文件。

### 第二步：无需迁移
本次修改仅涉及视图和模板，**不需要**执行数据库迁移。

### 第三步：重启服务
```bash
# 重启 Gunicorn 服务
sudo systemctl restart gunicorn_lab
```

### 第四步：验证
1. 访问“查看已录入数据”界面。
2. 确认页面底部是否出现分页控件（如果数据超过20条）。
3. 点击右上角的“导出Excel”按钮，确认是否能下载 Excel 文件。
