"""
自定义模板过滤器
"""
from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """
    获取字典中的值
    用法: {{ mydict|get_item:key }}
    """
    if dictionary is None:
        return None
    try:
        return dictionary.get(key)
    except (AttributeError, TypeError):
        return None


@register.filter
def get_attr(obj, attr):
    """
    获取对象的属性
    用法: {{ obj|get_attr:field_name }}
    """
    if obj is None:
        return None
    try:
        return getattr(obj, attr)
    except AttributeError:
        return None


@register.filter
def multiply(value, arg):
    """
    乘法运算
    用法: {{ value|multiply:2 }}
    """
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def divide(value, arg):
    """
    除法运算
    用法: {{ value|divide:2 }}
    """
    try:
        return float(value) / float(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0


@register.filter
def subtract(value, arg):
    """
    减法运算
    用法: {{ value|subtract:2 }}
    """
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def add_value(value, arg):
    """
    加法运算
    用法: {{ value|add_value:2 }}
    """
    try:
        return float(value) + float(arg)
    except (ValueError, TypeError):
        return value
