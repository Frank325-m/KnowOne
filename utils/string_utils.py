"""
字符串工具模块
提供字符串处理相关的工具函数
"""

import re
import random
import string
from typing import List, Optional, Union, Dict, Any
import unicodedata


def truncate_string(
    text: str,
    max_length: int = 100,
    suffix: str = "..."
) -> str:
    """
    截断字符串
    
    Args:
        text: 原始字符串
        max_length: 最大长度
        suffix: 截断后缀
        
    Returns:
        截断后的字符串
    """
    if not text:
        return ""
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def normalize_text(
    text: str,
    remove_whitespace: bool = True,
    remove_punctuation: bool = False,
    to_lowercase: bool = False,
    remove_accents: bool = False
) -> str:
    """
    标准化文本
    
    Args:
        text: 原始文本
        remove_whitespace: 是否移除空白字符
        remove_punctuation: 是否移除标点符号
        to_lowercase: 是否转换为小写
        remove_accents: 是否移除重音符号
        
    Returns:
        标准化后的文本
    """
    if not text:
        return ""
    
    result = text
    
    # 移除重音符号
    if remove_accents:
        result = ''.join(
            c for c in unicodedata.normalize('NFD', result)
            if unicodedata.category(c) != 'Mn'
        )
    
    # 转换为小写
    if to_lowercase:
        result = result.lower()
    
    # 移除标点符号
    if remove_punctuation:
        result = re.sub(r'[^\w\s-]', '', result)
    
    # 移除空白字符
    if remove_whitespace:
        result = re.sub(r'\s+', ' ', result).strip()
    
    return result


def remove_extra_spaces(text: str) -> str:
    """
    移除多余的空格
    
    Args:
        text: 原始文本
        
    Returns:
        处理后的文本
    """
    if not text:
        return ""
    
    # 移除多余的空格和换行符
    result = re.sub(r'\s+', ' ', text)
    return result.strip()


def extract_keywords(
    text: str,
    min_length: int = 2,
    max_length: int = 20,
    stopwords: Optional[List[str]] = None
) -> List[str]:
    """
    提取关键词
    
    Args:
        text: 原始文本
        min_length: 关键词最小长度
        max_length: 关键词最大长度
        stopwords: 停用词列表
        
    Returns:
        关键词列表
    """
    if not text:
        return []
    
    if stopwords is None:
        stopwords = [
            "的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都", "一", "一个", "上", "也", "很", "到", "说", "要", "去", "你", "会", "着", "没有", "看", "好", "自己", "这", "那", "他", "她", "我们", "你们", "他们", "这个", "那个", "这些", "那些", "什么", "为什么", "怎么", "如何", "哪里", "谁", "什么时候", "多少", "几个", "一些", "很多", "非常", "特别", "比较", "有点", "稍微", "大概", "可能", "也许", "或者", "但是", "然而", "因此", "所以", "因为", "如果", "那么", "虽然", "尽管", "即使", "无论", "不管", "只要", "只有", "除非", "除了", "关于", "对于", "根据", "按照", "通过", "由于", "为了", "关于", "对于", "根据", "按照", "通过", "由于", "为了"
        ]
    
    # 标准化文本
    normalized = normalize_text(
        text,
        remove_whitespace=True,
        remove_punctuation=True,
        to_lowercase=True
    )
    
    # 分割单词
    words = re.findall(r'\b\w+\b', normalized)
    
    # 过滤停用词和长度不符合要求的词
    keywords = []
    for word in words:
        if (min_length <= len(word) <= max_length and 
            word not in stopwords and 
            not word.isdigit()):
            keywords.append(word)
    
    # 去重
    unique_keywords = []
    for word in keywords:
        if word not in unique_keywords:
            unique_keywords.append(word)
    
    return unique_keywords


def calculate_similarity(
    text1: str,
    text2: str,
    method: str = "jaccard"
) -> float:
    """
    计算文本相似度
    
    Args:
        text1: 文本1
        text2: 文本2
        method: 相似度计算方法，可选值: jaccard, cosine, levenshtein
        
    Returns:
        相似度分数 (0.0-1.0)
    """
    if not text1 or not text2:
        return 0.0
    
    if method == "jaccard":
        # Jaccard 相似度
        set1 = set(text1)
        set2 = set(text2)
        
        if not set1 and not set2:
            return 1.0
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0.0
    
    elif method == "cosine":
        # 简单的余弦相似度（基于词频）
        from collections import Counter
        
        words1 = re.findall(r'\w+', text1.lower())
        words2 = re.findall(r'\w+', text2.lower())
        
        vec1 = Counter(words1)
        vec2 = Counter(words2)
        
        # 获取所有词汇
        all_words = set(vec1.keys()).union(set(vec2.keys()))
        
        # 计算点积
        dot_product = sum(vec1.get(word, 0) * vec2.get(word, 0) for word in all_words)
        
        # 计算模长
        norm1 = sum(val ** 2 for val in vec1.values()) ** 0.5
        norm2 = sum(val ** 2 for val in vec2.values()) ** 0.5
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    elif method == "levenshtein":
        # Levenshtein 距离
        m = len(text1)
        n = len(text2)
        
        # 创建距离矩阵
        d = [[0] * (n + 1) for _ in range(m + 1)]
        
        # 初始化第一行和第一列
        for i in range(m + 1):
            d[i][0] = i
        for j in range(n + 1):
            d[0][j] = j
        
        # 填充矩阵
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if text1[i - 1] == text2[j - 1]:
                    cost = 0
                else:
                    cost = 1
                
                d[i][j] = min(
                    d[i - 1][j] + 1,      # 删除
                    d[i][j - 1] + 1,      # 插入
                    d[i - 1][j - 1] + cost  # 替换
                )
        
        # 计算相似度
        max_len = max(m, n)
        if max_len == 0:
            return 1.0
        
        distance = d[m][n]
        return 1.0 - (distance / max_len)
    
    else:
        raise ValueError(f"不支持的相似度计算方法: {method}")


def generate_random_string(
    length: int = 10,
    include_letters: bool = True,
    include_digits: bool = True,
    include_special: bool = False
) -> str:
    """
    生成随机字符串
    
    Args:
        length: 字符串长度
        include_letters: 是否包含字母
        include_digits: 是否包含数字
        include_special: 是否包含特殊字符
        
    Returns:
        随机字符串
    """
    if length <= 0:
        return ""
    
    # 构建字符集
    charset = ""
    
    if include_letters:
        charset += string.ascii_letters
    
    if include_digits:
        charset += string.digits
    
    if include_special:
        charset += string.punctuation
    
    if not charset:
        raise ValueError("字符集不能为空")
    
    # 生成随机字符串
    return ''.join(random.choice(charset) for _ in range(length))


def slugify(
    text: str,
    separator: str = "-",
    max_length: int = 50,
    allow_unicode: bool = False
) -> str:
    """
    将文本转换为 URL 友好的 slug
    
    Args:
        text: 原始文本
        separator: 分隔符
        max_length: 最大长度
        allow_unicode: 是否允许 Unicode 字符
        
    Returns:
        slug 字符串
    """
    if not text:
        return ""
    
    # 转换为小写
    if allow_unicode:
        text = unicodedata.normalize('NFKC', text)
        text = text.lower()
    else:
        text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
        text = text.lower()
    
    # 替换非单词字符
    text = re.sub(r'[^\w\s-]', '', text)
    
    # 替换空白字符
    text = re.sub(r'[-\s]+', separator, text)
    
    # 移除首尾分隔符
    text = text.strip(separator)
    
    # 截断长度
    if max_length and len(text) > max_length:
        text = text[:max_length].rstrip(separator)
    
    return text


def camel_to_snake(text: str) -> str:
    """
    将驼峰命名转换为蛇形命名
    
    Args:
        text: 驼峰命名字符串
        
    Returns:
        蛇形命名字符串
    """
    if not text:
        return ""
    
    # 插入下划线
    result = re.sub(r'(?<!^)(?=[A-Z])', '_', text)
    
    # 转换为小写
    return result.lower()


def snake_to_camel(text: str) -> str:
    """
    将蛇形命名转换为驼峰命名
    
    Args:
        text: 蛇形命名字符串
        
    Returns:
        驼峰命名字符串
    """
    if not text:
        return ""
    
    # 分割单词
    words = text.split('_')
    
    # 将每个单词首字母大写
    camel_words = [word.capitalize() for word in words if word]
    
    # 组合单词
    return ''.join(camel_words)


def count_words(text: str) -> int:
    """
    统计单词数量
    
    Args:
        text: 文本
        
    Returns:
        单词数量
    """
    if not text:
        return 0
    
    # 使用正则表达式匹配单词
    words = re.findall(r'\b\w+\b', text)
    return len(words)


def count_characters(text: str, include_spaces: bool = True) -> int:
    """
    统计字符数量
    
    Args:
        text: 文本
        include_spaces: 是否包含空格
        
    Returns:
        字符数量
    """
    if not text:
        return 0
    
    if include_spaces:
        return len(text)
    else:
        return len(text.replace(' ', '').replace('\t', '').replace('\n', ''))


def count_lines(text: str) -> int:
    """
    统计行数
    
    Args:
        text: 文本
        
    Returns:
        行数
    """
    if not text:
        return 0
    
    return text.count('\n') + 1


def find_all_substrings(
    text: str,
    substring: str,
    case_sensitive: bool = True
) -> List[int]:
    """
    查找所有子串的位置
    
    Args:
        text: 文本
        substring: 子串
        case_sensitive: 是否区分大小写
        
    Returns:
        子串起始位置列表
    """
    if not text or not substring:
        return []
    
    if not case_sensitive:
        text = text.lower()
        substring = substring.lower()
    
    positions = []
    start = 0
    
    while True:
        pos = text.find(substring, start)
        if pos == -1:
            break
        
        positions.append(pos)
        start = pos + 1
    
    return positions


def replace_multiple(
    text: str,
    replacements: Dict[str, str],
    case_sensitive: bool = True
) -> str:
    """
    批量替换字符串
    
    Args:
        text: 原始文本
        replacements: 替换映射字典
        case_sensitive: 是否区分大小写
        
    Returns:
        替换后的文本
    """
    if not text or not replacements:
        return text
    
    result = text
    
    for old, new in replacements.items():
        if case_sensitive:
            result = result.replace(old, new)
        else:
            # 不区分大小写替换
            pattern = re.compile(re.escape(old), re.IGNORECASE)
            result = pattern.sub(new, result)
    
    return result


def is_palindrome(text: str, case_sensitive: bool = False) -> bool:
    """
    判断是否为回文字符串
    
    Args:
        text: 文本
        case_sensitive: 是否区分大小写
        
    Returns:
        是否为回文
    """
    if not text:
        return True
    
    # 清理文本
    cleaned = re.sub(r'[^\w]', '', text)
    
    if not case_sensitive:
        cleaned = cleaned.lower()
    
    return cleaned == cleaned[::-1]


def wrap_text(
    text: str,
    width: int = 80,
    indent: str = ""
) -> str:
    """
    自动换行文本
    
    Args:
        text: 原始文本
        width: 行宽度
        indent: 缩进字符串
        
    Returns:
        换行后的文本
    """
    if not text:
        return ""
    
    lines = text.split('\n')
    wrapped_lines = []
    
    for line in lines:
        if not line:
            wrapped_lines.append("")
            continue
        
        # 分割长行
        while len(line) > width:
            # 查找合适的换行位置
            break_pos = width
            
            # 尝试在空格处换行
            space_pos = line.rfind(' ', 0, width)
            if space_pos > 0:
                break_pos = space_pos
            
            # 添加换行
            wrapped_lines.append(indent + line[:break_pos].rstrip())
            line = line[break_pos:].lstrip()
        
        # 添加剩余部分
        if line:
            wrapped_lines.append(indent + line)
    
    return '\n'.join(wrapped_lines)


def encode_base64(text: str) -> str:
    """
    Base64 编码
    
    Args:
        text: 原始文本
        
    Returns:
        Base64 编码后的字符串
    """
    import base64
    
    if not text:
        return ""
    
    encoded_bytes = base64.b64encode(text.encode('utf-8'))
    return encoded_bytes.decode('utf-8')


def decode_base64(encoded_text: str) -> str:
    """
    Base64 解码
    
    Args:
        encoded_text: Base64 编码的文本
        
    Returns:
        解码后的文本
    """
    import base64
    
    if not encoded_text:
        return ""
    
    try:
        decoded_bytes = base64.b64decode(encoded_text)
        return decoded_bytes.decode('utf-8')
    except Exception:
        return ""


def mask_sensitive_info(
    text: str,
    patterns: Optional[List[str]] = None
) -> str:
    """
    掩码敏感信息
    
    Args:
        text: 原始文本
        patterns: 正则表达式模式列表
        
    Returns:
        掩码后的文本
    """
    if not text:
        return ""
    
    if patterns is None:
        patterns = [
            r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',  # 信用卡号
            r'\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b',            # 社会安全号
            r'\b\d{10,11}\b',                              # 手机号
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # 邮箱
        ]
    
    result = text
    
    for pattern in patterns:
        result = re.sub(
            pattern,
            lambda m: '*' * len(m.group()),
            result
        )
    
    return result