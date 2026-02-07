# 2026-02-04 生产环境部署文件清单

以下是今天（2026-02-04）修改或创建的所有需要上传到生产环境的文件列表。

## 1. 核心配置文件
| 文件路径 | 说明 |
|----------|------|
| `laboratory_management/settings.py` | 增加了允许的主机IP、静态文件配置等 |

## 2. 前端静态资源 (Static Assets)
**注意：上传后必须运行 `python manage.py collectstatic`**

### CSS 样式
| 文件路径 | 说明 |
|----------|------|
| `static/css/tokens.css` | 玻璃拟态设计系统变量 |
| `static/css/glass.css` | 玻璃拟态核心样式 |
| `static/css/sidebar-theme.css` | 侧边栏主题变量 |
| `static/css/sidebar.css` | 侧边栏布局样式 |
| `static/css/modal.css` | 弹窗组件样式 |

### JavaScript 脚本
| 文件路径 | 说明 |
|----------|------|
| `static/js/sidebar.js` | 侧边栏交互逻辑 |
| `static/js/modal.js` | 弹窗组件逻辑 |

## 3. 模板文件 (Templates)

### 全局模板
| 文件路径 | 说明 |
|----------|------|
| `templates/base.html` | 引入了新样式、重构了导航栏结构 |

### 任务管理应用 (apps/tasks)
| 文件路径 | 说明 |
|----------|------|
| `apps/tasks/templates/tasks/task_detail.html` | 任务详情页更新 |
| `apps/tasks/templates/tasks/subtask_detail.html` | 子任务详情页更新 |
| `apps/tasks/templates/tasks/task_decompose.html` | 任务分解页更新 |

## 4. 后端逻辑代码 (Backend Code)

### 任务管理应用 (apps/tasks)
| 文件路径 | 说明 |
|----------|------|
| `apps/tasks/models.py` | 数据模型更新 |
| `apps/tasks/views.py` | 视图逻辑更新 |
| `apps/tasks/forms.py` | 表单逻辑更新 |
| `apps/tasks/migrations/0015_alter_testtask_actual_end_date_and_more.py` | 数据库迁移文件 |

## 5. 运维与文档 (Optional)
| 文件路径 | 说明 |
|----------|------|
| `install_redis.ps1` | Redis 安装脚本 (Windows) |
| `Redis安装指南.md` | Redis 安装说明 |
| `Glassmorphism集成使用指南.md` | UI 风格指南 |

---

## 部署操作步骤

1.  **备份**：备份上述文件在服务器上的对应版本。
2.  **上传**：将文件通过 FTP/SFTP 上传并覆盖。
3.  **收集静态文件**：
    ```powershell
    python manage.py collectstatic --noinput
    ```
4.  **重启服务**：重启 Django/Gunicorn/IIS 服务以应用 Python 代码变更。
5.  **数据库迁移**（如果涉及模型变更）：
    ```powershell
    python manage.py migrate
    ```
    *(注：今天的变更主要集中在 UI 和视图逻辑，若 `models.py` 变更涉及数据库结构，请务必执行迁移)*
