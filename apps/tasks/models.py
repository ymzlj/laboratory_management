"""
试验任务模块数据模型
"""
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


class TestType(models.Model):
    """试验类型模型"""
    name = models.CharField(max_length=100, verbose_name='试验类型名称')
    code = models.CharField(max_length=20, unique=True, verbose_name='试验类型代码')
    description = models.TextField(blank=True, verbose_name='试验类型描述')
    
    # 试验类型层级
    LEVEL_CHOICES = (
        (1, '总试验类型'),
        (2, '分试验类型'),
    )
    level_type = models.IntegerField(choices=LEVEL_CHOICES, default=1, verbose_name='类型级别')
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='sub_types', 
        verbose_name='所属总类型'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'test_types'
        verbose_name = '试验类型'
        verbose_name_plural = '试验类型'

    def __str__(self):
        return self.name

    def get_all_fields(self):
        """
        获取该试验类型的所有字段配置，包含从父类型继承的字段。
        如果有冲突（如同名代码），子类型的配置覆盖父类型。
        返回已排序的字段列表。
        性能优化：使用select_related和数据库层面排序，添加缓存机制
        """
        from django.core.cache import cache
        
        # 构建缓存键 - 需包含父级的更新时间以处理继承字段的变更
        key_parts = [f'{self.id}_{self.updated_at.timestamp()}']
        if self.parent:
            key_parts.append(f'{self.parent.id}_{self.parent.updated_at.timestamp()}')
            
        cache_key = f'test_type_fields_v2_{"_".join(key_parts)}'
        
        # 尝试从缓存获取
        cached_fields = cache.get(cache_key)
        if cached_fields is not None:
            return cached_fields
        
        fields_map = {}
        
        #1. 获取父类型字段（使用select_related优化）
        if self.parent:
            parent_fields = self.parent.custom_fields.filter(is_active=True).select_related('test_type').order_by('order', 'id')
            for field in parent_fields:
                fields_map[field.field_code] = field
        
        #2. 获取当前类型字段（覆盖父类型，使用select_related优化）
        current_fields = self.custom_fields.filter(is_active=True).select_related('test_type').order_by('order', 'id')
        for field in current_fields:
            fields_map[field.field_code] = field
        
        #3. 排序：按order和id排序
        # 注意：这里我们无法直接使用QuerySet的order_by，因为是混合的列表
        result = sorted(fields_map.values(), key=lambda x: (x.order, x.id))
        
        # 缓存结果（缓存5分钟）
        cache.set(cache_key, result, timeout=300)
        
        return result



class TestTypeField(models.Model):
    """试验类型字段配置模型 - 用于动态配置试验数据录入字段"""
    
    # 字段类型选择
    FIELD_TYPE_CHOICES = [
        ('text', '文本'),
        ('textarea', '多行文本'),
        ('number', '数字'),
        ('decimal', '小数'),
        ('date', '日期'),
        ('datetime', '日期时间'),
        ('select', '下拉选择'),
        ('checkbox', '复选框'),
        ('file', '文件上传'),
    ]
    
    test_type = models.ForeignKey(
        TestType,
        on_delete=models.CASCADE,
        related_name='custom_fields',
        verbose_name='试验类型'
    )
    field_name = models.CharField(max_length=100, verbose_name='字段名称')  # 显示名称
    field_code = models.CharField(max_length=50, verbose_name='字段代码')  # 用于存储的键名
    field_type = models.CharField(
        max_length=20,
        choices=FIELD_TYPE_CHOICES,
        default='text',
        verbose_name='字段类型'
    )
    field_options = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='字段选项',
        help_text='对于下拉选择类型，存储选项列表；其他配置如最大值、最小值等'
    )
    is_required = models.BooleanField(default=False, verbose_name='是否必填')
    default_value = models.CharField(max_length=200, blank=True, verbose_name='默认值')
    placeholder = models.CharField(max_length=200, blank=True, verbose_name='提示文本')
    help_text = models.CharField(max_length=500, blank=True, verbose_name='帮助文本')
    order = models.IntegerField(default=0, verbose_name='显示顺序')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    is_batch_input_enabled = models.BooleanField(default=True, verbose_name='启用批量录入', help_text='开启后，该字段将出现在批量数据录入界面；关闭后，仅在子任务详情中单独显示')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'test_type_fields'
        verbose_name = '试验类型字段配置'
        verbose_name_plural = '试验类型字段配置'
        ordering = ['test_type', 'order', 'id']
        unique_together = [['test_type', 'field_code']]  # 同一试验类型下字段代码唯一
    
    def __str__(self):
        return f"{self.test_type.name} - {self.field_name}"


class PriorityType(models.Model):
    """优先级类型模型"""
    name = models.CharField(max_length=50, verbose_name='优先级名称')
    level = models.IntegerField(unique=True, verbose_name='优先级等级')
    description = models.TextField(blank=True, verbose_name='优先级描述')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'priority_types'
        verbose_name = '优先级类型'
        verbose_name_plural = '优先级类型'
        ordering = ['level']

    def __str__(self):
        return self.name


class TaskStatus(models.Model):
    """任务状态模型"""
    name = models.CharField(max_length=50, verbose_name='状态名称')
    code = models.CharField(max_length=20, unique=True, verbose_name='状态代码')
    description = models.TextField(blank=True, verbose_name='状态描述')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'task_status'
        verbose_name = '任务状态'
        verbose_name_plural = '任务状态'

    def __str__(self):
        return self.name


class TestTask(models.Model):
    """试验任务模型"""
    # 基本信息字段
    task_number = models.CharField(max_length=50, unique=True, verbose_name='任务编号', help_text='系统自动生成的唯一任务编号，格式：TASK-YYYYMMDD-序号')
    task_name = models.CharField(max_length=200, verbose_name='任务名称', help_text='试验任务的名称，简明扼要地描述试验目的')
    
    # 产品相关字段
    product_name = models.CharField(max_length=50, verbose_name='产品名称', blank=True, default='', help_text='需要进行试验的产品名称')
    product_model = models.CharField(max_length=20, verbose_name='产品型号', blank=True, default='', help_text='产品的具体型号规格')
    
    # 关联字段
    test_type = models.ForeignKey(
        TestType, 
        on_delete=models.CASCADE, 
        verbose_name='试验类型',
        help_text='选择试验类型，决定试验的具体流程和要求'
    )
    priority = models.ForeignKey(
        PriorityType, 
        on_delete=models.CASCADE, 
        verbose_name='优先级',
        help_text='任务优先级，影响任务的处理顺序和资源分配'
    )
    status = models.ForeignKey(
        TaskStatus, 
        on_delete=models.CASCADE, 
        verbose_name='任务状态',
        help_text='当前任务的状态，如待处理、进行中、待审核等'
    )
    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='requested_tasks',
        verbose_name='申请人',
        help_text='创建此任务的用户'
    )
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks',
        verbose_name='负责人',
        help_text='负责执行此任务的工程师或技术人员'
    )
    
    # 申请人联系信息
    requester_name = models.CharField(max_length=100, blank=True, default='', verbose_name='申请人姓名', help_text='申请人的真实姓名')
    requester_phone = models.CharField(max_length=20, blank=True, default='', verbose_name='申请人手机号', help_text='申请人的联系电话')
    requester_department = models.CharField(max_length=100, blank=True, default='', verbose_name='申请人部门', help_text='申请人所在的部门或单位')
    
    # 任务描述
    description = models.TextField(verbose_name='任务描述', blank=True, help_text='对试验任务的详细描述和要求')
    
    # 试验过程描述（新增字段）
    test_process_description = models.TextField(
        verbose_name='试验过程描述', 
        blank=True, 
        default='',
        help_text='记录试验过程中的详细步骤、观察结果和关键参数'
    )
    
    # 试验文档字段
    test_outline = models.TextField(blank=True, verbose_name='试验大纲', help_text='试验的具体大纲和要求，文本格式')
    test_report = models.TextField(blank=True, verbose_name='试验报告', help_text='试验结果报告，文本格式（历史遗留字段）')
    
    # 试验文档文件
    test_outline_file = models.FileField(
        upload_to='test_outlines/', 
        blank=True, 
        null=True,
        verbose_name='试验大纲文件',
        help_text='上传试验大纲文件，支持PDF、Word等格式'
    )
    test_report_file = models.FileField(
        upload_to='test_reports/', 
        blank=True, 
        null=True,
        verbose_name='试验报告文件',
        help_text='上传试验报告文件，支持PDF、Word等格式（历史遗留字段）'
    )
    
    # 时间字段
    start_date = models.DateField(verbose_name='开始日期', help_text='计划开始执行任务的日期')
    end_date = models.DateField(verbose_name='结束日期', help_text='计划完成任务的日期')
    actual_start_date = models.DateField(null=True, blank=True, verbose_name='实际开始日期', help_text='任务实际开始执行的日期')
    actual_end_date = models.DateField(null=True, blank=True, verbose_name='实际结束日期', help_text='任务实际完成的日期')
    
    # 状态相关字段
    rejection_reason = models.TextField(blank=True, default='', verbose_name='拒绝理由', help_text='当任务被拒绝或退回时填写的理由说明')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'test_tasks'
        verbose_name = '试验任务'
        verbose_name_plural = '试验任务'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['test_type', 'status']),
            models.Index(fields=['status', 'end_date']),  # 用于查询未完成且逾期的任务
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.task_number} - {self.task_name}"

    @property
    def is_overdue(self):
        """判断任务是否逾期"""
        from django.utils import timezone
        # 审核完成、已完成和已取消的任务不算逾期
        if self.status.code in ['reviewed', 'completed', 'cancelled']:
            return False
        return timezone.now().date() > self.end_date

    @property
    def progress_percentage(self):
        """计算任务进度百分比"""
        if self.status.code in ['reviewed', 'completed']:
            # 审核完成和已完成都是100%
            return 100
        elif self.status.code == 'pending_review':
            # 待审核状态显示90%
            return 90
        elif self.status.code == 'in_progress':
            return 50
        elif self.status.code == 'pending':
            return 0
        else:
            return 0


class TestTaskProcessHistory(models.Model):
    """试验过程描述历史记录"""
    task = models.ForeignKey(
        TestTask,
        on_delete=models.CASCADE,
        related_name='process_history',
        verbose_name='试验任务'
    )
    content = models.TextField(verbose_name='描述内容')
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='修改人'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='修改时间')

    class Meta:
        db_table = 'test_task_process_history'
        verbose_name = '试验过程历史'
        verbose_name_plural = '试验过程历史'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.task.task_number} - {self.created_at}"


class TestTaskReport(models.Model):
    """试验任务报告文件模型"""
    task = models.ForeignKey(
        TestTask,
        on_delete=models.CASCADE,
        related_name='reports',
        verbose_name='试验任务'
    )
    file = models.FileField(upload_to='task_reports/%Y/%m/%d/', verbose_name='报告文件')
    name = models.CharField(max_length=255, verbose_name='文件名')
    size = models.PositiveIntegerField(verbose_name='文件大小(字节)')
    uploader = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='上传人'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='上传时间')

    class Meta:
        db_table = 'test_task_reports'
        verbose_name = '试验任务报告'
        verbose_name_plural = '试验任务报告'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class SubTask(models.Model):
    """子任务模型 - 由主任务分解而来"""
    parent_task = models.ForeignKey(
        TestTask,
        on_delete=models.CASCADE,
        related_name='subtasks',
        verbose_name='主任务'
    )
    subtask_number = models.CharField(max_length=50, unique=True, verbose_name='子任务编号')
    subtask_name = models.CharField(max_length=200, verbose_name='子任务名称')
    test_type = models.ForeignKey(
        TestType,
        on_delete=models.CASCADE,
        verbose_name='试验类型'
    )
    status = models.ForeignKey(
        TaskStatus,
        on_delete=models.CASCADE,
        verbose_name='状态'
    )
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_subtasks',
        verbose_name='负责人'
    )
    description = models.TextField(blank=True, verbose_name='子任务描述')
    start_date = models.DateField(verbose_name='开始日期')
    end_date = models.DateField(verbose_name='结束日期')
    actual_start_date = models.DateField(null=True, blank=True, verbose_name='实际开始日期')
    actual_end_date = models.DateField(null=True, blank=True, verbose_name='实际结束日期')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'sub_tasks'
        verbose_name = '子任务'
        verbose_name_plural = '子任务'
        ordering = ['subtask_number']
        indexes = [
            models.Index(fields=['test_type', 'status']),
            models.Index(fields=['parent_task']),
        ]

    def __str__(self):
        return f"{self.subtask_number} - {self.subtask_name}"

    @property
    def is_overdue(self):
        """判断子任务是否逾期"""
        from django.utils import timezone
        if self.status.code in ['completed', 'cancelled']:
            return False
        return timezone.now().date() > self.end_date


class SubTaskData(models.Model):
    """子任务数据录入模型"""
    subtask = models.OneToOneField(
        SubTask,
        on_delete=models.CASCADE,
        related_name='test_data',
        verbose_name='子任务'
    )
    # 通用数据字段
    test_conditions = models.TextField(blank=True, verbose_name='试验条件')
    test_method = models.TextField(blank=True, verbose_name='试验方法')
    test_equipment = models.TextField(blank=True, verbose_name='试验设备')
    test_data = models.JSONField(default=dict, blank=True, verbose_name='试验数据')
    meta_data = models.JSONField(default=dict, blank=True, verbose_name='元数据', help_text='存储非批量录入的自定义字段数据')
    test_result = models.TextField(blank=True, verbose_name='试验结果')
    test_conclusion = models.TextField(blank=True, verbose_name='试验结论')
    remarks = models.TextField(blank=True, verbose_name='备注')
    
    # 文件附件
    data_file = models.FileField(
        upload_to='subtask_data/',
        blank=True,
        null=True,
        verbose_name='数据文件'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'subtask_data'
        verbose_name = '子任务数据'
        verbose_name_plural = '子任务数据'

    def __str__(self):
        return f"数据 - {self.subtask.subtask_number}"


# 信号处理：当字段配置变更时，更新试验类型的updated_at，从而使缓存失效
@receiver(post_save, sender=TestTypeField)
@receiver(post_delete, sender=TestTypeField)
def update_test_type_timestamp(sender, instance, **kwargs):
    # 更新所属试验类型的更新时间
    # 注意：使用 save() 会自动更新 auto_now=True 的字段 (updated_at)
    if instance.test_type:
        instance.test_type.save()
