"""
试验任务管理表单
"""
from django import forms
from django.contrib.auth import get_user_model
from django.forms import formset_factory
from .models import TestTask, TestType, TestTypeField, PriorityType, TaskStatus, SubTask, SubTaskData
from apps.users.models import Department

# 导入通用批量录入表单
from .generic_forms import GenericTestDataForm, create_generic_test_data_formset

User = get_user_model()


class TestTypeForm(forms.ModelForm):
    """试验类型表单"""
    
    class Meta:
        model = TestType
        fields = ['name', 'code', 'description', 'level_type', 'parent']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入试验类型名称'
            }),
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入试验类型代码（唯一标识）'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': '请输入试验类型描述'
            }),
            'level_type': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_level_type'
            }),
            'parent': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_parent'
            }),
        }
        labels = {
            'name': '试验类型名称',
            'code': '试验类型代码',
            'description': '试验类型描述',
            'level_type': '类型级别',
            'parent': '所属总类型',
        }
        help_texts = {
            'code': '用于系统内部识别的唯一代码，只能包含字母、数字和下划线',
            'parent': '仅当类型级别为"分试验类型"时需要选择',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 限制父级选择只能是总试验类型
        self.fields['parent'].queryset = TestType.objects.filter(level_type=1)
        self.fields['parent'].empty_label = "请选择所属总类型"

    def clean(self):
        cleaned_data = super().clean()
        level_type = cleaned_data.get('level_type')
        parent = cleaned_data.get('parent')

        if level_type == 2 and not parent:
            self.add_error('parent', '分试验类型必须选择所属总类型！')
        
        return cleaned_data
    
    def clean_code(self):
        """验证试验类型代码格式"""
        code = self.cleaned_data.get('code')
        if code:
            import re
            if not re.match(r'^[a-zA-Z0-9_]+$', code):
                raise forms.ValidationError('试验类型代码只能包含字母、数字和下划线！')
        return code


class TestTaskForm(forms.ModelForm):
    """试验任务表单"""
    
    # 将申请人部门改为下拉框选择
    requester_department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        required=False,
        empty_label="请选择部门",
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='申请人部门'
    )
    
    class Meta:
        model = TestTask
        fields = [
            'task_name', 'product_name', 'product_model', 'test_type', 'priority',
            'requester_name', 'requester_phone', 'requester_department',
            'description', 'test_outline_file',
            'start_date', 'end_date'
        ]
        widgets = {
            'task_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入任务名称'
            }),
            'product_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入产品名称（可选）',
                'maxlength': '50'
            }),
            'product_model': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入产品型号（可选）',
                'maxlength': '20'
            }),
            'test_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'priority': forms.Select(attrs={
                'class': 'form-select'
            }),
            'requester_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入申请人姓名'
            }),
            'requester_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入申请人手机号'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': '请输入任务描述（可选）'
            }),
            'test_outline_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.txt'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }
        labels = {
            'task_name': '任务名称',
            'product_name': '产品名称',
            'product_model': '产品型号',
            'test_type': '试验类型',
            'priority': '优先级',
            'requester_name': '申请人姓名',
            'requester_phone': '申请人手机号',
            'requester_department': '申请人部门',
            'description': '任务描述',
            'test_outline_file': '试验大纲文件',
            'start_date': '计划开始日期',
            'end_date': '计划结束日期',
        }
        help_texts = {
            'test_outline_file': '支持PDF、Word、文本文件',
        }
    
    def __init__(self, *args, **kwargs):
        # 提取request参数以获取当前用户
        self.request = kwargs.pop('request', None)
        # 提取user参数（兼容views中传递user的情况）
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # 设置试验类型选项
        self.fields['test_type'].queryset = TestType.objects.filter(level_type=1).order_by('code')
        self.fields['test_type'].empty_label = "请选择试验类型"
        
        # 设置优先级选项
        self.fields['priority'].queryset = PriorityType.objects.all().order_by('level')
        self.fields['priority'].empty_label = "请选择优先级"
        
        # 如果是创建新任务，自动填充申请人信息
        if not self.instance.pk:
            # 优先使用直接传递的user，其次尝试从request获取
            user = self.user
            if not user and self.request:
                user = self.request.user
                
            if user and user.is_authenticated:
                self.fields['requester_name'].initial = user.get_full_name() or user.username
                self.fields['requester_phone'].initial = user.phone
                # 设置部门下拉框的默认值为当前用户的部门
                if hasattr(user, 'department') and user.department:
                    self.fields['requester_department'].initial = user.department
        else:
            # 如果是编辑任务，将存储的部门名称转换为Department对象
            if self.instance.requester_department:
                try:
                    department = Department.objects.get(name=self.instance.requester_department)
                    self.fields['requester_department'].initial = department
                except Department.DoesNotExist:
                    pass
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        product_model = cleaned_data.get('product_model')
        
        # 验证产品型号格式：只能包含字母、数字和短横线
        if product_model:
            import re
            if not re.match(r'^[a-zA-Z0-9-]+$', product_model):
                self.add_error('product_model', '产品型号只能包含字母、数字和短横线！')
        
        if start_date and end_date:
            if start_date > end_date:
                raise forms.ValidationError('开始日期不能晚于结束日期！')
        
        return cleaned_data
    
    def save(self, commit=True):
        """保存表单，将部门对象转换为部门名称字符串，并设置默认状态"""
        instance = super().save(commit=False)
        
        # 将部门对象转换为部门名称
        department = self.cleaned_data.get('requester_department')
        if department:
            instance.requester_department = department.name
        else:
            instance.requester_department = ''
        
        # 如果是新建任务，自动设置状态为待分配
        if not instance.pk:
            try:
                pending_status = TaskStatus.objects.get(code='pending')
                instance.status = pending_status
            except TaskStatus.DoesNotExist:
                # 如果找不到待分配状态，尝试获取第一个状态
                first_status = TaskStatus.objects.first()
                if first_status:
                    instance.status = first_status
        
        if commit:
            instance.save()
        
        return instance


class TestTaskSearchForm(forms.Form):
    """试验任务搜索表单"""
    
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '搜索任务编号、名称或描述'
        }),
        label='关键词'
    )
    
    test_type = forms.ModelChoiceField(
        queryset=TestType.objects.filter(level_type=1),
        required=False,
        empty_label="所有类型",
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='试验类型'
    )
    
    priority = forms.ModelChoiceField(
        queryset=PriorityType.objects.all(),
        required=False,
        empty_label="所有优先级",
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='优先级'
    )
    
    status = forms.ModelChoiceField(
        queryset=TaskStatus.objects.all(),
        required=False,
        empty_label="所有状态",
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='状态'
    )
    
    assignee = forms.ModelChoiceField(
        queryset=User.objects.filter(account_status=True),
        required=False,
        empty_label="所有负责人",
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='负责人'
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='开始日期从'
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='开始日期到'
    )
    
    def clean(self):
        cleaned_data = super().clean()
        date_from = cleaned_data.get('date_from')
        date_to = cleaned_data.get('date_to')
        
        if date_from and date_to:
            if date_from > date_to:
                raise forms.ValidationError('开始日期不能晚于结束日期！')
        
        return cleaned_data


class TaskAssignForm(forms.Form):
    """任务分配表单"""
    
    assignee = forms.ModelChoiceField(
        queryset=User.objects.filter(account_status=True),
        required=False,
        empty_label="取消分配",
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'assignee_id'
        }),
        label='分配给'
    )


class TaskStatusUpdateForm(forms.Form):
    """任务状态更新表单"""
    
    status = forms.ModelChoiceField(
        queryset=TaskStatus.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='状态'
    )
    
    remarks = forms.CharField(
        max_length=500,
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': '状态更新说明（可选）'
        }),
        label='备注'
    )


class TaskDecomposeForm(forms.Form):
    """任务分解表单"""
    
    main_test_type = forms.ModelChoiceField(
        queryset=TestType.objects.filter(level_type=1),
        label='总试验类型',
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_main_test_type'})
    )
    
    test_types = forms.ModelMultipleChoiceField(
        queryset=TestType.objects.filter(level_type=2),
        widget=forms.CheckboxSelectMultiple,
        label='分试验类型',
        help_text='选择需要分解的试验类型'
    )
    
    def __init__(self, *args, **kwargs):
        task = kwargs.pop('task', None)
        super().__init__(*args, **kwargs)
        
        if task and task.test_type:
            # 如果有任务实例，设置默认总类型
            self.fields['main_test_type'].initial = task.test_type
            # 限制分类型为该总类型下的子类型
            sub_types = TestType.objects.filter(
                level_type=2, 
                parent=task.test_type
            )
            
            if not sub_types.exists():
                # 如果没有子类型，允许选择主类型作为默认子类型（自动继承）
                self.fields['test_types'].queryset = TestType.objects.filter(id=task.test_type.id)
                self.fields['test_types'].initial = [task.test_type]
                self.fields['test_types'].help_text = "⚠️ 该类型无子类型，已自动选择主类型作为默认分解类型（将继承主类型配置）"
            else:
                self.fields['test_types'].queryset = sub_types
        else:
             # 如果没有指定任务，默认显示所有分类型（或空）
             # 这里为了AJAX体验，可以先保留空或者全部，前端会重置
             pass


class SubTaskForm(forms.ModelForm):
    """子任务表单"""
    
    class Meta:
        model = SubTask
        fields = ['subtask_name', 'test_type', 'status', 'assignee', 
                  'description', 'start_date', 'end_date']
        widgets = {
            'subtask_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入子任务名称'
            }),
            'test_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'assignee': forms.Select(attrs={
                'class': 'form-select'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '请输入子任务描述'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }
        labels = {
            'subtask_name': '子任务名称',
            'test_type': '试验类型',
            'status': '状态',
            'assignee': '负责人',
            'description': '子任务描述',
            'start_date': '开始日期',
            'end_date': '结束日期',
        }


class SubTaskDataForm(forms.ModelForm):
    """子任务数据录入表单 - 支持动态字段"""
    
    class Meta:
        model = SubTaskData
        fields = ['test_conditions', 'test_method', 'test_equipment', 
                  'test_result', 'test_conclusion', 'remarks', 'data_file']
        widgets = {
            'test_conditions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '请输入试验条件'
            }),
            'test_method': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '请输入试验方法'
            }),
            'test_equipment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': '请输入使用的试验设备'
            }),
            'test_result': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': '请输入试验结果'
            }),
            'test_conclusion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '请输入试验结论'
            }),
            'remarks': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': '备注信息'
            }),
            'data_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.xlsx,.xls,.txt'
            }),
        }
        labels = {
            'test_conditions': '试验条件',
            'test_method': '试验方法',
            'test_equipment': '试验设备',
            'test_result': '试验结果',
            'test_conclusion': '试验结论',
            'remarks': '备注',
            'data_file': '数据文件',
        }
        help_texts = {
            'data_file': '支持PDF、Word、Excel、文本文件',
        }
    
    def __init__(self, *args, **kwargs):
        """初始化表单，根据试验类型动态添加字段"""
        # 获取试验类型（通过subtask传递）
        subtask = kwargs.pop('subtask', None)
        super().__init__(*args, **kwargs)
        
        # 如果有subtask，根据其试验类型动态添加字段
        if subtask and subtask.test_type:
            # 使用模型方法获取字段（支持继承）
            all_fields = subtask.test_type.get_all_fields()
            # 仅保留非批量录入的字段（元数据）
            custom_fields = [f for f in all_fields if not f.is_batch_input_enabled]
            
            # 获取已保存的数据
            existing_data = self.instance.meta_data if self.instance.pk else {}
            
            for field_config in custom_fields:
                field_name = f"custom_{field_config.field_code}"
                field_label = field_config.field_name
                field_type = field_config.field_type
                is_required = field_config.is_required
                default_value = field_config.default_value
                placeholder = field_config.placeholder
                help_text = field_config.help_text
                
                # 获取初始值
                initial_value = existing_data.get(field_config.field_code, default_value or '')
                
                # 根据字段类型创建表单字段
                if field_type == 'text':
                    self.fields[field_name] = forms.CharField(
                        required=is_required,
                        initial=initial_value,
                        label=field_label,
                        help_text=help_text,
                        widget=forms.TextInput(attrs={
                            'class': 'form-control',
                            'placeholder': placeholder or f'请输入{field_label}'
                        })
                    )
                elif field_type == 'textarea':
                    self.fields[field_name] = forms.CharField(
                        required=is_required,
                        initial=initial_value,
                        label=field_label,
                        help_text=help_text,
                        widget=forms.Textarea(attrs={
                            'class': 'form-control',
                            'rows': 3,
                            'placeholder': placeholder or f'请输入{field_label}'
                        })
                    )
                elif field_type == 'number':
                    self.fields[field_name] = forms.IntegerField(
                        required=is_required,
                        initial=initial_value,
                        label=field_label,
                        help_text=help_text,
                        widget=forms.NumberInput(attrs={
                            'class': 'form-control',
                            'placeholder': placeholder or f'请输入{field_label}'
                        })
                    )
                elif field_type == 'decimal':
                    self.fields[field_name] = forms.DecimalField(
                        required=is_required,
                        initial=initial_value,
                        label=field_label,
                        help_text=help_text,
                        widget=forms.NumberInput(attrs={
                            'class': 'form-control',
                            'step': '0.01',
                            'placeholder': placeholder or f'请输入{field_label}'
                        })
                    )
                elif field_type == 'date':
                    self.fields[field_name] = forms.DateField(
                        required=is_required,
                        initial=initial_value,
                        label=field_label,
                        help_text=help_text,
                        widget=forms.DateInput(attrs={
                            'class': 'form-control',
                            'type': 'date'
                        })
                    )
                elif field_type == 'datetime':
                    self.fields[field_name] = forms.DateTimeField(
                        required=is_required,
                        initial=initial_value,
                        label=field_label,
                        help_text=help_text,
                        widget=forms.DateTimeInput(attrs={
                            'class': 'form-control',
                            'type': 'datetime-local'
                        })
                    )
                elif field_type == 'select':
                    options = field_config.field_options.get('options', [])
                    choices = [('', '请选择')] + [(opt, opt) for opt in options]
                    self.fields[field_name] = forms.ChoiceField(
                        required=is_required,
                        initial=initial_value,
                        label=field_label,
                        help_text=help_text,
                        choices=choices,
                        widget=forms.Select(attrs={
                            'class': 'form-select'
                        })
                    )
                elif field_type == 'checkbox':
                    self.fields[field_name] = forms.BooleanField(
                        required=False,  # checkbox不应该是必填
                        initial=initial_value,
                        label=field_label,
                        help_text=help_text,
                        widget=forms.CheckboxInput(attrs={
                            'class': 'form-check-input'
                        })
                    )
                elif field_type == 'file':
                    # 使用placeholder作为help_text（如果help_text为空），确保提示信息可见
                    effective_help_text = help_text or placeholder
                    self.fields[field_name] = forms.FileField(
                        required=is_required,
                        label=field_label,
                        help_text=effective_help_text,
                        widget=forms.FileInput(attrs={
                            'class': 'form-control'
                        })
                    )
    
    def save(self, commit=True):
        """保存时将动态字段数据存入meta_data JSONField"""
        instance = super().save(commit=False)
        
        # 获取所有自定义字段的数据
        meta_data = instance.meta_data or {}
        for field_name, field_value in self.cleaned_data.items():
            if field_name.startswith('custom_'):
                # 提取字段代码
                field_code = field_name.replace('custom_', '')
                # 处理不同类型的值
                if isinstance(field_value, (list, dict)):
                    meta_data[field_code] = field_value
                elif field_value is not None:
                    # 转换为字符串存储
                    meta_data[field_code] = str(field_value)
                else:
                    meta_data[field_code] = ''
        
        instance.meta_data = meta_data
        
        if commit:
            instance.save()
        
        return instance


class TestTypeFieldForm(forms.ModelForm):
    """试验类型字段配置表单"""
    
    # 字段选项（用于select类型）
    options_text = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': '每行一个选项，仅适用于下拉选择类型'
        }),
        label='选项列表',
        help_text='对于下拉选择类型，每行输入一个选项'
    )
    images_order = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
        label='图片顺序'
    )
    
    class Meta:
        model = TestTypeField
        fields = [
            'field_name', 'field_code', 'field_type',
            'is_required', 'default_value', 'placeholder',
            'help_text', 'order', 'is_active', 'is_batch_input_enabled'
        ]
        widgets = {
            'field_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入字段名称'
            }),
            'field_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入字段代码（英文，用于存储）'
            }),
            'field_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'is_required': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'default_value': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '默认值（可选）'
            }),
            'placeholder': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '提示文本（可选）'
            }),
            'help_text': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '帮助文本（可选）'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_batch_input_enabled': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'field_name': '字段名称',
            'field_code': '字段代码',
            'field_type': '字段类型',
            'is_required': '是否必填',
            'default_value': '默认值',
            'placeholder': '提示文本',
            'help_text': '帮助文本',
            'order': '显示顺序',
            'is_active': '是否启用',
            'is_batch_input_enabled': '启用批量录入',
        }
        help_texts = {
            'field_code': '用于数据存储的唯一标识，只能包含字母、数字和下划线',
            'order': '数字越小越靠前',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 新建字段时，默认关闭批量录入（根据需求）
        if not self.instance.pk:
            self.fields['is_batch_input_enabled'].initial = False
            
        # 如果是编辑模式，且字段类型是select，将选项转换为文本
        if self.instance.pk and self.instance.field_type == 'select':
            options = self.instance.field_options.get('options', [])
            self.fields['options_text'].initial = '\n'.join(options)
    
    def clean_field_code(self):
        """验证字段代码格式"""
        code = self.cleaned_data.get('field_code')
        if code:
            import re
            if not re.match(r'^[a-zA-Z0-9_]+$', code):
                raise forms.ValidationError('字段代码只能包含字母、数字和下划线！')
        return code
    
    def save(self, commit=True):
        """保存时处理field_options"""
        instance = super().save(commit=False)
        
        # 如果是下拉选择类型，将options_text转换为field_options
        if instance.field_type == 'select':
            options_text = self.cleaned_data.get('options_text', '')
            if options_text:
                options = [opt.strip() for opt in options_text.split('\n') if opt.strip()]
                instance.field_options = {'options': options}
            else:
                instance.field_options = {'options': []}
        else:
            # 其他类型清空field_options
            instance.field_options = {}
        
        if commit:
            instance.save()
        
        return instance
