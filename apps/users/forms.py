"""
用户模块表单
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.signals import user_logged_in
from django.db import models
from .models import User, Department, Role


class CustomAuthenticationForm(AuthenticationForm):
    """自定义登录表单"""
    
    username = forms.CharField(
        max_length=254,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '用户名或工号',
            'autofocus': True
        }),
        label='用户名'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '密码'
        }),
        label='密码'
    )
    
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            # 查找用户（通过用户名或工号）
            user = None
            
            # 尝试通过用户名查找
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                # 如果通过用户名找不到，尝试通过工号查找
                try:
                    user = User.objects.get(employee_id=username)
                except User.DoesNotExist:
                    # 用户名和工号都找不到用户
                    raise forms.ValidationError('用户名或密码错误')
            
            if user:
                # 尝试认证
                self.user_cache = authenticate(
                    self.request,
                    username=user.username,
                    password=password
                )
                
                if self.user_cache is None:
                    # 密码错误
                    raise forms.ValidationError('用户名或密码错误')
                
                # 检查账户状态
                if not user.account_status:
                    raise forms.ValidationError('该账户已被冻结，请联系管理员。')
                
                self.cleaned_data['user'] = self.user_cache

        return self.cleaned_data


class UserForm(forms.ModelForm):
    """用户表单"""
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='密码',
        required=False
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='确认密码',
        required=False
    )
    
    class Meta:
        model = User
        fields = ('employee_id', 'username', 'email', 'department', 'phone', 'position', 'role', 'account_status')
        widgets = {
            'employee_id': forms.TextInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
            'account_status': forms.Select(attrs={'class': 'form-control'}, choices=[(True, '正常'), (False, '冻结')]),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError('两次输入的密码不一致')
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        
        if password:
            user.set_password(password)
        
        if commit:
            user.save()
        
        return user


class UserProfileForm(forms.ModelForm):
    """用户个人资料编辑表单"""
    # 显示用户名（只读）
    username = forms.CharField(
        label='用户名',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'disabled': 'disabled'})
    )
    # 添加密码修改字段
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '若不修改请留空'}),
        label='新密码',
        required=False
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '确认新密码'}),
        label='确认新密码',
        required=False
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'email', 'phone', 'department', 'position')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入真实姓名'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-control'}),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'first_name': '姓名',
            'email': '邮箱',
            'phone': '手机号',
            'department': '部门',
            'position': '职位',
        }
        help_texts = {
            'email': '',  # 移除默认的帮助文本
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 设置用户名初始值
        if self.instance:
            self.fields['username'].initial = self.instance.username
            # 如果没有真实姓名，默认显示用户名
            if not self.instance.first_name:
                self.initial['first_name'] = self.instance.username
        
        # 设置邮箱为非必填
        self.fields['email'].required = False
        # 确保姓名字段有初始值
        if not self.initial.get('first_name'):
            self.initial['first_name'] = self.instance.first_name

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if new_password:
            if not confirm_password:
                self.add_error('confirm_password', '请确认新密码')
            elif new_password != confirm_password:
                self.add_error('confirm_password', '两次输入的密码不一致')
        
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        new_password = self.cleaned_data.get('new_password')
        
        if new_password:
            user.set_password(new_password)
            
        if commit:
            user.save()
        return user


class CustomUserCreationForm(UserCreationForm):
    """自定义用户创建表单"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': '邮箱地址'
        })
    )
    employee_id = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '工号'
        }),
        label='工号'
    )
    
    # 为避免静态分析工具报错，先定义部门选择字段，稍后在__init__中设置queryset
    department = forms.ModelChoiceField(
        queryset=Department.objects.none(),  # 初始为空
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='部门'
    )
    
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '电话号码'
        }),
        label='电话'
    )
    position = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '职位'
        }),
        label='职位'
    )

    # 明确指定Meta类继承
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'employee_id', 'email', 'department', 'phone', 'position', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '用户名'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '密码'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '确认密码'
        })
        
        # 在初始化时设置部门选择字段的queryset
        self.fields['department'].queryset = Department.objects.all()

    def clean_employee_id(self):
        employee_id = self.cleaned_data['employee_id']
        # 使用exists()方法避免静态分析工具报错
        if User.objects.filter(employee_id=employee_id).exists():
            raise forms.ValidationError('该工号已存在')
        return employee_id

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.employee_id = self.cleaned_data['employee_id']
        user.first_name = ''  # 设置为空字符串
        user.last_name = ''   # 设置为空字符串
        user.department = self.cleaned_data['department']
        user.phone = self.cleaned_data['phone']
        user.position = self.cleaned_data['position']
        # 新用户默认账户状态为正常
        user.account_status = True
        if commit:
            user.save()
        return user


class DepartmentForm(forms.ModelForm):
    """部门表单"""
    
    class Meta:
        model = Department
        fields = ('name', 'code', 'description')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def clean_code(self):
        code = self.cleaned_data['code']
        # 检查部门代码是否唯一
        if Department.objects.filter(code=code).exists():
            raise forms.ValidationError('该部门代码已存在')
        return code


class RoleForm(forms.ModelForm):
    """角色表单"""
    permissions = forms.MultipleChoiceField(
        choices=Role.PERMISSION_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
        label='权限设置'
    )
    
    class Meta:
        model = Role
        fields = ('name', 'code', 'description', 'permissions', 'is_active')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入角色名称'}),
            'code': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': '请输入角色描述'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 如果是编辑模式，初始化权限选项
        if self.instance and self.instance.pk:
            self.initial['permissions'] = self.instance.permissions
    
    def clean_code(self):
        code = self.cleaned_data['code']
        # 检查角色代码是否唯一（编辑时排除自身）
        queryset = Role.objects.filter(code=code)
        if self.instance and self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise forms.ValidationError('该角色代码已存在')
        return code
    
    def save(self, commit=True):
        role = super().save(commit=False)
        # 保存权限列表
        role.permissions = self.cleaned_data.get('permissions', [])
        if commit:
            role.save()
        return role