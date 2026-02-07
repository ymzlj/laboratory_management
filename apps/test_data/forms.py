"""
试验数据模块表单
"""
from django import forms
from django.core.exceptions import ValidationError
from .models import (
    AntiSlipTestData, MetalImpactTestData, MetalTensileTestData,
    CompressionTestData, FatigueTestData, HardnessTestData,
    CreepTestData, CorrosionTestData
)


class BaseTestDataForm(forms.ModelForm):
    """试验数据基础表单"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 为所有字段添加CSS类
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.widgets.Input):
                field.widget.attrs.update({'class': 'form-control'})
            elif isinstance(field.widget, forms.widgets.Select):
                field.widget.attrs.update({'class': 'form-select'})
            elif isinstance(field.widget, forms.widgets.Textarea):
                field.widget.attrs.update({'class': 'form-control', 'rows': 3})
            elif isinstance(field.widget, forms.widgets.DateInput):
                field.widget.attrs.update({
                    'class': 'form-control',
                    'type': 'date'
                })
    
    def clean_test_date(self):
        """验证试验日期"""
        test_date = self.cleaned_data.get('test_date')
        if test_date:
            from datetime import date
            if test_date > date.today():
                raise ValidationError('试验日期不能是未来日期')
        return test_date
    
    def clean_temperature(self):
        """验证温度范围"""
        temperature = self.cleaned_data.get('temperature')
        if temperature is not None:
            if temperature < -273.15:
                raise ValidationError('温度不能低于绝对零度')
            if temperature > 3000:
                raise ValidationError('温度值过高，请检查输入')
        return temperature


class AntiSlipTestDataForm(BaseTestDataForm):
    """防滑试验数据表单"""
    
    class Meta:
        model = AntiSlipTestData
        fields = [
            'test_task', 'sample_id', 'test_date', 'tester',
            'temperature', 'humidity', 'friction_coefficient',
            'slip_resistance', 'result', 'remarks'
        ]
        widgets = {
            'test_date': forms.DateInput(attrs={'type': 'date'}),
            'remarks': forms.Textarea(attrs={'rows': 3}),
        }
    
    def clean_humidity(self):
        """验证湿度范围"""
        humidity = self.cleaned_data.get('humidity')
        if humidity is not None:
            if humidity < 0 or humidity > 100:
                raise ValidationError('湿度值应在0-100%之间')
        return humidity
    
    def clean_friction_coefficient(self):
        """验证摩擦系数"""
        friction_coefficient = self.cleaned_data.get('friction_coefficient')
        if friction_coefficient is not None:
            if friction_coefficient < 0:
                raise ValidationError('摩擦系数不能为负数')
            if friction_coefficient > 2:
                raise ValidationError('摩擦系数值过高，请检查输入')
        return friction_coefficient


class MetalImpactTestDataForm(BaseTestDataForm):
    """金属冲击试验数据表单"""
    
    class Meta:
        model = MetalImpactTestData
        fields = [
            'test_task', 'sample_id', 'test_date', 'tester',
            'temperature', 'impact_energy', 'impact_strength',
            'fracture_type', 'result', 'remarks'
        ]
        widgets = {
            'test_date': forms.DateInput(attrs={'type': 'date'}),
            'remarks': forms.Textarea(attrs={'rows': 3}),
        }
    
    def clean_impact_energy(self):
        """验证冲击能量"""
        impact_energy = self.cleaned_data.get('impact_energy')
        if impact_energy is not None and impact_energy <= 0:
            raise ValidationError('冲击能量必须大于0')
        return impact_energy


class MetalTensileTestDataForm(BaseTestDataForm):
    """金属拉伸试验数据表单"""
    
    class Meta:
        model = MetalTensileTestData
        fields = [
            'test_task', 'sample_id', 'test_date', 'tester',
            'temperature', 'strain_rate', 'tensile_strength',
            'yield_strength', 'elongation', 'elastic_modulus',
            'result', 'remarks'
        ]
        widgets = {
            'test_date': forms.DateInput(attrs={'type': 'date'}),
            'remarks': forms.Textarea(attrs={'rows': 3}),
        }
    
    def clean_strain_rate(self):
        """验证应变速率"""
        strain_rate = self.cleaned_data.get('strain_rate')
        if strain_rate is not None and strain_rate <= 0:
            raise ValidationError('应变速率必须大于0')
        return strain_rate
    
    def clean(self):
        """验证拉伸强度和屈服强度的关系"""
        cleaned_data = super().clean()
        tensile_strength = cleaned_data.get('tensile_strength')
        yield_strength = cleaned_data.get('yield_strength')
        
        if tensile_strength and yield_strength:
            if yield_strength > tensile_strength:
                raise ValidationError('屈服强度不能大于抗拉强度')
        
        return cleaned_data


class CompressionTestDataForm(BaseTestDataForm):
    """压缩试验数据表单"""
    
    class Meta:
        model = CompressionTestData
        fields = [
            'test_task', 'sample_id', 'test_date', 'tester',
            'temperature', 'compression_rate', 'compression_strength',
            'compression_modulus', 'deformation', 'result', 'remarks'
        ]
        widgets = {
            'test_date': forms.DateInput(attrs={'type': 'date'}),
            'remarks': forms.Textarea(attrs={'rows': 3}),
        }
    
    def clean_compression_rate(self):
        """验证压缩速率"""
        compression_rate = self.cleaned_data.get('compression_rate')
        if compression_rate is not None and compression_rate <= 0:
            raise ValidationError('压缩速率必须大于0')
        return compression_rate


class FatigueTestDataForm(BaseTestDataForm):
    """疲劳试验数据表单"""
    
    class Meta:
        model = FatigueTestData
        fields = [
            'test_task', 'sample_id', 'test_date', 'tester',
            'temperature', 'frequency', 'stress_ratio',
            'max_stress', 'min_stress', 'cycles_to_failure',
            'result', 'remarks'
        ]
        widgets = {
            'test_date': forms.DateInput(attrs={'type': 'date'}),
            'remarks': forms.Textarea(attrs={'rows': 3}),
        }
    
    def clean_frequency(self):
        """验证频率"""
        frequency = self.cleaned_data.get('frequency')
        if frequency is not None and frequency <= 0:
            raise ValidationError('频率必须大于0')
        return frequency
    
    def clean_cycles_to_failure(self):
        """验证破坏循环次数"""
        cycles = self.cleaned_data.get('cycles_to_failure')
        if cycles is not None and cycles <= 0:
            raise ValidationError('破坏循环次数必须大于0')
        return cycles
    
    def clean(self):
        """验证应力关系"""
        cleaned_data = super().clean()
        max_stress = cleaned_data.get('max_stress')
        min_stress = cleaned_data.get('min_stress')
        
        if max_stress and min_stress:
            if min_stress >= max_stress:
                raise ValidationError('最小应力必须小于最大应力')
        
        return cleaned_data


class HardnessTestDataForm(BaseTestDataForm):
    """硬度试验数据表单"""
    
    class Meta:
        model = HardnessTestData
        fields = [
            'test_task', 'sample_id', 'test_date', 'tester',
            'temperature', 'test_method', 'load_force',
            'hardness_value', 'indentation_depth', 'result', 'remarks'
        ]
        widgets = {
            'test_date': forms.DateInput(attrs={'type': 'date'}),
            'remarks': forms.Textarea(attrs={'rows': 3}),
        }
    
    def clean_load_force(self):
        """验证试验力"""
        load_force = self.cleaned_data.get('load_force')
        if load_force is not None and load_force <= 0:
            raise ValidationError('试验力必须大于0')
        return load_force
    
    def clean_hardness_value(self):
        """验证硬度值"""
        hardness_value = self.cleaned_data.get('hardness_value')
        if hardness_value is not None and hardness_value <= 0:
            raise ValidationError('硬度值必须大于0')
        return hardness_value


class CreepTestDataForm(BaseTestDataForm):
    """蠕变试验数据表单"""
    
    class Meta:
        model = CreepTestData
        fields = [
            'test_task', 'sample_id', 'test_date', 'tester',
            'temperature', 'applied_stress', 'test_duration',
            'initial_strain', 'final_strain', 'creep_rate',
            'result', 'remarks'
        ]
        widgets = {
            'test_date': forms.DateInput(attrs={'type': 'date'}),
            'remarks': forms.Textarea(attrs={'rows': 3}),
        }
    
    def clean_applied_stress(self):
        """验证施加应力"""
        applied_stress = self.cleaned_data.get('applied_stress')
        if applied_stress is not None and applied_stress <= 0:
            raise ValidationError('施加应力必须大于0')
        return applied_stress
    
    def clean_test_duration(self):
        """验证试验时间"""
        test_duration = self.cleaned_data.get('test_duration')
        if test_duration is not None and test_duration <= 0:
            raise ValidationError('试验时间必须大于0')
        return test_duration
    
    def clean(self):
        """验证应变关系"""
        cleaned_data = super().clean()
        initial_strain = cleaned_data.get('initial_strain')
        final_strain = cleaned_data.get('final_strain')
        
        if initial_strain and final_strain:
            if final_strain <= initial_strain:
                raise ValidationError('最终应变应大于初始应变')
        
        return cleaned_data


class CorrosionTestDataForm(BaseTestDataForm):
    """腐蚀试验数据表单"""
    
    class Meta:
        model = CorrosionTestData
        fields = [
            'test_task', 'sample_id', 'test_date', 'tester',
            'temperature', 'corrosive_medium', 'exposure_time',
            'weight_loss', 'corrosion_rate', 'corrosion_depth',
            'result', 'remarks'
        ]
        widgets = {
            'test_date': forms.DateInput(attrs={'type': 'date'}),
            'remarks': forms.Textarea(attrs={'rows': 3}),
        }
    
    def clean_exposure_time(self):
        """验证暴露时间"""
        exposure_time = self.cleaned_data.get('exposure_time')
        if exposure_time is not None and exposure_time <= 0:
            raise ValidationError('暴露时间必须大于0')
        return exposure_time
    
    def clean_weight_loss(self):
        """验证失重"""
        weight_loss = self.cleaned_data.get('weight_loss')
        if weight_loss is not None and weight_loss < 0:
            raise ValidationError('失重不能为负数')
        return weight_loss
    
    def clean_corrosion_rate(self):
        """验证腐蚀速率"""
        corrosion_rate = self.cleaned_data.get('corrosion_rate')
        if corrosion_rate is not None and corrosion_rate < 0:
            raise ValidationError('腐蚀速率不能为负数')
        return corrosion_rate


# 试验数据搜索表单
class TestDataSearchForm(forms.Form):
    """试验数据搜索表单"""
    
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '搜索样品编号、试验员...'
        })
    )
    
    test_task = forms.ModelChoiceField(
        queryset=None,
        required=False,
        empty_label='所有任务',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    tester = forms.ModelChoiceField(
        queryset=None,
        required=False,
        empty_label='所有试验员',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    result = forms.ChoiceField(
        choices=[
            ('', '所有结果'),
            ('合格', '合格'),
            ('不合格', '不合格'),
            ('待定', '待定'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    def __init__(self, *args, **kwargs):
        from apps.tasks.models import TestTask
        from django.contrib.auth import get_user_model
        
        super().__init__(*args, **kwargs)
        
        # 设置任务选项
        self.fields['test_task'].queryset = TestTask.objects.all()
        
        # 设置试验员选项
        User = get_user_model()
        self.fields['tester'].queryset = User.objects.filter(account_status=True)
    
    def clean(self):
        """验证日期范围"""
        cleaned_data = super().clean()
        date_from = cleaned_data.get('date_from')
        date_to = cleaned_data.get('date_to')
        
        if date_from and date_to:
            if date_from > date_to:
                raise ValidationError('开始日期不能晚于结束日期')
        
        return cleaned_data