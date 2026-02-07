"""
公共模块数据模型
"""
from django.db import models
from django.conf import settings


class SystemConfig(models.Model):
    """系统配置模型"""
    CONFIG_TYPE_CHOICES = [
        ('system', '系统配置'),
        ('email', '邮件配置'),
        ('notification', '通知配置'),
        ('security', '安全配置'),
        ('backup', '备份配置'),
    ]
    
    config_key = models.CharField(max_length=100, unique=True, verbose_name='配置键')
    config_value = models.TextField(verbose_name='配置值')
    config_type = models.CharField(
        max_length=20,
        choices=CONFIG_TYPE_CHOICES,
        verbose_name='配置类型'
    )
    description = models.TextField(verbose_name='配置描述')
    
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    is_editable = models.BooleanField(default=True, verbose_name='是否可编辑')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'system_config'
        verbose_name = '系统配置'
        verbose_name_plural = '系统配置'

    def __str__(self):
        return f"{self.config_key}: {self.config_value[:50]}"


class Notification(models.Model):
    """通知模型"""
    NOTIFICATION_TYPE_CHOICES = [
        ('info', '信息'),
        ('warning', '警告'),
        ('error', '错误'),
        ('success', '成功'),
    ]
    
    NOTIFICATION_CATEGORY_CHOICES = [
        ('task', '任务通知'),
        ('equipment', '设备通知'),
        ('maintenance', '维护通知'),
        ('system', '系统通知'),
        ('report', '报表通知'),
    ]
    
    title = models.CharField(max_length=200, verbose_name='通知标题')
    content = models.TextField(verbose_name='通知内容')
    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPE_CHOICES,
        default='info',
        verbose_name='通知类型'
    )
    category = models.CharField(
        max_length=20,
        choices=NOTIFICATION_CATEGORY_CHOICES,
        verbose_name='通知分类'
    )
    
    # 接收人
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='接收人'
    )
    
    # 状态
    is_read = models.BooleanField(default=False, verbose_name='是否已读')
    read_at = models.DateTimeField(null=True, blank=True, verbose_name='阅读时间')
    
    # 关联对象
    related_object_type = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='关联对象类型'
    )
    related_object_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='关联对象ID'
    )
    
    # 发送方式
    send_email = models.BooleanField(default=False, verbose_name='是否发送邮件')
    email_sent = models.BooleanField(default=False, verbose_name='邮件是否已发送')
    email_sent_at = models.DateTimeField(null=True, blank=True, verbose_name='邮件发送时间')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'notifications'
        verbose_name = '通知'
        verbose_name_plural = '通知'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.recipient.username}"

    def mark_as_read(self):
        """标记为已读"""
        from django.utils import timezone
        self.is_read = True
        self.read_at = timezone.now()
        self.save()


class AuditLog(models.Model):
    """审计日志模型"""
    ACTION_CHOICES = [
        ('create', '创建'),
        ('update', '更新'),
        ('delete', '删除'),
        ('login', '登录'),
        ('logout', '登出'),
        ('view', '查看'),
        ('export', '导出'),
        ('import', '导入'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='操作用户'
    )
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        verbose_name='操作类型'
    )
    
    # 操作对象
    object_type = models.CharField(max_length=50, verbose_name='对象类型')
    object_id = models.CharField(max_length=50, blank=True, verbose_name='对象ID')
    object_repr = models.CharField(max_length=200, verbose_name='对象描述')
    
    # 操作详情
    changes = models.JSONField(null=True, blank=True, verbose_name='变更内容')
    description = models.TextField(verbose_name='操作描述')
    
    # 请求信息
    ip_address = models.GenericIPAddressField(verbose_name='IP地址')
    user_agent = models.TextField(verbose_name='用户代理')
    request_path = models.CharField(max_length=500, verbose_name='请求路径')
    request_method = models.CharField(max_length=10, verbose_name='请求方法')
    
    # 结果
    success = models.BooleanField(default=True, verbose_name='是否成功')
    error_message = models.TextField(blank=True, verbose_name='错误信息')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='操作时间')

    class Meta:
        db_table = 'audit_logs'
        verbose_name = '审计日志'
        verbose_name_plural = '审计日志'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} - {self.get_action_display()} - {self.object_type}"


class FileUpload(models.Model):
    """文件上传记录模型"""
    FILE_TYPE_CHOICES = [
        ('document', '文档'),
        ('image', '图片'),
        ('data', '数据文件'),
        ('report', '报表'),
        ('manual', '手册'),
        ('certificate', '证书'),
    ]
    
    original_name = models.CharField(max_length=255, verbose_name='原始文件名')
    file = models.FileField(upload_to='uploads/%Y/%m/%d/', verbose_name='文件')
    file_type = models.CharField(
        max_length=20,
        choices=FILE_TYPE_CHOICES,
        verbose_name='文件类型'
    )
    file_size = models.BigIntegerField(verbose_name='文件大小(字节)')
    mime_type = models.CharField(max_length=100, verbose_name='MIME类型')
    
    # 上传信息
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='上传人'
    )
    
    # 关联对象
    related_object_type = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='关联对象类型'
    )
    related_object_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='关联对象ID'
    )
    
    # 访问控制
    is_public = models.BooleanField(default=False, verbose_name='是否公开')
    download_count = models.IntegerField(default=0, verbose_name='下载次数')
    
    description = models.TextField(blank=True, verbose_name='文件描述')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='上传时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'file_uploads'
        verbose_name = '文件上传记录'
        verbose_name_plural = '文件上传记录'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.original_name} - {self.uploaded_by.username}"

    @property
    def file_size_human(self):
        """人类可读的文件大小"""
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"


class SystemBackup(models.Model):
    """系统备份记录模型"""
    BACKUP_TYPE_CHOICES = [
        ('full', '完整备份'),
        ('incremental', '增量备份'),
        ('differential', '差异备份'),
    ]
    
    BACKUP_STATUS_CHOICES = [
        ('running', '备份中'),
        ('completed', '已完成'),
        ('failed', '备份失败'),
    ]
    
    backup_name = models.CharField(max_length=200, verbose_name='备份名称')
    backup_type = models.CharField(
        max_length=20,
        choices=BACKUP_TYPE_CHOICES,
        verbose_name='备份类型'
    )
    
    # 备份配置
    backup_config = models.JSONField(verbose_name='备份配置')
    backup_path = models.CharField(max_length=500, verbose_name='备份路径')
    
    # 备份状态
    status = models.CharField(
        max_length=20,
        choices=BACKUP_STATUS_CHOICES,
        default='running',
        verbose_name='备份状态'
    )
    
    # 备份信息
    file_count = models.IntegerField(default=0, verbose_name='文件数量')
    backup_size = models.BigIntegerField(default=0, verbose_name='备份大小(字节)')
    duration = models.DurationField(null=True, blank=True, verbose_name='备份耗时')
    
    # 执行信息
    started_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='执行人'
    )
    started_at = models.DateTimeField(verbose_name='开始时间')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='完成时间')
    
    error_message = models.TextField(blank=True, verbose_name='错误信息')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'system_backups'
        verbose_name = '系统备份记录'
        verbose_name_plural = '系统备份记录'
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.backup_name} - {self.started_at.strftime('%Y-%m-%d %H:%M')}"

    @property
    def backup_size_human(self):
        """人类可读的备份大小"""
        size = self.backup_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"