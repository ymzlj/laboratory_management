"""
试验数据模块数据模型
"""
from django.db import models
from django.conf import settings
from apps.tasks.models import TestTask


class AntiSlipTestData(models.Model):
    """防滑试验数据模型"""
    test_task = models.ForeignKey(
        TestTask, 
        on_delete=models.CASCADE, 
        verbose_name='试验任务'
    )
    sample_id = models.CharField(max_length=100, verbose_name='样品编号')
    test_date = models.DateField(verbose_name='试验日期')
    tester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='试验员'
    )
    
    # 试验条件
    temperature = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        verbose_name='温度(°C)'
    )
    humidity = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        verbose_name='湿度(%)'
    )
    
    # 试验数据
    friction_coefficient = models.DecimalField(
        max_digits=6, 
        decimal_places=4, 
        verbose_name='摩擦系数'
    )
    slip_resistance = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        verbose_name='防滑阻力(N)'
    )
    
    # 试验结果
    result = models.CharField(max_length=20, verbose_name='试验结果')
    remarks = models.TextField(blank=True, verbose_name='备注')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'anti_slip_test_data'
        verbose_name = '防滑试验数据'
        verbose_name_plural = '防滑试验数据'

    def __str__(self):
        return f"{self.sample_id} - {self.test_date}"


class MetalImpactTestData(models.Model):
    """金属冲击试验数据模型"""
    test_task = models.ForeignKey(
        TestTask, 
        on_delete=models.CASCADE, 
        verbose_name='试验任务'
    )
    sample_id = models.CharField(max_length=100, verbose_name='样品编号')
    test_date = models.DateField(verbose_name='试验日期')
    tester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='试验员'
    )
    
    # 试验条件
    temperature = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        verbose_name='温度(°C)'
    )
    impact_energy = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        verbose_name='冲击能量(J)'
    )
    
    # 试验数据
    impact_strength = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        verbose_name='冲击强度(J/cm²)'
    )
    fracture_type = models.CharField(max_length=50, verbose_name='断裂类型')
    
    # 试验结果
    result = models.CharField(max_length=20, verbose_name='试验结果')
    remarks = models.TextField(blank=True, verbose_name='备注')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'metal_impact_test_data'
        verbose_name = '金属冲击试验数据'
        verbose_name_plural = '金属冲击试验数据'

    def __str__(self):
        return f"{self.sample_id} - {self.test_date}"


class MetalTensileTestData(models.Model):
    """金属拉伸试验数据模型"""
    test_task = models.ForeignKey(
        TestTask, 
        on_delete=models.CASCADE, 
        verbose_name='试验任务'
    )
    sample_id = models.CharField(max_length=100, verbose_name='样品编号')
    test_date = models.DateField(verbose_name='试验日期')
    tester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='试验员'
    )
    
    # 试验条件
    temperature = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        verbose_name='温度(°C)'
    )
    strain_rate = models.DecimalField(
        max_digits=8, 
        decimal_places=6, 
        verbose_name='应变速率(s⁻¹)'
    )
    
    # 试验数据
    tensile_strength = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        verbose_name='抗拉强度(MPa)'
    )
    yield_strength = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        verbose_name='屈服强度(MPa)'
    )
    elongation = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        verbose_name='延伸率(%)'
    )
    elastic_modulus = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name='弹性模量(GPa)'
    )
    
    # 试验结果
    result = models.CharField(max_length=20, verbose_name='试验结果')
    remarks = models.TextField(blank=True, verbose_name='备注')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'metal_tensile_test_data'
        verbose_name = '金属拉伸试验数据'
        verbose_name_plural = '金属拉伸试验数据'

    def __str__(self):
        return f"{self.sample_id} - {self.test_date}"


class CompressionTestData(models.Model):
    """压缩试验数据模型"""
    test_task = models.ForeignKey(
        TestTask, 
        on_delete=models.CASCADE, 
        verbose_name='试验任务'
    )
    sample_id = models.CharField(max_length=100, verbose_name='样品编号')
    test_date = models.DateField(verbose_name='试验日期')
    tester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='试验员'
    )
    
    # 试验条件
    temperature = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        verbose_name='温度(°C)'
    )
    compression_rate = models.DecimalField(
        max_digits=8, 
        decimal_places=4, 
        verbose_name='压缩速率(mm/min)'
    )
    
    # 试验数据
    compression_strength = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        verbose_name='压缩强度(MPa)'
    )
    compression_modulus = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name='压缩模量(GPa)'
    )
    deformation = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        verbose_name='变形量(mm)'
    )
    
    # 试验结果
    result = models.CharField(max_length=20, verbose_name='试验结果')
    remarks = models.TextField(blank=True, verbose_name='备注')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'compression_test_data'
        verbose_name = '压缩试验数据'
        verbose_name_plural = '压缩试验数据'

    def __str__(self):
        return f"{self.sample_id} - {self.test_date}"


class FatigueTestData(models.Model):
    """疲劳试验数据模型"""
    test_task = models.ForeignKey(
        TestTask, 
        on_delete=models.CASCADE, 
        verbose_name='试验任务'
    )
    sample_id = models.CharField(max_length=100, verbose_name='样品编号')
    test_date = models.DateField(verbose_name='试验日期')
    tester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='试验员'
    )
    
    # 试验条件
    temperature = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        verbose_name='温度(°C)'
    )
    frequency = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        verbose_name='频率(Hz)'
    )
    stress_ratio = models.DecimalField(
        max_digits=4, 
        decimal_places=2, 
        verbose_name='应力比'
    )
    
    # 试验数据
    max_stress = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        verbose_name='最大应力(MPa)'
    )
    min_stress = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        verbose_name='最小应力(MPa)'
    )
    cycles_to_failure = models.BigIntegerField(verbose_name='破坏循环次数')
    
    # 试验结果
    result = models.CharField(max_length=20, verbose_name='试验结果')
    remarks = models.TextField(blank=True, verbose_name='备注')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'fatigue_test_data'
        verbose_name = '疲劳试验数据'
        verbose_name_plural = '疲劳试验数据'

    def __str__(self):
        return f"{self.sample_id} - {self.test_date}"


class HardnessTestData(models.Model):
    """硬度试验数据模型"""
    test_task = models.ForeignKey(
        TestTask, 
        on_delete=models.CASCADE, 
        verbose_name='试验任务'
    )
    sample_id = models.CharField(max_length=100, verbose_name='样品编号')
    test_date = models.DateField(verbose_name='试验日期')
    tester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='试验员'
    )
    
    # 试验条件
    temperature = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        verbose_name='温度(°C)'
    )
    test_method = models.CharField(max_length=50, verbose_name='试验方法')
    load_force = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        verbose_name='试验力(N)'
    )
    
    # 试验数据
    hardness_value = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        verbose_name='硬度值'
    )
    indentation_depth = models.DecimalField(
        max_digits=6, 
        decimal_places=3, 
        verbose_name='压痕深度(mm)'
    )
    
    # 试验结果
    result = models.CharField(max_length=20, verbose_name='试验结果')
    remarks = models.TextField(blank=True, verbose_name='备注')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'hardness_test_data'
        verbose_name = '硬度试验数据'
        verbose_name_plural = '硬度试验数据'

    def __str__(self):
        return f"{self.sample_id} - {self.test_date}"


class CreepTestData(models.Model):
    """蠕变试验数据模型"""
    test_task = models.ForeignKey(
        TestTask, 
        on_delete=models.CASCADE, 
        verbose_name='试验任务'
    )
    sample_id = models.CharField(max_length=100, verbose_name='样品编号')
    test_date = models.DateField(verbose_name='试验日期')
    tester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='试验员'
    )
    
    # 试验条件
    temperature = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        verbose_name='温度(°C)'
    )
    applied_stress = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        verbose_name='施加应力(MPa)'
    )
    test_duration = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name='试验时间(h)'
    )
    
    # 试验数据
    initial_strain = models.DecimalField(
        max_digits=8, 
        decimal_places=6, 
        verbose_name='初始应变'
    )
    final_strain = models.DecimalField(
        max_digits=8, 
        decimal_places=6, 
        verbose_name='最终应变'
    )
    creep_rate = models.DecimalField(
        max_digits=12, 
        decimal_places=8, 
        verbose_name='蠕变速率(s⁻¹)'
    )
    
    # 试验结果
    result = models.CharField(max_length=20, verbose_name='试验结果')
    remarks = models.TextField(blank=True, verbose_name='备注')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'creep_test_data'
        verbose_name = '蠕变试验数据'
        verbose_name_plural = '蠕变试验数据'

    def __str__(self):
        return f"{self.sample_id} - {self.test_date}"


class CorrosionTestData(models.Model):
    """腐蚀试验数据模型"""
    test_task = models.ForeignKey(
        TestTask, 
        on_delete=models.CASCADE, 
        verbose_name='试验任务'
    )
    sample_id = models.CharField(max_length=100, verbose_name='样品编号')
    test_date = models.DateField(verbose_name='试验日期')
    tester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='试验员'
    )
    
    # 试验条件
    temperature = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        verbose_name='温度(°C)'
    )
    corrosive_medium = models.CharField(max_length=100, verbose_name='腐蚀介质')
    exposure_time = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name='暴露时间(h)'
    )
    
    # 试验数据
    weight_loss = models.DecimalField(
        max_digits=8, 
        decimal_places=4, 
        verbose_name='失重(g)'
    )
    corrosion_rate = models.DecimalField(
        max_digits=8, 
        decimal_places=4, 
        verbose_name='腐蚀速率(mm/year)'
    )
    corrosion_depth = models.DecimalField(
        max_digits=6, 
        decimal_places=3, 
        verbose_name='腐蚀深度(mm)'
    )
    
    # 试验结果
    result = models.CharField(max_length=20, verbose_name='试验结果')
    remarks = models.TextField(blank=True, verbose_name='备注')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'corrosion_test_data'
        verbose_name = '腐蚀试验数据'
        verbose_name_plural = '腐蚀试验数据'

    def __str__(self):
        return f"{self.sample_id} - {self.test_date}"