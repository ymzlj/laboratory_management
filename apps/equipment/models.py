"""
设备管理模块数据模型
"""
from django.db import models
from django.conf import settings


class Equipment(models.Model):
    """设备模型"""
    EQUIPMENT_STATUS_CHOICES = [
        ('available', '可用'),
        ('in_use', '使用中'),
        ('maintenance', '维护中'),
        ('repair', '维修中'),
        ('retired', '已报废'),
    ]
    
    equipment_id = models.CharField(max_length=50, unique=True, verbose_name='设备编号')
    name = models.CharField(max_length=200, verbose_name='设备名称')
    model = models.CharField(max_length=100, verbose_name='设备型号')
    manufacturer = models.CharField(max_length=100, verbose_name='制造商')
    serial_number = models.CharField(max_length=100, unique=True, verbose_name='序列号')
    
    # 设备基本信息
    purchase_date = models.DateField(verbose_name='采购日期')
    purchase_price = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        verbose_name='采购价格'
    )
    warranty_period = models.IntegerField(verbose_name='保修期(月)')
    warranty_end_date = models.DateField(verbose_name='保修到期日期')
    
    # 设备状态
    status = models.CharField(
        max_length=20, 
        choices=EQUIPMENT_STATUS_CHOICES, 
        default='available',
        verbose_name='设备状态'
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
    operating_manual = models.FileField(
        upload_to='equipment_manuals/', 
        blank=True, 
        null=True,
        verbose_name='操作手册'
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
        default=30, 
        verbose_name='维护间隔(天)'
    )
    
    # 备注
    remarks = models.TextField(blank=True, verbose_name='备注')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'equipment'
        verbose_name = '设备'
        verbose_name_plural = '设备'
        ordering = ['equipment_id']

    def __str__(self):
        return f"{self.equipment_id} - {self.name}"

    @property
    def is_maintenance_due(self):
        """判断是否需要维护"""
        from django.utils import timezone
        if self.next_maintenance_date:
            return timezone.now().date() >= self.next_maintenance_date
        return False

    @property
    def is_warranty_expired(self):
        """判断保修是否过期"""
        from django.utils import timezone
        return timezone.now().date() > self.warranty_end_date


class EquipmentUsageRecord(models.Model):
    """设备使用记录模型"""
    equipment = models.ForeignKey(
        Equipment, 
        on_delete=models.CASCADE, 
        verbose_name='设备'
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
    
    # 使用后状态
    equipment_condition = models.CharField(
        max_length=20,
        choices=[
            ('normal', '正常'),
            ('abnormal', '异常'),
            ('damaged', '损坏'),
        ],
        default='normal',
        verbose_name='设备状态'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'equipment_usage_records'
        verbose_name = '设备使用记录'
        verbose_name_plural = '设备使用记录'
        ordering = ['-start_time']

    def __str__(self):
        return f"{self.equipment.name} - {self.user.username} - {self.start_time}"

    @property
    def usage_duration(self):
        """计算使用时长"""
        if self.end_time:
            return self.end_time - self.start_time
        return None


class EquipmentMaintenance(models.Model):
    """设备维护记录模型"""
    MAINTENANCE_TYPE_CHOICES = [
        ('routine', '例行维护'),
        ('preventive', '预防性维护'),
        ('corrective', '纠正性维护'),
        ('emergency', '紧急维护'),
    ]
    
    equipment = models.ForeignKey(
        Equipment, 
        on_delete=models.CASCADE, 
        verbose_name='设备'
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
        max_digits=10, 
        decimal_places=2, 
        default=0,
        verbose_name='维护费用'
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
        db_table = 'equipment_maintenance'
        verbose_name = '设备维护记录'
        verbose_name_plural = '设备维护记录'
        ordering = ['-maintenance_date']

    def __str__(self):
        return f"{self.equipment.name} - {self.maintenance_date} - {self.get_maintenance_type_display()}"