"""
通用试验数据批量录入表单
根据试验类型的字段配置动态生成表单字段
"""
from django import forms
from django.forms import formset_factory


class GenericTestDataForm(forms.Form):
    """通用试验数据表单（单条记录）- 根据试验类型动态生成字段"""
    
    # 试验编号字段（只读，自动生成）
    test_number = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-sm',
            'readonly': 'readonly',
            'placeholder': '自动生成',
            'style': 'background-color: #e9ecef;'
        }),
        label='试验编号'
    )
    
    def __init__(self, *args, test_type=None, subtask=None, fields_config=None, **kwargs):
        """
        初始化表单，根据试验类型动态添加字段
        
        参数:
            test_type: TestType实例，用于获取字段配置
            subtask: SubTask实例
            fields_config: 预加载的字段配置列表，避免重复查询
        """
        super().__init__(*args, **kwargs)
        self._subtask = subtask
        
        if fields_config is not None:
            fields = fields_config
        elif test_type:
            # 获取该试验类型的字段配置
            fields = test_type.custom_fields.filter(is_active=True).order_by('order', 'id')
        else:
            fields = []
            
        # 获取已保存的数据
        existing_data = self.initial or {}
            
        # 根据字段配置动态添加表单字段
        for field_config in fields:
            field_code = field_config.field_code
            field_name = field_config.field_name
            field_type = field_config.field_type
            is_required = field_config.is_required
            placeholder = field_config.placeholder or f'请输入{field_name}'
            
            # 获取初始值
            initial_value = existing_data.get(field_code, field_config.default_value or '')
            
            # 智能识别日期字段：如果字段代码包含 date 且被配置为文本类型，强制转为日期类型
            if field_type == 'text' and 'date' in field_code.lower():
                field_type = 'date'
            
            # 根据字段类型创建对应的表单字段
            if field_type == 'text':
                self.fields[field_code] = forms.CharField(
                    required=False,  # 批量录入时设为非必填，在clean时验证
                    initial=initial_value,
                    label=field_name,
                    widget=forms.TextInput(attrs={
                        'class': 'form-control form-control-sm',
                        'placeholder': placeholder
                    })
                )
            elif field_type == 'textarea':
                self.fields[field_code] = forms.CharField(
                    required=False,
                    initial=initial_value,
                    label=field_name,
                    widget=forms.Textarea(attrs={
                        'class': 'form-control form-control-sm',
                        'rows': 2,
                        'placeholder': placeholder
                    })
                )
            elif field_type == 'number':
                self.fields[field_code] = forms.IntegerField(
                    required=False,
                    initial=initial_value,
                    label=field_name,
                    widget=forms.NumberInput(attrs={
                        'class': 'form-control form-control-sm',
                        'placeholder': placeholder
                    })
                )
            elif field_type == 'decimal':
                self.fields[field_code] = forms.DecimalField(
                    required=False,
                    initial=initial_value,
                    label=field_name,
                    widget=forms.NumberInput(attrs={
                        'class': 'form-control form-control-sm',
                        'step': '0.01',
                        'placeholder': placeholder
                    })
                )
            elif field_type == 'date':
                self.fields[field_code] = forms.DateField(
                    required=False,
                    initial=initial_value,
                    label=field_name,
                    widget=forms.TextInput(attrs={
                        'class': 'form-control form-control-sm flatpickr-date',
                        'placeholder': 'YYYY-MM-DD'
                    })
                )
            elif field_type == 'datetime':
                self.fields[field_code] = forms.DateTimeField(
                    required=False,
                    initial=initial_value,
                    label=field_name,
                    widget=forms.TextInput(attrs={
                        'class': 'form-control form-control-sm flatpickr-datetime',
                        'placeholder': 'YYYY-MM-DD HH:mm'
                    })
                )
            elif field_type == 'select':
                options = field_config.field_options.get('options', [])
                choices = [('', '请选择')] + [(opt, opt) for opt in options]
                self.fields[field_code] = forms.ChoiceField(
                    required=False,
                    initial=initial_value,
                    label=field_name,
                    choices=choices,
                    widget=forms.Select(attrs={
                        'class': 'form-select form-select-sm'
                    })
                )
            elif field_type == 'checkbox':
                self.fields[field_code] = forms.BooleanField(
                    required=False,
                    initial=initial_value,
                    label=field_name,
                    widget=forms.CheckboxInput(attrs={
                        'class': 'form-check-input'
                    })
                )
            elif field_type == 'file':
                accept = 'image/*'  # 默认图片
                try:
                    opts = field_config.field_options or {}
                    acc = opts.get('accept')
                    if acc:
                        accept = acc
                except Exception:
                    pass
                self.fields[field_code] = forms.FileField(
                    required=False,
                    label=field_name,
                    help_text=placeholder,
                    widget=forms.FileInput(attrs={
                        'class': 'form-control form-control-sm',
                        'accept': accept
                    })
                )
            
            # 存储字段配置信息（用于后续验证）
            if not hasattr(self, '_field_configs'):
                self._field_configs = {}
            self._field_configs[field_code] = field_config
    
    def clean(self):
        """验证表单数据"""
        cleaned_data = super().clean()
        
        # 检查是否为空行（所有动态字段都为空）
        has_data = False
        for field_code in cleaned_data:
            if field_code != 'test_number' and cleaned_data.get(field_code):
                has_data = True
                break
        
        # 如果是空行，跳过验证
        if not has_data:
            return cleaned_data
        
        # 验证必填字段
        if hasattr(self, '_field_configs'):
            for field_code, field_config in self._field_configs.items():
                if field_config.is_required and not cleaned_data.get(field_code):
                    self.add_error(field_code, f'{field_config.field_name}为必填项')
        
        return cleaned_data
    
    def get_test_data(self):
        """提取动态字段数据为字典"""
        test_data = {}
        from django.core.files.storage import default_storage
        for field_name, field_value in self.cleaned_data.items():
            if field_name != 'test_number':
                # 文件类型处理：保存文件并记录路径
                cfg = None
                if hasattr(self, '_field_configs'):
                    cfg = self._field_configs.get(field_name)
                if cfg and getattr(cfg, 'field_type', '') == 'file':
                    saved_paths = []
                    try:
                        prefixed_key = self.add_prefix(field_name)
                        files_list = self.files.getlist(prefixed_key)
                    except Exception:
                        files_list = []
                    if files_list:
                        subtask_id = getattr(self._subtask, 'id', None)
                        base_dir = f"generic_data/{subtask_id or 'unknown'}/{field_name}"
                        for f in files_list:
                            name = getattr(f, 'name', 'upload.bin')
                            path = default_storage.save(f"{base_dir}/{name}", f)
                            saved_paths.append(path)
                        test_data[field_name] = saved_paths
                    elif field_value:
                        # 兼容单文件上传
                        subtask_id = getattr(self._subtask, 'id', None)
                        base_dir = f"generic_data/{subtask_id or 'unknown'}/{field_name}"
                        name = getattr(field_value, 'name', 'upload.bin')
                        path = default_storage.save(f"{base_dir}/{name}", field_value)
                        test_data[field_name] = [path]
                else:
                    if field_value is not None and field_value != '':
                        # 转换为字符串存储
                        test_data[field_name] = str(field_value)
        return test_data


def create_generic_test_data_formset(test_type, extra=1, subtask=None, fields_config=None):
    """
    创建通用试验数据表单集工厂函数
    
    参数:
        test_type: TestType实例 (保留参数以兼容旧调用，实际通过form_kwargs传递)
        extra: 额外显示的空表单数量
        subtask: 当前子任务对象 (保留参数以兼容旧调用)
        fields_config: 预加载的字段配置列表 (保留参数以兼容旧调用)
    
    返回:
        表单集类
    """
    # 创建表单集
    formset_class = formset_factory(
        GenericTestDataForm,
        extra=extra,
        can_delete=True,
        max_num=100
    )
    
    return formset_class
