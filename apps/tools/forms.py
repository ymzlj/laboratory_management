from django import forms
from .models import Tool

class ToolForm(forms.ModelForm):
    """工具表单"""
    class Meta:
        model = Tool
        fields = [
            'tool_id', 'name', 'type', 'model', 'manufacturer',
            'purchase_date', 'purchase_price', 'status', 'location', 
            'responsible_person', 'specifications', 
            'material', 'dimensions', 'weight',
            'accuracy', 'measurement_range',
            'last_calibration_date', 'next_calibration_date', 'calibration_interval',
            'remarks'
        ]
        labels = {
            'tool_id': '工具编号',
            'name': '工具名称',
            'type': '工具类型',
            'model': '规格型号',
            'manufacturer': '制造商',
            'purchase_date': '采购日期',
            'purchase_price': '采购价格',
            'status': '状态',
            'location': '存放位置',
            'responsible_person': '负责人',
            'specifications': '技术规格',
            'material': '材质',
            'dimensions': '尺寸规格',
            'weight': '重量(kg)',
            'accuracy': '精度',
            'measurement_range': '测量范围',
            'last_calibration_date': '上次校准日期',
            'next_calibration_date': '下次校准日期',
            'calibration_interval': '校准间隔(天)',
            'remarks': '备注',
        }
        widgets = {
            'purchase_date': forms.DateInput(attrs={'type': 'date'}),
            'last_calibration_date': forms.DateInput(attrs={'type': 'date'}),
            'next_calibration_date': forms.DateInput(attrs={'type': 'date'}),
            'specifications': forms.Textarea(attrs={'rows': 3}),
            'remarks': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 统一添加样式
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
        
        # 设置必填字段
        required_fields = ['tool_id', 'name', 'type', 'location']
        for field_name in required_fields:
            if field_name in self.fields:
                self.fields[field_name].required = True
        
        # 设置非必填字段
        optional_fields = ['purchase_date', 'purchase_price', 'specifications', 'remarks']
        for field_name in optional_fields:
            if field_name in self.fields:
                self.fields[field_name].required = False


class ToolSearchForm(forms.Form):
    """工具搜索表单"""
    search = forms.CharField(
        label='关键词搜索',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '工具编号/名称/型号'
        })
    )
    status = forms.ChoiceField(
        label='状态',
        required=False,
        choices=[('', '全部')] + Tool.TOOL_STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    type = forms.CharField(
        label='工具类型',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '输入类型'
        })
    )
    location = forms.CharField(
        label='存放位置',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '存放位置'
        })
    )
