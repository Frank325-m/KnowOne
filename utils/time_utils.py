"""
时间工具模块
提供时间相关的工具函数
"""

import time
import datetime
from typing import Optional, Union
from functools import wraps


class Timer:
    """计时器类"""
    
    def __init__(self, name: str = "计时器"):
        self.name = name
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
        if exc_type is None:
            print(f"{self.name}: {self.elapsed():.3f} 秒")
    
    def start(self):
        """开始计时"""
        self.start_time = time.time()
        self.end_time = None
    
    def stop(self):
        """停止计时"""
        self.end_time = time.time()
    
    def elapsed(self) -> float:
        """获取经过的时间（秒）"""
        if self.start_time is None:
            return 0.0
        if self.end_time is None:
            return time.time() - self.start_time
        return self.end_time - self.start_time
    
    def reset(self):
        """重置计时器"""
        self.start_time = None
        self.end_time = None


def format_duration(seconds: float) -> str:
    """
    格式化持续时间
    
    Args:
        seconds: 秒数
        
    Returns:
        格式化的时间字符串
    """
    if seconds < 0:
        return "0秒"
    
    if seconds < 1:
        return f"{seconds * 1000:.0f}毫秒"
    
    if seconds < 60:
        return f"{seconds:.1f}秒"
    
    minutes = seconds / 60
    if minutes < 60:
        return f"{minutes:.1f}分钟"
    
    hours = minutes / 60
    if hours < 24:
        return f"{hours:.1f}小时"
    
    days = hours / 24
    return f"{days:.1f}天"


def get_current_timestamp() -> int:
    """
    获取当前时间戳
    
    Returns:
        当前时间戳（秒）
    """
    return int(time.time())


def get_current_date() -> str:
    """
    获取当前日期
    
    Returns:
        当前日期字符串 (YYYY-MM-DD)
    """
    return datetime.datetime.now().strftime("%Y-%m-%d")


def get_current_datetime() -> str:
    """
    获取当前日期时间
    
    Returns:
        当前日期时间字符串 (YYYY-MM-DD HH:MM:SS)
    """
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_current_time() -> str:
    """
    获取当前时间
    
    Returns:
        当前时间字符串 (HH:MM:SS)
    """
    return datetime.datetime.now().strftime("%H:%M:%S")


def get_current_datetime_iso() -> str:
    """
    获取当前日期时间（ISO格式）
    
    Returns:
        ISO格式的日期时间字符串
    """
    return datetime.datetime.now().isoformat()


def sleep_with_progress(
    seconds: float,
    interval: float = 0.1,
    progress_callback: Optional[callable] = None
):
    """
    带进度显示地睡眠
    
    Args:
        seconds: 睡眠时间（秒）
        interval: 进度更新间隔（秒）
        progress_callback: 进度回调函数，接收进度百分比
    """
    if seconds <= 0:
        return
    
    total_intervals = int(seconds / interval)
    if total_intervals == 0:
        time.sleep(seconds)
        if progress_callback:
            progress_callback(100)
        return
    
    for i in range(total_intervals + 1):
        progress = min(100, (i / total_intervals) * 100)
        if progress_callback:
            progress_callback(progress)
        if i < total_intervals:
            time.sleep(interval)
    
    # 确保最终进度为100%
    if progress_callback:
        progress_callback(100)


def timeit(func):
    """
    测量函数执行时间的装饰器
    
    Args:
        func: 要测量的函数
        
    Returns:
        装饰后的函数
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed = end_time - start_time
        print(f"函数 {func.__name__} 执行时间: {elapsed:.3f} 秒")
        return result
    return wrapper


def parse_datetime(
    datetime_str: str,
    format_str: Optional[str] = None
) -> Optional[datetime.datetime]:
    """
    解析日期时间字符串
    
    Args:
        datetime_str: 日期时间字符串
        format_str: 格式字符串，如果为 None 则自动尝试常见格式
        
    Returns:
        解析后的 datetime 对象，如果解析失败则返回 None
    """
    if format_str:
        try:
            return datetime.datetime.strptime(datetime_str, format_str)
        except ValueError:
            return None
    
    # 尝试常见格式
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
        "%Y/%m/%d %H:%M:%S",
        "%Y/%m/%d %H:%M",
        "%Y/%m/%d",
        "%d-%m-%Y %H:%M:%S",
        "%d-%m-%Y %H:%M",
        "%d-%m-%Y",
        "%d/%m/%Y %H:%M:%S",
        "%d/%m/%Y %H:%M",
        "%d/%m/%Y",
    ]
    
    for fmt in formats:
        try:
            return datetime.datetime.strptime(datetime_str, fmt)
        except ValueError:
            continue
    
    return None


def format_datetime(
    dt: Union[datetime.datetime, str],
    format_str: str = "%Y-%m-%d %H:%M:%S"
) -> str:
    """
    格式化日期时间
    
    Args:
        dt: datetime 对象或日期时间字符串
        format_str: 格式字符串
        
    Returns:
        格式化后的日期时间字符串
    """
    if isinstance(dt, str):
        dt_obj = parse_datetime(dt)
        if dt_obj is None:
            return dt
        dt = dt_obj
    
    return dt.strftime(format_str)


def is_within_time_range(
    check_time: Union[datetime.datetime, str],
    start_time: Union[datetime.datetime, str],
    end_time: Union[datetime.datetime, str]
) -> bool:
    """
    检查时间是否在指定范围内
    
    Args:
        check_time: 要检查的时间
        start_time: 开始时间
        end_time: 结束时间
        
    Returns:
        是否在时间范围内
    """
    # 转换为 datetime 对象
    if isinstance(check_time, str):
        check_time = parse_datetime(check_time)
        if check_time is None:
            return False
    
    if isinstance(start_time, str):
        start_time = parse_datetime(start_time)
        if start_time is None:
            return False
    
    if isinstance(end_time, str):
        end_time = parse_datetime(end_time)
        if end_time is None:
            return False
    
    return start_time <= check_time <= end_time


def add_time_delta(
    dt: Union[datetime.datetime, str],
    days: int = 0,
    hours: int = 0,
    minutes: int = 0,
    seconds: int = 0
) -> datetime.datetime:
    """
    添加时间间隔
    
    Args:
        dt: 基准时间
        days: 天数
        hours: 小时数
        minutes: 分钟数
        seconds: 秒数
        
    Returns:
        添加间隔后的时间
    """
    if isinstance(dt, str):
        dt = parse_datetime(dt)
        if dt is None:
            raise ValueError(f"无法解析时间字符串: {dt}")
    
    delta = datetime.timedelta(
        days=days,
        hours=hours,
        minutes=minutes,
        seconds=seconds
    )
    
    return dt + delta


def get_time_difference(
    time1: Union[datetime.datetime, str],
    time2: Union[datetime.datetime, str],
    unit: str = "seconds"
) -> float:
    """
    获取两个时间的差值
    
    Args:
        time1: 时间1
        time2: 时间2
        unit: 单位，可选值: seconds, minutes, hours, days
        
    Returns:
        时间差值
    """
    if isinstance(time1, str):
        time1 = parse_datetime(time1)
        if time1 is None:
            raise ValueError(f"无法解析时间字符串: {time1}")
    
    if isinstance(time2, str):
        time2 = parse_datetime(time2)
        if time2 is None:
            raise ValueError(f"无法解析时间字符串: {time2}")
    
    diff = abs((time2 - time1).total_seconds())
    
    if unit == "seconds":
        return diff
    elif unit == "minutes":
        return diff / 60
    elif unit == "hours":
        return diff / 3600
    elif unit == "days":
        return diff / 86400
    else:
        raise ValueError(f"不支持的单位: {unit}")


def is_weekend(dt: Union[datetime.datetime, str]) -> bool:
    """
    判断是否为周末
    
    Args:
        dt: 日期时间
        
    Returns:
        是否为周末
    """
    if isinstance(dt, str):
        dt = parse_datetime(dt)
        if dt is None:
            return False
    
    return dt.weekday() >= 5  # 5=周六, 6=周日


def is_working_hours(
    dt: Union[datetime.datetime, str],
    start_hour: int = 9,
    end_hour: int = 17
) -> bool:
    """
    判断是否为工作时间
    
    Args:
        dt: 日期时间
        start_hour: 工作开始时间（小时）
        end_hour: 工作结束时间（小时）
        
    Returns:
        是否为工作时间
    """
    if isinstance(dt, str):
        dt = parse_datetime(dt)
        if dt is None:
            return False
    
    # 检查是否为周末
    if is_weekend(dt):
        return False
    
    # 检查是否在工作时间范围内
    hour = dt.hour
    return start_hour <= hour < end_hour