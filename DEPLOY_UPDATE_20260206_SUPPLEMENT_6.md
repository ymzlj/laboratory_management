# 2026-02-06 生产环境更新部署文档 (最终版 - 补充 6)

## 1. 修复内容
本次更新主要修复 **UnboundLocalError: cannot access local variable 'datetime'** 错误。

**问题原因**：
在之前的 Excel 导入逻辑优化中，我在 `generic_test_data_entry` 函数内部使用了 `from datetime import datetime`，这遮蔽了文件顶部导入的全局 `datetime` 模块。
当函数执行到后续代码（第859行）调用 `datetime.now()` 时，Python 认为这里的 `datetime` 是局部变量，但在该分支中尚未赋值（因为之前的导入是在另一个 if 分支里），从而抛出 `UnboundLocalError`。

**修复方案**：
在内部导入时使用别名 `from datetime import datetime as dt_datetime`，避免与全局 `datetime` 模块冲突。

## 2. 涉及文件清单
请将以下文件上传至服务器对应目录（覆盖原文件）：

### 后端代码 (Python)
- `apps/tasks/views.py` (修复变量作用域冲突)

## 3. 部署操作说明

### 第一步：上传文件
请将 `apps/tasks/views.py` 上传覆盖服务器上的同名文件。

### 第二步：无需迁移
本次修改仅涉及视图逻辑，**不需要**执行数据库迁移。

### 第三步：重启服务
```bash
# 重启 Gunicorn 服务
sudo systemctl restart gunicorn_lab
```

### 第四步：验证
1. 再次尝试批量录入数据。
2. 确认不再报错 `UnboundLocalError`。
