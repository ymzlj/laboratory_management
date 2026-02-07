"""
设备管理模块表单
"""
from django import forms
from django.contrib.auth import get_user_model
from .models import Equipment, EquipmentUsageRecord, EquipmentMaintenance

User = get_user_model()


class BaseEquipmentForm(forms.ModelForm):
    """设备表单基类"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 为所有字段添加CSS类
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.widgets.Select):
                field.widget.attrs.update({'class': 'form-select'})
            elif isinstance(field.widget, forms.widgets.Textarea):
                field.widget.attrs.update({'class': 'form-control', 'rows': 3})
            elif isinstance(field.widget, forms.widgets.FileInput):
                field.widget.attrs.update({'class': 'form-control'})
            else:
                field.widget.attrs.update({'class': 'form-control'})
    
    def clean_purchase_price(self):
        """验证采购价格"""
        price = self.cleaned_data.get('purchase_price')
        if price and price <= 0:
            raise forms.ValidationError('采购价格必须大于0')
        return price
    
    def clean_warranty_period(self):
        """验证保修期"""
        period = self.cleaned_data.get('warranty_period')
        if period and period <= 0:
            raise forms.ValidationError('保修期必须大于0个月')
        return period
    
    def clean_maintenance_interval(self):
        """验证维护间隔"""
        interval = self.cleaned_data.get('maintenance_interval')
        if interval and interval <= 0:
            raise forms.ValidationError('维护间隔必须大于0天')
        return interval


class EquipmentForm(BaseEquipmentForm):
    """设备表单"""
    
    class Meta:
        model = Equipment
        fields = [
            'equipment_id', 'name', 'model', 'manufacturer', 'serial_number',
            'purchase_date', 'purchase_price', 'warranty_period', 'warranty_end_date',
            'status', 'location', 'responsible_person', 'specifications',
            'operating_manual', 'last_maintenance_date', 'next_maintenance_date',
            'maintenance_interval', 'remarks'
        ]
        labels = {
            'last_maintenance_date': '上次校验日期',
            'next_maintenance_date': '下次校验日期',
            'maintenance_interval': '校验间隔',
        }
        widgets = {
            'purchase_date': forms.DateInput(attrs={'type': 'date'}),
            'warranty_end_date': forms.DateInput(attrs={'type': 'date'}),
            'last_maintenance_date': forms.DateInput(attrs={'type': 'date'}),
            'next_maintenance_date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 设置负责人选项（只显示活跃用户）
        self.fields['responsible_person'].queryset = User.objects.filter(
            account_status=True
        ).order_by('username')
        self.fields['responsible_person'].empty_label = "请选择负责人"
        
        # 设置必填字段
        required_fields = ['equipment_id', 'name', 'model', 'manufacturer', 
                          'serial_number', 'location', 
                          'specifications']
        for field_name in required_fields:
            if field_name in self.fields:
                self.fields[field_name].required = True
    
    def clean_equipment_id(self):
        """验证设备编号"""
        equipment_id = self.cleaned_data.get('equipment_id')
        if equipment_id:
            # 检查设备编号是否已存在（排除当前实例）
            queryset = Equipment.objects.filter(equipment_id=equipment_id)
            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise forms.ValidationError('设备编号已存在')
        return equipment_id
    
    def clean_serial_number(self):
        """验证序列号"""
        serial_number = self.cleaned_data.get('serial_number')
        if serial_number:
            # 检查序列号是否已存在（排除当前实例）
            queryset = Equipment.objects.filter(serial_number=serial_number)
            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise forms.ValidationError('序列号已存在')
        return serial_number


class EquipmentUsageRecordForm(BaseEquipmentForm):
    """设备使用记录表单"""
    
    class Meta:
        model = EquipmentUsageRecord
        fields = [
            'equipment', 'user', 'test_task', 'start_time', 'end_time',
            'usage_purpose', 'usage_notes', 'equipment_condition'
        ]
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 设置用户选择
        self.fields['user'].queryset = User.objects.filter(account_status=True)
        self.fields['user'].empty_label = "请选择使用人"
        
        # 设置设备选择（只显示可用设备）
        self.fields['equipment'].queryset = Equipment.objects.filter(
            status__in=['available', 'in_use']
        )
        self.fields['equipment'].empty_label = "请选择设备"
        
        # 设置必填字段
        required_fields = ['equipment', 'user', 'start_time', 'usage_purpose']
        for field_name in required_fields:
            if field_name in self.fields:
                self.fields[field_name].required = True
    
    def clean(self):
        """表单整体验证"""
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        
        if start_time and end_time:
            if end_time <= start_time:
                raise forms.ValidationError('结束时间必须晚于开始时间')
        
        return cleaned_data


class EquipmentMaintenanceForm(BaseEquipmentForm):
    """设备维护记录表单"""
    
    class Meta:
        model = EquipmentMaintenance
        fields = [
            'equipment', 'maintenance_type', 'maintenance_date', 'maintenance_person',
            'maintenance_content', 'parts_replaced', 'maintenance_cost',
            'maintenance_result', 'next_maintenance_date', 'remarks'
        ]
        widgets = {
            'maintenance_date': forms.DateInput(attrs={'type': 'date'}),
            'next_maintenance_date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 设置维护人员选择
        self.fields['maintenance_person'].queryset = User.objects.filter(account_status=True)
        self.fields['maintenance_person'].empty_label = "请选择维护人员"
        
        # 设置设备选择
        self.fields['equipment'].queryset = Equipment.objects.all()
        self.fields['equipment'].empty_label = "请选择设备"
        
        # 设置必填字段
        required_fields = ['equipment', 'maintenance_type', 'maintenance_date', 
                          'maintenance_person', 'maintenance_content']
        for field_name in required_fields:
            if field_name in self.fields:
                self.fields[field_name].required = True
    
    def clean_maintenance_cost(self):
        """验证维护费用"""
        cost = self.cleaned_data.get('maintenance_cost')
        if cost and cost < 0:
            raise forms.ValidationError('维护费用不能为负数')
        return cost


class EquipmentSearchForm(forms.Form):
    """设备搜索表单"""
    
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '搜索设备编号、名称、型号...'
        }),
        label='搜索关键词'
    )
    
    status = forms.ChoiceField(
        choices=[('', '全部状态')] + Equipment.EQUIPMENT_STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='设备状态'
    )
    
    manufacturer = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '制造商'
        }),
        label='制造商'
    )
    
    location = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '存放位置'
        }),
        label='存放位置'
    )
    
    responsible_person = forms.ModelChoiceField(
        queryset=User.objects.filter(account_status=True),
        required=False,
        empty_label='全部负责人',
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='负责人'
    )
    
    maintenance_due = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='需要维护'
    )
    
    warranty_expired = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='保修过期'
    )


class EquipmentUsageSearchForm(forms.Form):
    """设备使用记录搜索表单"""
    
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '搜索设备名称、使用人...'
        }),
        label='搜索关键词'
    )
    
    equipment = forms.ModelChoiceField(
        queryset=Equipment.objects.all(),
        required=False,
        empty_label='全部设备',
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='设备'
    )
    
    user = forms.ModelChoiceField(
        queryset=User.objects.filter(account_status=True),
        required=False,
        empty_label='全部使用人',
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='使用人'
    )
    
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label='开始日期'
    )
    
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label='结束日期'
    )
    
    equipment_condition = forms.ChoiceField(
        choices=[('', '全部状态')] + [
            ('normal', '正常'),
            ('abnormal', '异常'),
            ('damaged', '损坏'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='设备状态'
    )


class EquipmentMaintenanceSearchForm(forms.Form):
    """设备维护记录搜索表单"""
    
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '搜索设备名称、维护人员...'
        }),
        label='搜索关键词'
    )
    
    equipment = forms.ModelChoiceField(
        queryset=Equipment.objects.all(),
        required=False,
        empty_label='全部设备',
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='设备'
    )
    
    maintenance_type = forms.ChoiceField(
        choices=[('', '全部类型')] + EquipmentMaintenance.MAINTENANCE_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='维护类型'
    )
    
    maintenance_person = forms.ModelChoiceField(
        queryset=User.objects.filter(account_status=True),
        required=False,
        empty_label='全部维护人员',
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='维护人员'
    )
    
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label='开始日期'
    )
    
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label='结束日期'
    )
    
    maintenance_result = forms.ChoiceField(
        choices=[('', '全部结果')] + [
            ('completed', '完成'),
            ('pending', '待完成'),
            ('failed', '失败'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='维护结果'
    )