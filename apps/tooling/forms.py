from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Tooling, ToolingUsageRecord, ToolingMaintenance
from apps.tasks.models import TestTask

User = get_user_model()


class ToolingForm(forms.ModelForm):
    """工装表单"""
    
    class Meta:
        model = Tooling
        fields = [
            'tooling_id', 'name', 'type', 'model', 'manufacturer', 'status',
            'location', 'responsible_person', 'purchase_date', 'purchase_price',
            'specifications', 'material', 'dimensions', 'weight', 'remarks'
        ]
        widgets = {
            'tooling_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入工装编号，如：TL-001'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入工装名称'
            }),
            'model': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入型号'
            }),
            'manufacturer': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入制造商'
            }),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入存放位置'
            }),
            'responsible_person': forms.Select(attrs={'class': 'form-control'}),
            'purchase_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'purchase_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入采购价格',
                'step': '0.01',
                'min': '0'
            }),
            'type': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入工装类型'
            }),
            'specifications': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '请输入技术规格'
            }),
            'material': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入材质'
            }),
            'dimensions': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入尺寸，如：100x50x20mm'
            }),
            'weight': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入重量(kg)',
                'step': '0.01',
                'min': '0'
            }),
            'remarks': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '请输入备注信息'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 设置负责人选项
        self.fields['responsible_person'].queryset = User.objects.filter(account_status=True)
        self.fields['responsible_person'].empty_label = "请选择负责人"
        
        # 设置必填字段
        self.fields['tooling_id'].required = True
        self.fields['name'].required = True
        self.fields['status'].required = True
    
    def clean_tooling_id(self):
        """验证工装编号"""
        tooling_id = self.cleaned_data.get('tooling_id')
        if tooling_id:
            # 检查编号是否已存在（排除当前实例）
            queryset = Tooling.objects.filter(tooling_id=tooling_id)
            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            
            if queryset.exists():
                raise ValidationError('该工装编号已存在，请使用其他编号。')
        
        return tooling_id
    
    def clean_purchase_price(self):
        """验证采购价格"""
        price = self.cleaned_data.get('purchase_price')
        if price is not None and price < 0:
            raise ValidationError('采购价格不能为负数。')
        return price
    
    def clean(self):
        """表单整体验证"""
        cleaned_data = super().clean()
        return cleaned_data


class ToolingUsageRecordForm(forms.ModelForm):
    """工装使用记录表单"""
    
    class Meta:
        model = ToolingUsageRecord
        fields = [
            'tooling', 'user', 'test_task', 'start_time', 'end_time',
            'usage_purpose', 'usage_notes', 'load_applied',
            'temperature', 'tooling_condition'
        ]
        widgets = {
            'tooling': forms.Select(attrs={'class': 'form-control'}),
            'user': forms.Select(attrs={'class': 'form-control'}),
            'test_task': forms.Select(attrs={'class': 'form-control'}),
            'start_time': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'end_time': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'usage_purpose': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入使用目的'
            }),
            'usage_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '请输入使用说明'
            }),
            'load_applied': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '施加载荷(kg)',
                'step': '0.01',
                'min': '0'
            }),
            'temperature': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '使用温度(°C)'
            }),
            'tooling_condition': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 设置选项
        self.fields['tooling'].queryset = Tooling.objects.filter(status__in=['available', 'in_use'])
        self.fields['tooling'].empty_label = "请选择工装"
        
        self.fields['user'].queryset = User.objects.filter(account_status=True)
        self.fields['user'].empty_label = "请选择使用人员"
        
        self.fields['test_task'].queryset = TestTask.objects.filter(status__code__in=['in_progress', 'pending'])
        self.fields['test_task'].empty_label = "请选择关联任务（可选）"
        self.fields['test_task'].required = False
        
        # 设置必填字段
        self.fields['tooling'].required = True
        self.fields['user'].required = True
        self.fields['start_time'].required = True
        self.fields['usage_purpose'].required = True
    
    def clean(self):
        """表单整体验证"""
        cleaned_data = super().clean()
        
        # 验证时间逻辑
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        
        if start_time and end_time:
            if start_time >= end_time:
                raise ValidationError('结束时间必须晚于开始时间。')
            
            # 检查时间是否合理（不能超过当前时间太多）
            now = timezone.now()
            if start_time > now + timezone.timedelta(hours=1):
                raise ValidationError('开始时间不能超过当前时间1小时以上。')
        
        # 验证载荷
        tooling = cleaned_data.get('tooling')
        load_applied = cleaned_data.get('load_applied')
        
        if tooling and load_applied and tooling.max_load:
            if load_applied > tooling.max_load:
                raise ValidationError(f'施加载荷({load_applied}kg)超过工装最大载荷({tooling.max_load}kg)。')
        
        # 验证温度
        temperature = cleaned_data.get('temperature')
        if tooling and temperature is not None:
            if (tooling.operating_temperature_min is not None and 
                temperature < tooling.operating_temperature_min):
                raise ValidationError(
                    f'使用温度({temperature}°C)低于工装最低工作温度({tooling.operating_temperature_min}°C)。'
                )
            
            if (tooling.operating_temperature_max is not None and 
                temperature > tooling.operating_temperature_max):
                raise ValidationError(
                    f'使用温度({temperature}°C)高于工装最高工作温度({tooling.operating_temperature_max}°C)。'
                )
        
        return cleaned_data


class ToolingMaintenanceForm(forms.ModelForm):
    """工装维护记录表单"""
    
    class Meta:
        model = ToolingMaintenance
        fields = [
            'tooling', 'maintenance_person', 'maintenance_type', 'maintenance_date',
            'maintenance_content', 'parts_replaced', 'maintenance_cost',
            'maintenance_result', 'next_maintenance_date',
            'calibration_certificate', 'calibration_due_date', 'remarks'
        ]
        widgets = {
            'tooling': forms.Select(attrs={'class': 'form-control'}),
            'maintenance_person': forms.Select(attrs={'class': 'form-control'}),
            'maintenance_type': forms.Select(attrs={'class': 'form-control'}),
            'maintenance_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'maintenance_content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': '请详细描述维护内容'
            }),
            'parts_replaced': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '请列出更换的部件（如有）'
            }),
            'maintenance_cost': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '维护费用',
                'step': '0.01',
                'min': '0'
            }),
            'maintenance_result': forms.Select(attrs={'class': 'form-control'}),
            'next_maintenance_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'calibration_certificate': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '校准证书编号'
            }),
            'calibration_due_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'remarks': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '请输入备注信息'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 设置选项
        self.fields['tooling'].queryset = Tooling.objects.all()
        self.fields['tooling'].empty_label = "请选择工装"
        
        self.fields['maintenance_person'].queryset = User.objects.filter(account_status=True)
        self.fields['maintenance_person'].empty_label = "请选择维护人员"
        
        # 设置必填字段
        self.fields['tooling'].required = True
        self.fields['maintenance_person'].required = True
        self.fields['maintenance_type'].required = True
        self.fields['maintenance_date'].required = True
        self.fields['maintenance_content'].required = True
        self.fields['maintenance_result'].required = True
        
        # 校准相关字段仅在校准类型时必填
        self.fields['calibration_certificate'].required = False
        self.fields['calibration_due_date'].required = False
    
    def clean_maintenance_cost(self):
        """验证维护费用"""
        cost = self.cleaned_data.get('maintenance_cost')
        if cost is not None and cost < 0:
            raise ValidationError('维护费用不能为负数。')
        return cost
    
    def clean(self):
        """表单整体验证"""
        cleaned_data = super().clean()
        
        # 验证日期逻辑
        maintenance_date = cleaned_data.get('maintenance_date')
        next_maintenance_date = cleaned_data.get('next_maintenance_date')
        calibration_due_date = cleaned_data.get('calibration_due_date')
        
        if maintenance_date:
            # 维护日期不能是未来日期
            today = timezone.now().date()
            if maintenance_date > today:
                raise ValidationError('维护日期不能是未来日期。')
            
            # 下次维护日期必须晚于维护日期
            if next_maintenance_date and next_maintenance_date <= maintenance_date:
                raise ValidationError('下次维护日期必须晚于维护日期。')
            
            # 校准到期日期必须晚于维护日期
            if calibration_due_date and calibration_due_date <= maintenance_date:
                raise ValidationError('校准到期日期必须晚于维护日期。')
        
        # 校准类型的特殊验证
        maintenance_type = cleaned_data.get('maintenance_type')
        if maintenance_type == 'calibration':
            if not cleaned_data.get('calibration_certificate'):
                raise ValidationError('校准类型维护必须填写校准证书编号。')
            if not calibration_due_date:
                raise ValidationError('校准类型维护必须填写校准到期日期。')
        
        return cleaned_data


class ToolingSearchForm(forms.Form):
    """工装搜索表单"""
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '搜索工装名称、编号、型号或制造商'
        })
    )
    
    status = forms.ChoiceField(
        choices=[('', '全部状态')] + Tooling.TOOLING_STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    manufacturer = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '制造商'
        })
    )
    
    location = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '存放位置'
        })
    )
    
    responsible_person = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '负责人'
        })
    )
    
    needs_maintenance = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    calibration_overdue = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )


class UsageRecordSearchForm(forms.Form):
    """使用记录搜索表单"""
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '搜索工装、使用人或目的'
        })
    )
    
    tooling = forms.ModelChoiceField(
        queryset=Tooling.objects.all(),
        required=False,
        empty_label="全部工装",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    user = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '使用人'
        })
    )
    
    task = forms.ModelChoiceField(
        queryset=TestTask.objects.all(),
        required=False,
        empty_label="全部任务",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    tooling_condition = forms.ChoiceField(
        choices=[('', '全部状态')] + [
            ('normal', '正常'),
            ('wear', '磨损'),
            ('damaged', '损坏'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    in_use_only = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )


class MaintenanceRecordSearchForm(forms.Form):
    """维护记录搜索表单"""
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '搜索工装、维护人或内容'
        })
    )
    
    tooling = forms.ModelChoiceField(
        queryset=Tooling.objects.all(),
        required=False,
        empty_label="全部工装",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    maintenance_type = forms.ChoiceField(
        choices=[('', '全部类型')] + ToolingMaintenance.MAINTENANCE_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    maintenance_result = forms.ChoiceField(
        choices=[('', '全部结果')] + [
            ('completed', '完成'),
            ('pending', '待完成'),
            ('failed', '失败'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    maintainer = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '维护人员'
        })
    )
    
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    calibration_overdue = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )