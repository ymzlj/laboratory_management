"""
Django settings for laboratory_management project.
试验室管理系统配置文件

包含内容：
1. 基础路径和密钥配置
2. 允许访问的主机配置
3. 应用注册 (Django内置, 第三方, 本地应用)
4. 中间件配置
5. 模板系统配置
6. WSGI/ASGI 应用入口
7. 数据库配置 (支持 MySQL 和 SQLite 切换)
8. 缓存配置 (Redis)
9. 密码验证策略
10. 用户模型与认证后端
11. 国际化与时区
12. 静态文件与媒体文件配置
13. Django REST Framework 配置
14. CORS 和 CSRF 安全配置
15. 日志系统配置
16. 文件上传与会话设置
17. Celery 异步任务配置
"""

import os
from pathlib import Path

# ==============================================================================
# 1. 基础配置 (Base Configuration)
# ==============================================================================

# 项目根目录路径: BASE_DIR / 'subdir'
BASE_DIR = Path(__file__).resolve().parent.parent

# 安全密钥: 生产环境请务必修改并保密
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-u%%dt(e-sd!09=9e-t@z&l+pmaz$mh1lfi1@639b4z2xjzi0p-'

# 调试模式: 生产环境请设置为 False
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# 允许访问的主机列表 (局域网部署时需要添加服务器IP)
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '0.0.0.0',
    '192.168.8.215',
    '192.168.8.225',  # 新增的局域网IP
    '192.168.187.128', # 虚拟机NAT模式IP
    '192.168.8.225',   # 虚拟机桥接模式IP
    'www.jksys.com',   # 自定义域名
    '.jksys.com',      # 允许子域名
    '192.168.8.209',   # User IP
]


# ==============================================================================
# 2. 应用注册 (Application Definition)
# ==============================================================================

# Django 内置应用
DJANGO_APPS = [
    'django.contrib.admin',        # 管理后台
    'django.contrib.auth',         # 认证系统
    'django.contrib.contenttypes', # 内容类型框架
    'django.contrib.sessions',     # 会话管理
    'django.contrib.messages',     # 消息框架
    'django.contrib.staticfiles',  # 静态文件管理
]

# 第三方扩展应用
THIRD_PARTY_APPS = [
    'rest_framework',           # Web API 框架
    'rest_framework.authtoken', # Token 认证
    'corsheaders',              # 跨域资源共享
    'crispy_forms',             # 表单美化
    'crispy_bootstrap4',        # Bootstrap4 支持
    'guardian',                 # 对象级权限控制
    'django_celery_beat',       # 定时任务调度
    'django_celery_results',    # 任务结果存储
]

# 本地自定义应用
LOCAL_APPS = [
    'apps.users',      # 用户与角色管理
    'apps.tasks',      # 试验任务管理
    'apps.test_data',  # 试验数据管理
    'apps.equipment',  # 设备管理
    'apps.tooling',    # 工装管理
    'apps.tools',      # 工具管理
    'apps.reports',    # 报告生成
    'apps.common',     # 通用组件
]

# 汇总所有安装的应用
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS


# ==============================================================================
# 3. 中间件配置 (Middleware)
# ==============================================================================
# 注意：中间件的顺序非常重要，不可随意调整
MIDDLEWARE = [
    'django.middleware.gzip.GZipMiddleware',                      # GZip 压缩
    'corsheaders.middleware.CorsMiddleware',                      # CORS 跨域处理 (必须在 CommonMiddleware 之前)
    'django.middleware.security.SecurityMiddleware',              # 安全中间件
    'whitenoise.middleware.WhiteNoiseMiddleware',                 # 静态文件服务
    'django.contrib.sessions.middleware.SessionMiddleware',       # 会话管理
    'django.middleware.locale.LocaleMiddleware',                  # 国际化支持
    'django.middleware.common.CommonMiddleware',                  # 通用处理
    'django.middleware.csrf.CsrfViewMiddleware',                  # CSRF 防护
    'django.contrib.auth.middleware.AuthenticationMiddleware',    # 用户认证
    'django.contrib.messages.middleware.MessageMiddleware',       # 消息处理
    'django.middleware.clickjacking.XFrameOptionsMiddleware',     # 点击劫持防护
]

# 根路由配置
ROOT_URLCONF = 'laboratory_management.urls'


# ==============================================================================
# 4. 模板系统配置 (Templates)
# ==============================================================================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], # 全局模板目录
        'APP_DIRS': True,                 # 自动查找应用下的 templates 目录
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
            ],
            # 添加模板缓存选项以提高性能（仅在生产环境）
        },
    },
]

# 在生产环境(DEBUG=False)中启用模板缓存以提高性能
if not DEBUG:
    TEMPLATES[0]['OPTIONS']['loaders'] = [
        ('django.template.loaders.cached.Loader', [
            'django.template.loaders.filesystem.Loader',
            'django.template.loaders.app_directories.Loader',
        ]),
    ]
    # 禁用APP_DIRS以使用自定义加载器
    TEMPLATES[0]['APP_DIRS'] = False
else:
    # 开发环境确保启用 APP_DIRS
    TEMPLATES[0]['APP_DIRS'] = True


# WSGI 应用入口
WSGI_APPLICATION = 'laboratory_management.wsgi.application'


# ==============================================================================
# 5. 数据库配置 (Database)
# ==============================================================================
# 支持通过环境变量 DB_USE_MYSQL 控制数据库类型
# 1: 使用 MySQL (生产环境推荐)
# 0: 使用 SQLite3 (开发环境默认)

# 修改默认为 '0'，即默认启用 SQLite
DB_USE_MYSQL = os.getenv('DB_USE_MYSQL', '1') == '1'

if DB_USE_MYSQL:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.getenv('DB_NAME', 'laboratory_test_management'),
            'USER': os.getenv('DB_USER', 'root'),
            'PASSWORD': os.getenv('DB_PASSWORD', '123456'),
            'HOST': os.getenv('DB_HOST', 'localhost'),
            'PORT': os.getenv('DB_PORT', '3306'),
            'OPTIONS': {
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            },
        }
    }
else:
    # 默认 SQLite 配置
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / os.getenv('DB_SQLITE_NAME', 'db.sqlite3'),
        }
    }


# ==============================================================================
# 6. 缓存配置 (Cache)
# ==============================================================================
# 使用本地内存缓存（开发环境）
# 生产环境建议使用 Redis 或 Memcached
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
        }
    }
}


# ==============================================================================
# 7. 密码验证策略 (Password Validation)
# ==============================================================================
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# ==============================================================================
# 8. 认证后端 (Authentication Backends)
# ==============================================================================
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',   # 默认认证
    'guardian.backends.ObjectPermissionBackend',   # 对象级权限认证
]

# 自定义用户模型
AUTH_USER_MODEL = 'users.User'


# ==============================================================================
# 9. 国际化与时区 (Internationalization)
# ==============================================================================
LANGUAGE_CODE = 'zh-hans'   # 简体中文
TIME_ZONE = 'Asia/Shanghai' # 上海时间
USE_I18N = True             # 启用国际化
USE_TZ = True               # 启用时区支持


# ==============================================================================
# 10. 静态文件与媒体文件 (Static & Media)
# ==============================================================================
# 静态文件 (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles' # collectstatic 收集目录
STATICFILES_DIRS = [
    BASE_DIR / 'static', # 开发时静态文件目录
]

# 媒体文件 (用户上传的文件)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# WhiteNoise 配置 (用于生产环境服务静态文件)
WHITENOISE_USE_FINDERS = True
WHITENOISE_MAX_AGE = 31536000

# 默认主键类型
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ==============================================================================
# 11. Django REST Framework 配置
# ==============================================================================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',   # Token 认证
        'rest_framework.authentication.SessionAuthentication', # Session 认证
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated', # 默认需要登录
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20, # 默认每页20条
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend', # 过滤
        'rest_framework.filters.SearchFilter',               # 搜索
        'rest_framework.filters.OrderingFilter',             # 排序
    ],
}


# ==============================================================================
# 12. CORS 和 CSRF 安全配置
# ==============================================================================
# CORS 设置: 内部局域网环境下允许所有来源
CORS_ALLOW_ALL_ORIGINS = True

# CSRF 信任源配置: 局域网访问时必须配置对应的 IP
CSRF_TRUSTED_ORIGINS = [
    "http://localhost",
    "http://localhost:8000",
    "http://127.0.0.1",
    "http://127.0.0.1:8000",
    "http://192.168.8.215",
    "http://192.168.8.215:8000",
    "http://192.168.8.225",
    "http://192.168.8.225:8000",
    "http://192.168.187.128",
    "http://www.jksys.com",
    "https://www.jksys.com",
    "http://www.jksys.com:8000",
    "http://192.168.8.209",
    "http://192.168.8.209:8000",
]


# ==============================================================================
# 13. 第三方插件配置
# ==============================================================================
# Crispy Forms (Bootstrap4 风格)
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap4"
CRISPY_TEMPLATE_PACK = "bootstrap4"


# ==============================================================================
# 14. 日志系统配置 (Logging)
# ==============================================================================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}


# ==============================================================================
# 15. 文件上传与会话设置
# ==============================================================================
FILE_UPLOAD_MAX_MEMORY_SIZE = 100 * 1024 * 1024
DATA_UPLOAD_MAX_MEMORY_SIZE = 200 * 1024 * 1024
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10000 # 增加表单字段数量限制 (默认1000)

# Session 设置
SESSION_COOKIE_AGE = 86400        # Session 有效期: 24小时
SESSION_SAVE_EVERY_REQUEST = True # 每次请求都保存 Session
SESSION_EXPIRE_AT_BROWSER_CLOSE = True  # 关闭浏览器时清除会话

# 登录/登出跳转 URL
LOGIN_URL = '/users/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/users/login/'


# ==============================================================================
# 16. Celery 异步任务配置
# ==============================================================================
CELERY_BROKER_URL = 'redis://localhost:6379/0'      # 消息中间件 (Broker)
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'  # 结果存储 (Backend)
CELERY_ACCEPT_CONTENT = ['json']    # 允许的内容类型
CELERY_TASK_SERIALIZER = 'json'     # 任务序列化格式
CELERY_RESULT_SERIALIZER = 'json'   # 结果序列化格式
CELERY_TIMEZONE = TIME_ZONE         # 时区
