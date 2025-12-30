# myapp/templatetags/get_item.py
from django import template

register = template.Library()

@register.filter
def get_item(lst, index):
    """通过索引获取列表/字典的元素"""
    try:
        # 如果是数字索引（字符串形式）
        if isinstance(index, str) and index.isdigit():
            index = int(index)
        return lst[index]
    except (IndexError, TypeError, KeyError):
        return None

@register.filter
def get_item_safe(lst, index, default=''):
    """带默认值的索引访问"""
    try:
        if isinstance(index, str) and index.isdigit():
            index = int(index)
        return lst[index]
    except (IndexError, TypeError, KeyError):
        return default