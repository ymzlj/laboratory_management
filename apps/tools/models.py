"""
工具管理模块数据模型
"""
from django.db import models
from django.conf import settings


class Tool(models.Model):
    """工具模型"""
    TOOL_STATUS_CHOICES = [
        ('available', '可用'),
        ('borrowed', '已借出'),
        ('maintenance', '维护中'),
        ('lost', '丢失'),
        ('retired', '已报废'),
    ]
    
    tool_id = models.CharField(max_length=50, unique=True, verbose_name='工具编号')
    name = models.CharField(max_length=200, verbose_name='工具名称')
    type = models.CharField(max_length=100, verbose_name='工具类型')
    model = models.CharField(max_length=100, verbose_name='工具型号')
    manufacturer = models.CharField(max_length=100, verbose_name='制造商')
    
    # 工具基本信息
    purchase_date = models.DateField(verbose_name='采购日期', null=True, blank=True)
    purchase_price = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        verbose_name='采购价格',
        null=True,
        blank=True
    )
    
    # 工具状态
    status = models.CharField(
        max_length=20, 
        choices=TOOL_STATUS_CHOICES, 
        default='available',
        verbose_name='工具状态'
    )
    location = models.CharField(max_length=100, verbose_name='存放位置')
    responsible_person = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='负责人'
    )
    
    # 技术参数
    specifications = models.TextField(verbose_name='技术规格')
    material = models.CharField(max_length=100, blank=True, verbose_name='材质')
    dimensions = models.CharField(max_length=200, blank=True, verbose_name='尺寸规格')
    weight = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name='重量(kg)'
    )
    
    # 精度信息（适用于测量工具）
    accuracy = models.CharField(max_length=50, blank=True, verbose_name='精度')
    measurement_range = models.CharField(max_length=100, blank=True, verbose_name='测量范围')
    
    # 校准信息
    last_calibration_date = models.DateField(
        null=True, 
        blank=True, 
        verbose_name='上次校准日期'
    )
    next_calibration_date = models.DateField(
        null=True, 
        blank=True, 
        verbose_name='下次校准日期'
    )
    calibration_interval = models.IntegerField(
        default=365, 
        verbose_name='校准间隔(天)'
    )
    
    # 备注
    remarks = models.TextField(blank=True, verbose_name='备注')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'tools'
        verbose_name = '工具'
        verbose_name_plural = '工具'
        ordering = ['tool_id']

    def __str__(self):
        return f"{self.tool_id} - {self.name}"

    @property
    def is_calibration_due(self):
        """判断是否需要校准"""
        from django.utils import timezone
        if self.next_calibration_date:
            return timezone.now().date() >= self.next_calibration_date
        return False


class ToolBorrowRecord(models.Model):
    """工具借用记录模型"""
    BORROW_STATUS_CHOICES = [
        ('active', '借用中'),
        ('returned', '已归还'),
        ('overdue', '逾期'),
        ('lost', '丢失'),
    ]
    
    tool = models.ForeignKey(
        Tool, 
        on_delete=models.CASCADE, 
        verbose_name='工具'
    )
    borrower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='borrowed_tools',
        verbose_name='借用人'
    )
    approver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_tool_borrows',
        verbose_name='审批人'
    )
    
    # 借用信息
    borrow_date = models.DateField(verbose_name='借用日期')
    expected_return_date = models.DateField(verbose_name='预期归还日期')
    actual_return_date = models.DateField(
        null=True, 
        blank=True, 
        verbose_name='实际归还日期'
    )
    
    borrow_purpose = models.CharField(max_length=200, verbose_name='借用目的')
    test_task = models.ForeignKey(
        'tasks.TestTask',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='关联试验任务'
    )
    
    # 状态
    status = models.CharField(
        max_length=20,
        choices=BORROW_STATUS_CHOICES,
        default='active',
        verbose_name='借用状态'
    )
    
    # 归还时状态
    return_condition = models.CharField(
        max_length=20,
        choices=[
            ('normal', '正常'),
            ('damaged', '损坏'),
            ('lost', '丢失'),
        ],
        blank=True,
        verbose_name='归还时状态'
    )
    
    # 备注
    borrow_notes = models.TextField(blank=True, verbose_name='借用备注')
    return_notes = models.TextField(blank=True, verbose_name='归还备注')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'tool_borrow_records'
        verbose_name = '工具借用记录'
        verbose_name_plural = '工具借用记录'
        ordering = ['-borrow_date']

    def __str__(self):
        return f"{self.tool.name} - {self.borrower.username} - {self.borrow_date}"

    @property
    def is_overdue(self):
        """判断是否逾期"""
        from django.utils import timezone
        if self.status == 'active':
            return timezone.now().date() > self.expected_return_date
        return False

    @property
    def borrow_duration(self):
        """计算借用时长"""
        if self.actual_return_date:
            return (self.actual_return_date - self.borrow_date).days
        else:
            from django.utils import timezone
            return (timezone.now().date() - self.borrow_date).days


class ToolCalibration(models.Model):
    """工具校准记录模型"""
    CALIBRATION_RESULT_CHOICES = [
        ('pass', '合格'),
        ('fail', '不合格'),
        ('limited', '有限制使用'),
    ]
    
    tool = models.ForeignKey(
        Tool, 
        on_delete=models.CASCADE, 
        verbose_name='工具'
    )
    calibration_date = models.DateField(verbose_name='校准日期')
    calibration_person = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='校准人员'
    )
    calibration_agency = models.CharField(max_length=200, verbose_name='校准机构')
    
    # 校准信息
    calibration_standard = models.CharField(max_length=200, verbose_name='校准标准')
    calibration_method = models.TextField(verbose_name='校准方法')
    environmental_conditions = models.TextField(verbose_name='环境条件')
    
    # 校准结果
    calibration_result = models.CharField(
        max_length=20,
        choices=CALIBRATION_RESULT_CHOICES,
        verbose_name='校准结果'
    )
    measurement_uncertainty = models.CharField(
        max_length=100, 
        blank=True, 
        verbose_name='测量不确定度'
    )
    calibration_data = models.TextField(verbose_name='校准数据')
    
    # 证书信息
    certificate_number = models.CharField(max_length=100, verbose_name='证书编号')
    certificate_file = models.FileField(
        upload_to='tool_calibration/', 
        blank=True, 
        null=True,
        verbose_name='校准证书'
    )
    
    # 有效期
    valid_until = models.DateField(verbose_name='有效期至')
    next_calibration_date = models.DateField(verbose_name='下次校准日期')
    
    # 费用
    calibration_cost = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        default=0,
        verbose_name='校准费用'
    )
    
    remarks = models.TextField(blank=True, verbose_name='备注')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'tool_calibration'
        verbose_name = '工具校准记录'
        verbose_name_plural = '工具校准记录'
        ordering = ['-calibration_date']

    def __str__(self):
        return f"{self.tool.name} - {self.calibration_date} - {self.get_calibration_result_display()}"

    @property
    def is_valid(self):
        """判断校准是否有效"""
        from django.utils import timezone
        return timezone.now().date() <= self.valid_until