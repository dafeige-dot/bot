"""
翻译器模块
"""
from typing import Optional
from app.i18n.translations import get_text as _get_text

# 用户语言缓存
_user_languages = {}


def set_language(user_id: int, lang: str) -> None:
    """设置用户语言"""
    _user_languages[user_id] = lang


def get_language(user_id: int) -> str:
    """获取用户语言，默认中文"""
    return _user_languages.get(user_id, 'zh')


def get_text(key: str, user_id: Optional[int] = None, lang: Optional[str] = None, **kwargs) -> str:
    """
    获取翻译文本
    
    Args:
        key: 翻译键
        user_id: 用户ID（用于获取用户语言偏好）
        lang: 强制指定语言
        **kwargs: 格式化参数
    
    Returns:
        翻译后的文本
    """
    if lang is None and user_id is not None:
        lang = get_language(user_id)
    elif lang is None:
        lang = 'zh'
    
    return _get_text(key, lang, **kwargs)


