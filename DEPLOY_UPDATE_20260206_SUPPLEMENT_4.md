# 2026-02-06 生产环境更新部署文档 (最终版 - 补充 4)

## 1. 修复内容
本次更新主要修复 **TooManyFieldsSent** 错误。

**问题原因**：
批量数据录入时提交的表单字段数量超过了 Django 默认的 1000 个限制（每行数据可能包含10+个字段，100行数据就会超过限制）。

**修复方案**：
增加 `DATA_UPLOAD_MAX_NUMBER_FIELDS` 配置，将其从默认的 1000 提升至 10000。

## 2. 涉及文件清单
请将以下文件上传至服务器对应目录（覆盖原文件）：

### 配置文件
- `laboratory_management/settings.py` (增加 DATA_UPLOAD_MAX_NUMBER_FIELDS 配置)

## 3. 部署操作说明

### 第一步：上传文件
请将 `laboratory_management/settings.py` 上传覆盖服务器上的同名文件。

### 第二步：无需迁移
本次修改仅涉及配置，**不需要**执行数据库迁移。

### 第三步：重启服务
```bash
# 重启 Gunicorn 服务
sudo systemctl restart gunicorn_lab
```

### 第四步：验证
1. 再次尝试批量录入大量数据（例如500条以上）。
2. 确认不再报错。
