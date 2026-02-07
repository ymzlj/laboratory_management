"""
工装管理模块数据模型
"""
from django.db import models
from django.conf import settings


class Tooling(models.Model):
    """工装模型"""
    TOOLING_STATUS_CHOICES = [
        ('available', '可用'),
        ('in_use', '使用中'),
        ('maintenance', '维护中'),
        ('repair', '维修中'),
        ('retired', '已报废'),
    ]
    
    tooling_id = models.CharField(max_length=50, unique=True, verbose_name='工装编号')
    name = models.CharField(max_length=200, verbose_name='工装名称')
    type = models.CharField(max_length=100, verbose_name='工装类型')
    model = models.CharField(max_length=100, verbose_name='工装型号')
    manufacturer = models.CharField(max_length=100, verbose_name='制造商')
    
    # 工装基本信息
    purchase_date = models.DateField(verbose_name='采购日期')
    purchase_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name='采购价格'
    )
    
    # 工装状态
    status = models.CharField(
        max_length=20, 
        choices=TOOLING_STATUS_CHOICES, 
        default='available',
        verbose_name='工装状态'
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
    material = models.CharField(max_length=100, verbose_name='材质')
    dimensions = models.CharField(max_length=200, verbose_name='尺寸规格')
    weight = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name='重量(kg)'
    )
    
    # 使用信息
    max_load = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name='最大载荷(N)'
    )
    operating_temperature_min = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name='最低工作温度(°C)'
    )
    operating_temperature_max = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name='最高工作温度(°C)'
    )
    
    # 维护信息
    last_maintenance_date = models.DateField(
        null=True, 
        blank=True, 
        verbose_name='上次维护日期'
    )
    next_maintenance_date = models.DateField(
        null=True, 
        blank=True, 
        verbose_name='下次维护日期'
    )
    maintenance_interval = models.IntegerField(
        default=90, 
        verbose_name='维护间隔(天)'
    )
    
    # 备注
    remarks = models.TextField(blank=True, verbose_name='备注')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'tooling'
        verbose_name = '工装'
        verbose_name_plural = '工装'
        ordering = ['tooling_id']

    def __str__(self):
        return f"{self.tooling_id} - {self.name}"

    @property
    def is_maintenance_due(self):
        """判断是否需要维护"""
        from django.utils import timezone
        if self.next_maintenance_date:
            return timezone.now().date() >= self.next_maintenance_date
        return False


class ToolingUsageRecord(models.Model):
    """工装使用记录模型"""
    tooling = models.ForeignKey(
        Tooling, 
        on_delete=models.CASCADE, 
        verbose_name='工装'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='使用人'
    )
    test_task = models.ForeignKey(
        'tasks.TestTask',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='关联试验任务'
    )
    
    start_time = models.DateTimeField(verbose_name='开始使用时间')
    end_time = models.DateTimeField(
        null=True, 
        blank=True, 
        verbose_name='结束使用时间'
    )
    usage_purpose = models.CharField(max_length=200, verbose_name='使用目的')
    usage_notes = models.TextField(blank=True, verbose_name='使用说明')
    
    # 使用条件
    load_applied = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name='施加载荷(N)'
    )
    temperature = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name='使用温度(°C)'
    )
    
    # 使用后状态
    tooling_condition = models.CharField(
        max_length=20,
        choices=[
            ('normal', '正常'),
            ('wear', '磨损'),
            ('damaged', '损坏'),
        ],
        default='normal',
        verbose_name='工装状态'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'tooling_usage_records'
        verbose_name = '工装使用记录'
        verbose_name_plural = '工装使用记录'
        ordering = ['-start_time']

    def __str__(self):
        return f"{self.tooling.name} - {self.user.username} - {self.start_time}"

    @property
    def usage_duration(self):
        """计算使用时长"""
        if self.end_time:
            return self.end_time - self.start_time
        return None


class ToolingMaintenance(models.Model):
    """工装维护记录模型"""
    MAINTENANCE_TYPE_CHOICES = [
        ('routine', '例行维护'),
        ('preventive', '预防性维护'),
        ('corrective', '纠正性维护'),
        ('calibration', '校准'),
    ]
    
    tooling = models.ForeignKey(
        Tooling, 
        on_delete=models.CASCADE, 
        verbose_name='工装'
    )
    maintenance_type = models.CharField(
        max_length=20,
        choices=MAINTENANCE_TYPE_CHOICES,
        verbose_name='维护类型'
    )
    maintenance_date = models.DateField(verbose_name='维护日期')
    maintenance_person = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='维护人员'
    )
    
    # 维护内容
    maintenance_content = models.TextField(verbose_name='维护内容')
    parts_replaced = models.TextField(blank=True, verbose_name='更换部件')
    maintenance_cost = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        default=0,
        verbose_name='维护费用'
    )
    
    # 校准信息（如果适用）
    calibration_certificate = models.FileField(
        upload_to='tooling_calibration/', 
        blank=True, 
        null=True,
        verbose_name='校准证书'
    )
    calibration_due_date = models.DateField(
        null=True, 
        blank=True, 
        verbose_name='校准到期日期'
    )
    
    # 维护结果
    maintenance_result = models.CharField(
        max_length=20,
        choices=[
            ('completed', '完成'),
            ('pending', '待完成'),
            ('failed', '失败'),
        ],
        default='completed',
        verbose_name='维护结果'
    )
    
    next_maintenance_date = models.DateField(
        null=True, 
        blank=True, 
        verbose_name='下次维护日期'
    )
    
    remarks = models.TextField(blank=True, verbose_name='备注')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'tooling_maintenance'
        verbose_name = '工装维护记录'
        verbose_name_plural = '工装维护记录'
        ordering = ['-maintenance_date']

    def __str__(self):
        return f"{self.tooling.name} - {self.maintenance_date} - {self.get_maintenance_type_display()}"