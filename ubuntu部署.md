# Ubuntu 22.04/20.04 部署指南 - 试验室管理系统

这份文档专门为“电脑小白”编写，旨在帮助你在 Ubuntu 服务器上从零开始部署试验室管理系统。

**目标环境信息：**
- **服务器IP**: `192.168.187.128`
- **数据库账号**: `lab_user`
- **数据库密码**: `Ymzlj729928@`
- **数据库名**: `laboratory_test_management`
- **部署路径**: `/opt/laboratory_management`

---

## 常见问题快速索引 (Troubleshooting)
如果你在部署过程中遇到报错，请先查看这里。这些都是你实际遇到并解决过的问题：

### 1. 文件权限报错 (Permission denied)
**现象**：编辑文件时提示 `Error writing ...: Permission denied`
**原因**：当前用户没有权限修改该文件。
**解决**：
- 编辑时加上 `sudo`，例如：`sudo nano /opt/...`
- 或者修改目录归属权（推荐）：`sudo chown -R $USER:$USER /opt/laboratory_management`

### 2. Gunicorn 启动失败 (Status=127)
**现象**：`systemctl status gunicorn_lab` 显示 `status=127`，或者提示 `No such file or directory`。
**原因1**：Windows 下编辑的文件换行符是 CRLF，Linux 需要 LF。
**解决1**：
```bash
sudo apt install -y dos2unix
sudo dos2unix /opt/laboratory_management/gunicorn_start.sh
```
**原因2**：虚拟环境中缺少 Gunicorn。
**解决2**：
```bash
cd /opt/laboratory_management
source venv/bin/activate
pip install gunicorn
```

### 3. 浏览器无法访问 (Connection refused / Timeout)
**现象**：浏览器提示“无法连接”或一直转圈。
**原因**：服务器防火墙没开 80 端口。
**解决**：
```bash
sudo ufw allow 80/tcp
sudo ufw reload
```

### 4. 访问显示 404 Not Found
**现象**：Nginx 欢迎页或 404 页面。
**原因**：Nginx 默认配置 (`default`) 优先级更高，或者没有链接你的配置文件。
**解决**：
```bash
# 删除默认配置
sudo rm /etc/nginx/sites-enabled/default
# 删除旧的冲突配置（如果有）
sudo rm /etc/nginx/sites-enabled/lab-mgmt
sudo rm /etc/nginx/sites-enabled/lab_project
# 链接新配置
sudo ln -sf /etc/nginx/sites-available/laboratory_management /etc/nginx/sites-enabled/
# 重启
sudo systemctl restart nginx
```

### 5. Nginx 报错 "No such file or directory"
**现象**：`nginx -t` 报错 `open() ".../sites-enabled/laboratory_management" failed`。
**原因**：软链接指向的源文件不存在（通常是源文件路径写错）。
**解决**：重新创建正确的软链接（使用 `-sf` 强制覆盖）。

---

## 第一步：连接到你的 Ubuntu 服务器

你需要使用 SSH 客户端连接到你的服务器。
在 Windows 上，你可以使用 PowerShell 或 CMD（如果安装了 OpenSSH），或者下载 Putty / Xshell。

```bash
# 在你的电脑终端执行（假设你的服务器用户名是 root，如果是其他用户请替换）
ssh root@192.168.187.128
# 输入密码登录
```

---

## 第二步：安装必要的系统软件

登录成功后，复制并执行以下命令来安装 Python、数据库、Web服务器等必要软件。

```bash
# 1. 更新软件源
sudo apt update
sudo apt upgrade -y

# 2. 安装 Python3 和开发工具
sudo apt install -y python3-pip python3-venv python3-dev build-essential libmysqlclient-dev pkg-config

# 3. 安装 MySQL 数据库
sudo apt install -y mysql-server

# 4. 安装 Redis (用于缓存和任务队列)
sudo apt install -y redis-server

# 5. 安装 Nginx (Web服务器)
sudo apt install -y nginx

# 6. 安装 Git (用于拉取代码，如果是直接上传代码包可跳过)
sudo apt install -y git

# 7. 安装文件格式转换工具 (解决Windows换行符问题)
sudo apt install -y dos2unix
```

---

## 第三步：配置数据库

我们需要创建一个数据库和用户，供项目使用。

1. **登录 MySQL**
```bash
sudo mysql
```

2. **在 MySQL 提示符下执行以下 SQL 语句**（请逐行复制粘贴）：

```sql
-- 创建数据库
CREATE DATABASE laboratory_test_management CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建用户（使用你指定的密码）
CREATE USER 'lab_user'@'localhost' IDENTIFIED BY 'Ymzlj729928@';

-- 授权
GRANT ALL PRIVILEGES ON laboratory_test_management.* TO 'lab_user'@'localhost';

-- 刷新权限
FLUSH PRIVILEGES;

-- 退出 MySQL
EXIT;
```

---

## 第四步：上传代码并准备环境

我们将把项目代码放在 `/opt/laboratory_management` 目录下。

### 1. 准备目录
```bash
# 创建目录
sudo mkdir -p /opt/laboratory_management

# 修改目录权限（方便当前用户操作）
# 注意：把下面的 $USER 替换为你的实际用户名，如 ymz
sudo chown -R $USER:$USER /opt/laboratory_management
```

### 2. 上传代码
**方法 A：如果你会使用 SCP 或 WinSCP**
将你本地项目文件夹下的**所有文件**（`manage.py`, `requirements.txt`, `laboratory_management` 文件夹等）上传到服务器的 `/opt/laboratory_management/` 目录中。

**方法 B：如果你已将代码上传到 Git 仓库**
```bash
git clone <你的Git仓库地址> /opt/laboratory_management
```

**检查文件结构**
执行 `ls /opt/laboratory_management`，你应该能看到 `manage.py` 和 `requirements.txt`。

### 3. 创建虚拟环境并安装依赖
```bash
cd /opt/laboratory_management

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 升级 pip
pip install --upgrade pip

# 安装项目依赖
pip install -r requirements.txt

# 【关键】安装 Gunicorn (如果 requirements.txt 里没有)
pip install gunicorn
```

---

## 第五步：项目配置与初始化

### 1. 检查配置
确保 `laboratory_management/settings.py` 中的数据库配置正确（代码库中应该已经配置好了，但确认一下无妨）。
主要确认 `DATABASES` 部分的 `USER` 是 `lab_user`，`PASSWORD` 是 `Ymzlj729928@`。

### 2. 数据库迁移
这步操作会根据代码在数据库中创建表。
```bash
# 确保还在虚拟环境中 (命令行前面有 (venv) 字样)
python manage.py makemigrations
python manage.py migrate
```

### 3. 收集静态文件
把 CSS/JS 图片等文件收集到统一目录，供 Nginx 使用。
```bash
python manage.py collectstatic --noinput
```

### 4. 创建管理员账号
用于登录后台。
```bash
python manage.py createsuperuser
# 按照提示输入用户名、邮箱（可留空）、密码
```

---

## 第六步：配置 Gunicorn (应用服务器)

我们需要 Gunicorn 来运行 Python 代码。我们将创建一个启动脚本。

1. **创建启动脚本**
```bash
nano /opt/laboratory_management/gunicorn_start.sh
```

2. **粘贴以下内容**：
```bash
#!/bin/bash

NAME="laboratory_management"
DJANGODIR=/opt/laboratory_management
SOCKFILE=/opt/laboratory_management/run/gunicorn.sock
NUM_WORKERS=3
DJANGO_SETTINGS_MODULE=laboratory_management.settings
DJANGO_WSGI_MODULE=laboratory_management.wsgi

echo "Starting $NAME"

# 激活虚拟环境
cd $DJANGODIR
source venv/bin/activate
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
export PYTHONPATH=$DJANGODIR:$PYTHONPATH

# 创建运行目录
RUNDIR=$(dirname $SOCKFILE)
test -d $RUNDIR || mkdir -p $RUNDIR

# 启动 Gunicorn
# 注意：不需要在这里指定 --user 和 --group，Systemd 会帮我们处理好
exec venv/bin/gunicorn ${DJANGO_WSGI_MODULE}:application \
  --name $NAME \
  --workers $NUM_WORKERS \
  --bind=unix:$SOCKFILE \
  --log-level=info \
  --log-file=-
```

3. **保存并退出**：按 `Ctrl + O`，回车保存，然后 `Ctrl + X` 退出。

4. **【关键】修复文件格式和权限**：
```bash
# 转换换行符（防止 Windows 编辑导致的 127 错误）
sudo dos2unix /opt/laboratory_management/gunicorn_start.sh

# 赋予执行权限
chmod +x /opt/laboratory_management/gunicorn_start.sh
```

5. **创建 Systemd 服务文件**：
```bash
sudo nano /etc/systemd/system/gunicorn_lab.service
```

6. **粘贴以下内容**（注意将 `User` 改为你的服务器用户名，如果不是 root）：
```ini
[Unit]
Description=Gunicorn instance to serve laboratory_management
After=network.target

[Service]
# 【关键】这里一定要改成你的实际用户名，如 ymz
User=ymz
Group=ymz
WorkingDirectory=/opt/laboratory_management
ExecStart=/opt/laboratory_management/gunicorn_start.sh
Restart=always

[Install]
WantedBy=multi-user.target
```

7. **启动 Gunicorn**：
```bash
sudo systemctl start gunicorn_lab
sudo systemctl enable gunicorn_lab
# 检查状态，一定要是 Active: active (running)
sudo systemctl status gunicorn_lab
```

---

## 第七步：配置 Nginx (Web服务器)

Nginx 负责接收用户的请求，并转发给 Gunicorn。

1. **创建 Nginx 配置文件**：
```bash
sudo nano /etc/nginx/sites-available/laboratory_management
```

2. **粘贴以下内容**：
```nginx
server {
    listen 80;
    server_name 192.168.187.128;

    # 静态文件
    location /static/ {
        alias /opt/laboratory_management/staticfiles/;
    }

    # 媒体文件（上传的文件）
    location /media/ {
        alias /opt/laboratory_management/media/;
    }

    # 主应用
    location / {
        proxy_pass http://unix:/opt/laboratory_management/run/gunicorn.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

3. **【关键】清理旧配置并启用新配置**：
```bash
# 删除默认配置和旧的配置
sudo rm /etc/nginx/sites-enabled/default
sudo rm /etc/nginx/sites-enabled/lab-mgmt
sudo rm /etc/nginx/sites-enabled/lab_project

# 建立新链接 (使用 -sf 强制覆盖)
sudo ln -sf /etc/nginx/sites-available/laboratory_management /etc/nginx/sites-enabled/
```

4. **【关键】修复目录权限** (防止 Nginx 报 404/502)
```bash
# 允许 Nginx 用户 (www-data) 访问我们的项目组
sudo chown -R ymz:www-data /opt/laboratory_management
sudo chmod -R 750 /opt/laboratory_management
sudo chmod -R 770 /opt/laboratory_management/run
```

5. **测试配置并重启 Nginx**：
```bash
sudo nginx -t
# 如果显示 successful，则继续
sudo systemctl restart nginx
```

---

## 第八步：配置防火墙

确保浏览器能访问 80 端口。

```bash
sudo ufw allow 80/tcp
sudo ufw allow 8000/tcp
sudo ufw reload
```

---

## 第九步：配置 Celery (异步任务)

如果你的系统有后台任务（如生成报告），需要配置 Celery。

1. **创建 Celery Worker 服务**：
```bash
sudo nano /etc/systemd/system/celery_worker.service
```

**内容**：
```ini
[Unit]
Description=Celery Worker
After=network.target

[Service]
Type=forking
User=root
Group=root
WorkingDirectory=/opt/laboratory_management
ExecStart=/opt/laboratory_management/venv/bin/celery -A laboratory_management multi start worker1 \
    --pidfile=/var/run/celery/worker1.pid \
    --logfile=/var/log/celery/worker1.log \
    --loglevel=INFO
ExecStop=/opt/laboratory_management/venv/bin/celery multi stopwait worker1 \
    --pidfile=/var/run/celery/worker1.pid
Restart=always

[Install]
WantedBy=multi-user.target
```

2. **创建日志和PID目录**：
```bash
sudo mkdir -p /var/run/celery /var/log/celery
sudo chown -R root:root /var/run/celery /var/log/celery
```

3. **启动 Celery**：
```bash
sudo systemctl start celery_worker
sudo systemctl enable celery_worker
```

---

## 第十步：完成与验证

1. **打开浏览器**：
   输入地址：`http://192.168.187.128`

2. **你应该能看到系统的登录页面**。
   使用之前创建的超级用户账号登录。

3. **如果还是看不到**：
   - 尝试 `curl -I http://192.168.187.128`
   - 强制刷新浏览器缓存 (Ctrl+F5)
   - 检查 Nginx 错误日志：`sudo tail -f /var/log/nginx/error.log`

---

## 常用维护命令

- **重启服务**（代码修改后）：
  ```bash
  sudo systemctl restart gunicorn_lab
  sudo systemctl restart celery_worker
  ```

- **查看日志**：
  ```bash
  # Nginx 访问日志
  tail -f /var/log/nginx/access.log
  # Nginx 错误日志
  tail -f /var/log/nginx/error.log
  # Gunicorn 日志
  journalctl -u gunicorn_lab -f
  ```

祝你部署顺利！
