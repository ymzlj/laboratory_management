"""
报表模块数据模型
"""
from django.db import models
from django.conf import settings


class ReportTemplate(models.Model):
    """报表模板模型"""
    REPORT_TYPE_CHOICES = [
        ('task_summary', '任务汇总报表'),
        ('equipment_usage', '设备使用报表'),
        ('test_data_analysis', '试验数据分析报表'),
        ('maintenance_schedule', '维护计划报表'),
        ('resource_utilization', '资源利用率报表'),
        ('quality_control', '质量控制报表'),
    ]
    
    name = models.CharField(max_length=200, verbose_name='模板名称')
    report_type = models.CharField(
        max_length=30,
        choices=REPORT_TYPE_CHOICES,
        verbose_name='报表类型'
    )
    description = models.TextField(verbose_name='模板描述')
    
    # 模板配置
    template_config = models.JSONField(verbose_name='模板配置')
    sql_query = models.TextField(blank=True, verbose_name='SQL查询语句')
    
    # 输出格式
    output_formats = models.JSONField(
        default=list,
        verbose_name='支持的输出格式'
    )  # ['pdf', 'excel', 'html']
    
    # 权限控制
    is_public = models.BooleanField(default=False, verbose_name='是否公开')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='创建人'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'report_templates'
        verbose_name = '报表模板'
        verbose_name_plural = '报表模板'

    def __str__(self):
        return self.name


class GeneratedReport(models.Model):
    """生成的报表模型"""
    REPORT_STATUS_CHOICES = [
        ('generating', '生成中'),
        ('completed', '已完成'),
        ('failed', '生成失败'),
    ]
    
    template = models.ForeignKey(
        ReportTemplate,
        on_delete=models.CASCADE,
        verbose_name='报表模板'
    )
    report_name = models.CharField(max_length=200, verbose_name='报表名称')
    
    # 生成参数
    generation_params = models.JSONField(verbose_name='生成参数')
    date_range_start = models.DateField(verbose_name='数据起始日期')
    date_range_end = models.DateField(verbose_name='数据结束日期')
    
    # 生成状态
    status = models.CharField(
        max_length=20,
        choices=REPORT_STATUS_CHOICES,
        default='generating',
        verbose_name='生成状态'
    )
    
    # 文件信息
    output_format = models.CharField(max_length=10, verbose_name='输出格式')
    file_path = models.FileField(
        upload_to='generated_reports/',
        blank=True,
        null=True,
        verbose_name='报表文件'
    )
    file_size = models.BigIntegerField(default=0, verbose_name='文件大小(字节)')
    
    # 生成信息
    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='生成人'
    )
    generation_time = models.DurationField(
        null=True,
        blank=True,
        verbose_name='生成耗时'
    )
    error_message = models.TextField(blank=True, verbose_name='错误信息')
    
    # 访问控制
    is_public = models.BooleanField(default=False, verbose_name='是否公开')
    download_count = models.IntegerField(default=0, verbose_name='下载次数')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'generated_reports'
        verbose_name = '生成的报表'
        verbose_name_plural = '生成的报表'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.report_name} - {self.created_at.strftime('%Y-%m-%d')}"


class ReportSchedule(models.Model):
    """报表定时任务模型"""
    SCHEDULE_TYPE_CHOICES = [
        ('daily', '每日'),
        ('weekly', '每周'),
        ('monthly', '每月'),
        ('quarterly', '每季度'),
        ('yearly', '每年'),
    ]
    
    template = models.ForeignKey(
        ReportTemplate,
        on_delete=models.CASCADE,
        verbose_name='报表模板'
    )
    schedule_name = models.CharField(max_length=200, verbose_name='任务名称')
    
    # 调度配置
    schedule_type = models.CharField(
        max_length=20,
        choices=SCHEDULE_TYPE_CHOICES,
        verbose_name='调度类型'
    )
    schedule_time = models.TimeField(verbose_name='执行时间')
    schedule_config = models.JSONField(verbose_name='调度配置')
    
    # 生成参数
    generation_params = models.JSONField(verbose_name='生成参数')
    output_format = models.CharField(max_length=10, verbose_name='输出格式')
    
    # 通知设置
    email_recipients = models.JSONField(
        default=list,
        verbose_name='邮件接收人'
    )
    notification_enabled = models.BooleanField(
        default=True,
        verbose_name='是否启用通知'
    )
    
    # 状态
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    last_run_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='上次执行时间'
    )
    next_run_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='下次执行时间'
    )
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='创建人'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'report_schedules'
        verbose_name = '报表定时任务'
        verbose_name_plural = '报表定时任务'

    def __str__(self):
        return f"{self.schedule_name} - {self.get_schedule_type_display()}"


class ReportAccess(models.Model):
    """报表访问记录模型"""
    ACTION_CHOICES = [
        ('view', '查看'),
        ('download', '下载'),
        ('share', '分享'),
    ]
    
    report = models.ForeignKey(
        GeneratedReport,
        on_delete=models.CASCADE,
        verbose_name='报表'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='用户'
    )
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        verbose_name='操作类型'
    )
    
    # 访问信息
    ip_address = models.GenericIPAddressField(verbose_name='IP地址')
    user_agent = models.TextField(verbose_name='用户代理')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='访问时间')

    class Meta:
        db_table = 'report_access'
        verbose_name = '报表访问记录'
        verbose_name_plural = '报表访问记录'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.get_action_display()} - {self.report.report_name}"