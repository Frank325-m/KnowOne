"""
验证工具模块
提供输入验证和类型检查功能
"""

import re
from typing import Any, Dict, List, Optional, Union, Callable
from pathlib import Path


def validate_string(
    value: Any,
    name: str = "字符串",
    min_length: int = 1,
    max_length: Optional[int] = None,
    allow_empty: bool = False,
    regex: Optional[str] = None
) -> str:
    """
    验证字符串
    
    Args:
        value: 要验证的值
        name: 参数名称
        min_length: 最小长度
        max_length: 最大长度
        allow_empty: 是否允许空字符串
        regex: 正则表达式模式
        
    Returns:
        验证后的字符串
        
    Raises:
        ValueError: 如果验证失败
    """
    if value is None:
        if allow_empty:
            return ""
        raise ValueError(f"{name} 不能为 None")
    
    if not isinstance(value, str):
        try:
            value = str(value)
        except Exception:
            raise ValueError(f"{name} 必须是字符串类型")
    
    if not allow_empty and not value.strip():
        raise ValueError(f"{name} 不能为空")
    
    if len(value) < min_length:
        raise ValueError(f"{name} 长度不能小于 {min_length}")
    
    if max_length is not None and len(value) > max_length:
        raise ValueError(f"{name} 长度不能大于 {max_length}")
    
    if regex is not None:
        if not re.match(regex, value):
            raise ValueError(f"{name} 格式无效")
    
    return value


def validate_integer(
    value: Any,
    name: str = "整数",
    min_value: Optional[int] = None,
    max_value: Optional[int] = None
) -> int:
    """
    验证整数
    
    Args:
        value: 要验证的值
        name: 参数名称
        min_value: 最小值
        max_value: 最大值
        
    Returns:
        验证后的整数
        
    Raises:
        ValueError: 如果验证失败
    """
    if value is None:
        raise ValueError(f"{name} 不能为 None")
    
    try:
        int_value = int(value)
    except (ValueError, TypeError):
        raise ValueError(f"{name} 必须是整数类型")
    
    if min_value is not None and int_value < min_value:
        raise ValueError(f"{name} 不能小于 {min_value}")
    
    if max_value is not None and int_value > max_value:
        raise ValueError(f"{name} 不能大于 {max_value}")
    
    return int_value


def validate_float(
    value: Any,
    name: str = "浮点数",
    min_value: Optional[float] = None,
    max_value: Optional[float] = None
) -> float:
    """
    验证浮点数
    
    Args:
        value: 要验证的值
        name: 参数名称
        min_value: 最小值
        max_value: 最大值
        
    Returns:
        验证后的浮点数
        
    Raises:
        ValueError: 如果验证失败
    """
    if value is None:
        raise ValueError(f"{name} 不能为 None")
    
    try:
        float_value = float(value)
    except (ValueError, TypeError):
        raise ValueError(f"{name} 必须是数值类型")
    
    if min_value is not None and float_value < min_value:
        raise ValueError(f"{name} 不能小于 {min_value}")
    
    if max_value is not None and float_value > max_value:
        raise ValueError(f"{name} 不能大于 {max_value}")
    
    return float_value


def validate_boolean(value: Any, name: str = "布尔值") -> bool:
    """
    验证布尔值
    
    Args:
        value: 要验证的值
        name: 参数名称
        
    Returns:
        验证后的布尔值
        
    Raises:
        ValueError: 如果验证失败
    """
    if value is None:
        raise ValueError(f"{name} 不能为 None")
    
    if isinstance(value, bool):
        return value
    
    if isinstance(value, str):
        value_lower = value.lower()
        if value_lower in ("true", "1", "yes", "y", "t"):
            return True
        elif value_lower in ("false", "0", "no", "n", "f"):
            return False
    
    try:
        return bool(int(value))
    except (ValueError, TypeError):
        raise ValueError(f"{name} 必须是布尔类型")


def validate_list(
    value: Any,
    name: str = "列表",
    min_length: int = 0,
    max_length: Optional[int] = None,
    item_validator: Optional[Callable] = None
) -> List:
    """
    验证列表
    
    Args:
        value: 要验证的值
        name: 参数名称
        min_length: 最小长度
        max_length: 最大长度
        item_validator: 项目验证函数
        
    Returns:
        验证后的列表
        
    Raises:
        ValueError: 如果验证失败
    """
    if value is None:
        raise ValueError(f"{name} 不能为 None")
    
    if not isinstance(value, (list, tuple, set)):
        raise ValueError(f"{name} 必须是列表类型")
    
    list_value = list(value)
    
    if len(list_value) < min_length:
        raise ValueError(f"{name} 长度不能小于 {min_length}")
    
    if max_length is not None and len(list_value) > max_length:
        raise ValueError(f"{name} 长度不能大于 {max_length}")
    
    if item_validator is not None:
        for i, item in enumerate(list_value):
            try:
                list_value[i] = item_validator(item, f"{name}[{i}]")
            except ValueError as e:
                raise ValueError(f"{name} 第 {i} 项无效: {e}")
    
    return list_value


def validate_dict(
    value: Any,
    name: str = "字典",
    required_keys: Optional[List[str]] = None,
    key_validator: Optional[Callable] = None,
    value_validator: Optional[Callable] = None
) -> Dict:
    """
    验证字典
    
    Args:
        value: 要验证的值
        name: 参数名称
        required_keys: 必需的键
        key_validator: 键验证函数
        value_validator: 值验证函数
        
    Returns:
        验证后的字典
        
    Raises:
        ValueError: 如果验证失败
    """
    if value is None:
        raise ValueError(f"{name} 不能为 None")
    
    if not isinstance(value, dict):
        raise ValueError(f"{name} 必须是字典类型")
    
    dict_value = dict(value)
    
    if required_keys is not None:
        for key in required_keys:
            if key not in dict_value:
                raise ValueError(f"{name} 缺少必需的键: {key}")
    
    if key_validator is not None:
        for key in list(dict_value.keys()):
            try:
                validated_key = key_validator(key, f"{name}键")
                if validated_key != key:
                    dict_value[validated_key] = dict_value.pop(key)
            except ValueError as e:
                raise ValueError(f"{name} 键 '{key}' 无效: {e}")
    
    if value_validator is not None:
        for key, val in dict_value.items():
            try:
                dict_value[key] = value_validator(val, f"{name}['{key}']")
            except ValueError as e:
                raise ValueError(f"{name} 键 '{key}' 的值无效: {e}")
    
    return dict_value


def validate_file_path(
    path: Any,
    name: str = "文件路径",
    must_exist: bool = False,
    must_be_file: bool = False,
    must_be_directory: bool = False,
    extensions: Optional[List[str]] = None
) -> Path:
    """
    验证文件路径
    
    Args:
        path: 要验证的路径
        name: 参数名称
        must_exist: 必须存在
        must_be_file: 必须是文件
        must_be_directory: 必须是目录
        extensions: 允许的文件扩展名
        
    Returns:
        验证后的 Path 对象
        
    Raises:
        ValueError: 如果验证失败
    """
    if path is None:
        raise ValueError(f"{name} 不能为 None")
    
    try:
        path_obj = Path(str(path))
    except Exception:
        raise ValueError(f"{name} 必须是有效的路径")
    
    if must_exist and not path_obj.exists():
        raise ValueError(f"{name} 不存在: {path_obj}")
    
    if must_be_file and not path_obj.is_file():
        raise ValueError(f"{name} 必须是文件: {path_obj}")
    
    if must_be_directory and not path_obj.is_dir():
        raise ValueError(f"{name} 必须是目录: {path_obj}")
    
    if extensions is not None and path_obj.is_file():
        if path_obj.suffix.lower() not in extensions:
            raise ValueError(f"{name} 扩展名必须是 {extensions}: {path_obj}")
    
    return path_obj


def validate_email(email: str) -> str:
    """
    验证电子邮件地址
    
    Args:
        email: 电子邮件地址
        
    Returns:
        验证后的电子邮件地址
        
    Raises:
        ValueError: 如果验证失败
    """
    email = validate_string(email, "电子邮件", min_length=3)
    
    # 简单的电子邮件验证正则表达式
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(email_regex, email):
        raise ValueError("电子邮件地址格式无效")
    
    return email.lower()


def validate_url(url: str) -> str:
    """
    验证 URL
    
    Args:
        url: URL 地址
        
    Returns:
        验证后的 URL
        
    Raises:
        ValueError: 如果验证失败
    """
    url = validate_string(url, "URL", min_length=4)
    
    # 简单的 URL 验证正则表达式
    url_regex = r'^(https?|ftp)://[^\s/$.?#].[^\s]*$'
    
    if not re.match(url_regex, url, re.IGNORECASE):
        raise ValueError("URL 格式无效")
    
    return url


def validate_phone_number(phone: str) -> str:
    """
    验证电话号码
    
    Args:
        phone: 电话号码
        
    Returns:
        验证后的电话号码
        
    Raises:
        ValueError: 如果验证失败
    """
    phone = validate_string(phone, "电话号码", min_length=3)
    
    # 移除所有非数字字符
    digits = re.sub(r'\D', '', phone)
    
    if len(digits) < 7:
        raise ValueError("电话号码太短")
    
    if len(digits) > 15:
        raise ValueError("电话号码太长")
    
    return digits


def validate_phone(phone: str) -> str:
    """验证电话号码（别名函数）"""
    return validate_phone_number(phone)


def validate_directory(
    path: Any,
    name: str = "目录",
    must_exist: bool = False,
    create_if_missing: bool = False
) -> Path:
    """
    验证目录
    
    Args:
        path: 要验证的路径
        name: 参数名称
        must_exist: 必须存在
        create_if_missing: 如果不存在则创建
        
    Returns:
        验证后的 Path 对象
        
    Raises:
        ValueError: 如果验证失败
    """
    if path is None:
        raise ValueError(f"{name} 不能为 None")
    
    try:
        path_obj = Path(str(path))
    except Exception:
        raise ValueError(f"{name} 必须是有效的路径")
    
    if must_exist and not path_obj.exists():
        if create_if_missing:
            try:
                path_obj.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                raise ValueError(f"无法创建目录 {path_obj}: {e}")
        else:
            raise ValueError(f"{name} 不存在: {path_obj}")
    
    if path_obj.exists() and not path_obj.is_dir():
        raise ValueError(f"{name} 必须是目录: {path_obj}")
    
    return path_obj


def validate_json(
    json_str: str,
    name: str = "JSON"
) -> Dict[str, Any]:
    """
    验证 JSON 字符串
    
    Args:
        json_str: JSON 字符串
        name: 参数名称
        
    Returns:
        解析后的 JSON 字典
        
    Raises:
        ValueError: 如果验证失败
    """
    import json
    
    json_str = validate_string(json_str, name)
    
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"{name} 格式无效: {e}")


def validate_config(
    config: Dict[str, Any],
    name: str = "配置",
    required_keys: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    验证配置字典
    
    Args:
        config: 配置字典
        name: 参数名称
        required_keys: 必需的键
        
    Returns:
        验证后的配置字典
        
    Raises:
        ValueError: 如果验证失败
    """
    config = validate_dict(config, name)
    
    if required_keys is not None:
        for key in required_keys:
            if key not in config:
                raise ValueError(f"{name} 缺少必需的键: {key}")
    
    return config


def sanitize_input(
    text: str,
    name: str = "输入",
    max_length: int = 1000,
    allow_html: bool = False,
    allow_script: bool = False
) -> str:
    """
    清理用户输入
    
    Args:
        text: 原始输入
        name: 参数名称
        max_length: 最大长度
        allow_html: 是否允许 HTML
        allow_script: 是否允许脚本
        
    Returns:
        清理后的输入
        
    Raises:
        ValueError: 如果验证失败
    """
    if text is None:
        return ""
    
    text = str(text).strip()
    
    if len(text) > max_length:
        text = text[:max_length]
    
    if not allow_html:
        # 移除 HTML 标签
        text = re.sub(r'<[^>]+>', '', text)
    
    if not allow_script:
        # 移除常见的脚本模式
        script_patterns = [
            r'javascript:', r'vbscript:', r'expression\(', r'eval\(', r'alert\(', r'prompt\(', r'confirm\(',
            r'document\.', r'window\.', r'location\.', r'onload=', r'onerror=', r'onclick=', r'onmouseover='
        ]
        
        for pattern in script_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    return text


def validate_model_name(
    model_name: str,
    name: str = "模型名称"
) -> str:
    """
    验证模型名称
    
    Args:
        model_name: 模型名称
        name: 参数名称
        
    Returns:
        验证后的模型名称
        
    Raises:
        ValueError: 如果验证失败
    """
    model_name = validate_string(model_name, name, min_length=1)
    
    # 检查模型名称格式
    if '/' not in model_name and ':' not in model_name:
        # 可能是简单的模型名称，如 "llama2"
        if not re.match(r'^[a-zA-Z0-9_-]+$', model_name):
            raise ValueError(f"{name} 格式无效，只能包含字母、数字、下划线和连字符")
    
    return model_name


def validate_range(
    value: Union[int, float],
    name: str = "值",
    min_value: Union[int, float] = 0,
    max_value: Union[int, float] = 100
) -> Union[int, float]:
    """
    验证数值范围
    
    Args:
        value: 要验证的值
        name: 参数名称
        min_value: 最小值
        max_value: 最大值
        
    Returns:
        验证后的值
        
    Raises:
        ValueError: 如果验证失败
    """
    if isinstance(value, int):
        return validate_integer(value, name, min_value, max_value)
    elif isinstance(value, float):
        return validate_float(value, name, min_value, max_value)
    else:
        try:
            # 尝试转换为浮点数
            float_value = float(value)
            return validate_float(float_value, name, min_value, max_value)
        except (ValueError, TypeError):
            raise ValueError(f"{name} 必须是数值类型")


def validate_choice(
    value: Any,
    name: str = "选择",
    choices: List[Any] = None,
    case_sensitive: bool = True
) -> Any:
    """
    验证选择值
    
    Args:
        value: 要验证的值
        name: 参数名称
        choices: 可选值列表
        case_sensitive: 是否区分大小写
        
    Returns:
        验证后的值
        
    Raises:
        ValueError: 如果验证失败
    """
    if choices is None:
        choices = []
    
    if not choices:
        raise ValueError("选择列表不能为空")
    
    if not case_sensitive and isinstance(value, str):
        value_lower = value.lower()
        choices_lower = [str(c).lower() for c in choices]
        if value_lower in choices_lower:
            index = choices_lower.index(value_lower)
            return choices[index]
    else:
        if value in choices:
            return value
    
    raise ValueError(f"{name} 必须是以下值之一: {choices}")


def validate_not_none(value: Any, name: str = "值") -> Any:
    """
    验证值不为 None
    
    Args:
        value: 要验证的值
        name: 参数名称
        
    Returns:
        原始值
        
    Raises:
        ValueError: 如果值为 None
    """
    if value is None:
        raise ValueError(f"{name} 不能为 None")
    
    return value


def validate_all(
    validators: List[Callable],
    value: Any,
    name: str = "值"
) -> Any:
    """
    应用多个验证器
    
    Args:
        validators: 验证器列表
        value: 要验证的值
        name: 参数名称
        
    Returns:
        验证后的值
        
    Raises:
        ValueError: 如果任何验证失败
    """
    result = value
    for validator in validators:
        result = validator(result, name)
    return result


# 装饰器函数
def validate_arguments(**validators):
    """
    参数验证装饰器
    
    Args:
        **validators: 参数名到验证函数的映射
        
    Returns:
        装饰器函数
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # 获取函数签名
            import inspect
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            # 验证参数
            for param_name, validator in validators.items():
                if param_name in bound_args.arguments:
                    try:
                        bound_args.arguments[param_name] = validator(
                            bound_args.arguments[param_name],
                            param_name
                        )
                    except ValueError as e:
                        raise ValueError(f"参数 '{param_name}' 验证失败: {e}")
            
            # 调用原始函数
            return func(*bound_args.args, **bound_args.kwargs)
        
        return wrapper
    
    return decorator