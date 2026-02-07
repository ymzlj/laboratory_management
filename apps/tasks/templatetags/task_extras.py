"""
自定义模板标签和过滤器
"""
from django import template
from django.conf import settings
import os

register = template.Library()


@register.filter(name='attr')
def attr(obj, attr_name):
    """
    获取对象的属性或项（支持Form字段访问）
    用法: {{ form|attr:"field_name" }}
    """
    # 先尝试作为字典或类似对象获取 (针对Django Form字段访问 form['field_name'])
    try:
        return obj[attr_name]
    except (TypeError, KeyError, IndexError, AttributeError):
        pass
    
    # 尝试作为属性获取
    try:
        return getattr(obj, attr_name)
    except AttributeError:
        return None


@register.filter(name='get_item')
def get_item(dictionary, key):
    """
    从字典中获取值，也支持从Form中获取BoundField
    用法: {{ dict|get_item:"key" }}
    """
    if dictionary is None:
        return None
    
    # 支持字典的 .get() 方法
    if hasattr(dictionary, 'get'):
        return dictionary.get(key, '')
    
    # 支持通过下标访问 (如 Form['field_name'])
    try:
        return dictionary[key]
    except (TypeError, KeyError, IndexError):
        return ''

@register.filter(name='is_list')
def is_list(value):
    try:
        return isinstance(value, (list, tuple))
    except Exception:
        return False

@register.filter(name='media_url')
def media_url(path):
    if not path:
        return ''
    try:
        p = str(path)
        if p.startswith('http://') or p.startswith('https://'):
            return p
        base = settings.MEDIA_URL or '/media/'
        if not base.endswith('/'):
            base = base + '/'
            
        # 检查是否已经包含base路径
        if p.startswith(base):
            return p
        if p.startswith('/') and p.startswith(base.rstrip('/')):
             return p
             
        if p.startswith('/'):
            p = p.lstrip('/')
        return base + p
    except Exception:
        return path

@register.filter(name='filename')
def filename(path):
    try:
        return os.path.basename(str(path))
    except Exception:
        return path

@register.filter(name='images_to_json')
def images_to_json(file_list):
    """
    将文件路径列表转换为JSON字符串，包含url和name，用于前端展示
    """
    import json
    if not file_list:
        return '[]'
    
    # 确保是列表
    if not isinstance(file_list, (list, tuple)):
        file_list = [file_list]
        
    photos = []
    for p in file_list:
        # 复用media_url和filename的逻辑
        url = media_url(p)
        name = filename(p)
        photos.append({'url': url, 'name': name})
    
    return json.dumps(photos)


@register.filter(name='split')
def split(value, arg):
    """
    将字符串按指定分隔符分割为列表
    用法: {{ string|split:";" }}
    如果value已经是列表，直接返回
    """
    if not value:
        return []
    if isinstance(value, (list, tuple)):
        return value
    return str(value).split(arg)
