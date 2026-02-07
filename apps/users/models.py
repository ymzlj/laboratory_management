"""
用户模块数据模型
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.Model):
    """角色模型"""
    ROLE_CODE_CHOICES = [
        ('admin', '系统管理员'),
        ('manager', '试验室主管'),
        ('engineer', '试验工程师'),
        ('equipment_manager', '设备管理员'),
        ('guest', '访客'),
    ]
    
    # 权限选项
    PERMISSION_CHOICES = [
        ('user_manage', '用户管理'),
        ('role_manage', '角色管理'),
        ('department_manage', '部门管理'),
        ('task_manage', '任务管理'),
        ('task_assign', '任务分配'),
        ('data_manage', '数据管理'),
        ('equipment_manage', '设备管理'),
        ('tooling_manage', '工装管理'),
        ('tools_manage', '工具管理'),
        ('report_view', '报表查看'),
        ('system_config', '系统配置'),
    ]
    
    name = models.CharField(max_length=50, verbose_name='角色名称')
    code = models.CharField(
        max_length=20, 
        unique=True, 
        choices=ROLE_CODE_CHOICES,
        verbose_name='角色代码'
    )
    description = models.TextField(blank=True, verbose_name='角色描述')
    
    # 权限字段（使用JSONField存储权限列表）
    permissions = models.JSONField(default=list, verbose_name='权限列表')
    
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'roles'
        verbose_name = '角色'
        verbose_name_plural = '角色'
        ordering = ['code']
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    def has_permission(self, permission_code):
        """检查是否拥有某个权限"""
        return permission_code in self.permissions


class Department(models.Model):
    """部门模型"""
    name = models.CharField(max_length=100, verbose_name='部门名称')
    code = models.CharField(max_length=20, unique=True, verbose_name='部门代码')
    description = models.TextField(blank=True, verbose_name='部门描述')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'departments'
        verbose_name = '部门'
        verbose_name_plural = '部门'

    def __str__(self):
        return str(self.name)


class User(AbstractUser):
    """用户模型"""
    USER_ROLE_CHOICES = [
        ('admin', '系统管理员'),
        ('manager', '试验室主管'),
        ('engineer', '试验工程师'),
        ('equipment_manager', '设备管理员'),
        ('guest', '访客'),
    ]
    
    employee_id = models.CharField(max_length=20, unique=True, verbose_name='工号')  # 对应user_code
    department = models.ForeignKey(
        Department, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name='部门'
    )
    phone = models.CharField(max_length=20, verbose_name='手机号')  # 数据库中不是NULL
    position = models.CharField(max_length=100, blank=True, verbose_name='职位')
    role = models.CharField(
        max_length=20, 
        choices=USER_ROLE_CHOICES, 
        default='engineer',
        verbose_name='角色'
    )
    # 根据数据库中的account_status字段，0表示冻结，1表示正常
    account_status = models.BooleanField(default=True, verbose_name='账户状态')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta(AbstractUser.Meta):
        db_table = 'users'
        verbose_name = '用户'
        verbose_name_plural = '用户'

    def __str__(self):
        return f"{self.username} ({self.employee_id})"
        
    @property
    def is_active(self):
        """重写is_active属性，使其与account_status保持一致"""
        return self.account_status
        
    @is_active.setter
    def is_active(self, value):
        """设置is_active时同时更新account_status"""
        self.account_status = value
