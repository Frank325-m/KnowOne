"""
应用配置设置
将所有硬编码值集中管理，便于配置和部署
"""

import os
from pathlib import Path
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置类"""
    
    # ============ 应用信息 ============
    APP_NAME: str = "RAG Knowledge Base Q&A System"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "基于本地大模型的离线 RAG 知识库问答系统"
    
    # ============ 路径配置 ============
    # 基础路径
    BASE_DIR: Path = Path(__file__).parent.parent
    
    # 数据路径
    DOCS_DIR: Path = Field(default=Path("./docs"), description="文档存储目录")
    VECTOR_DB_DIR: Path = Field(default=Path("./res/chroma_db"), description="向量数据库目录")
    MODEL_CACHE_DIR: Path = Field(default=Path("./model_cache"), description="模型缓存目录")
    LOG_DIR: Path = Field(default=Path("./logs"), description="日志目录")
    
    # ============ 模型配置 ============
    # LLM 配置
    LLM_MODEL_NAME: str = Field(default="qwen:4b", description="Ollama 模型名称")
    LLM_TEMPERATURE: float = Field(default=0.1, ge=0.0, le=2.0, description="模型温度")
    LLM_MAX_TOKENS: int = Field(default=4096, ge=1, description="最大生成token数")
    
    # 嵌入模型配置
    EMBED_MODEL_NAME: str = Field(
        default="mofanke/dmeta-embedding-zh",
        description="Ollama 嵌入模型名称"
    )
    EMBED_MODEL_DEVICE: str = Field(default="cpu", description="嵌入模型运行设备")
    EMBED_NORMALIZE: bool = Field(default=True, description="是否归一化向量")
    
    # ============ 文档处理配置 ============
    # 文档加载配置
    SUPPORTED_EXTENSIONS: list = Field(
        default=[".txt", ".pdf", ".docx"],
        description="支持的文档扩展名"
    )
    
    # 文本分割配置
    CHUNK_SIZE: int = Field(default=800, ge=100, description="文本块大小")
    CHUNK_OVERLAP: int = Field(default=150, ge=0, description="文本块重叠大小")
    SEPARATORS: list = Field(
        default=["\n\n", "\n", "。", "！", "？", "；", "，", " ", ""],
        description="文本分割符"
    )
    
    # ============ 向量检索配置 ============
    # 检索配置
    DEFAULT_TOP_K: int = Field(default=3, ge=1, le=20, description="默认检索数量")
    FETCH_K: int = Field(default=10, ge=1, le=50, description="MMR 初始召回数量")
    LAMBDA_MULT: float = Field(default=0.7, ge=0.0, le=1.0, description="MMR 多样性权重")
    
    # 搜索类型
    SEARCH_TYPE: str = Field(default="mmr", description="搜索类型: similarity/mmr")
    
    # ============ Web 服务配置 ============
    WEB_HOST: str = Field(default="0.0.0.0", description="Web 服务主机")
    WEB_PORT: int = Field(default=7801, ge=1024, le=65535, description="Web 服务端口")
    WEB_DEBUG: bool = Field(default=False, description="是否启用调试模式")
    WEB_SHARE: bool = Field(default=False, description="是否生成公共链接")
    
    # ============ 日志配置 ============
    LOG_LEVEL: str = Field(default="INFO", description="日志级别")
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="日志格式"
    )
    LOG_MAX_BYTES: int = Field(default=10 * 1024 * 1024, description="日志文件最大大小")
    LOG_BACKUP_COUNT: int = Field(default=5, description="日志备份数量")
    
    # ============ 性能配置 ============
    MAX_CONTEXT_LENGTH: int = Field(default=1800, description="最大上下文长度")
    REQUEST_TIMEOUT: int = Field(default=30, description="请求超时时间（秒）")
    CACHE_ENABLED: bool = Field(default=True, description="是否启用缓存")
    
    # ============ 安全配置 ============
    ALLOWED_ORIGINS: list = Field(
        default=["http://localhost:7801", "http://127.0.0.1:7801"],
        description="允许的跨域来源"
    )
    
    # ============ 环境变量配置 ============
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 确保所有目录存在
        self._ensure_directories()
    
    def _ensure_directories(self):
        """确保所有必要的目录存在"""
        directories = [
            self.DOCS_DIR,
            self.VECTOR_DB_DIR,
            self.MODEL_CACHE_DIR,
            self.LOG_DIR,
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    @property
    def docs_dir_abs(self) -> Path:
        """获取文档目录的绝对路径"""
        return self.BASE_DIR / self.DOCS_DIR
    
    @property
    def vector_db_dir_abs(self) -> Path:
        """获取向量数据库目录的绝对路径"""
        return self.BASE_DIR / self.VECTOR_DB_DIR
    
    @property
    def model_cache_dir_abs(self) -> Path:
        """获取模型缓存目录的绝对路径"""
        return self.BASE_DIR / self.MODEL_CACHE_DIR
    
    @property
    def log_dir_abs(self) -> Path:
        """获取日志目录的绝对路径"""
        return self.BASE_DIR / self.LOG_DIR
    
    def get_log_file_path(self, log_type: str = "app") -> Path:
        """获取日志文件路径"""
        return self.log_dir_abs / f"{log_type}.log"


# 创建全局配置实例
settings = Settings()

# 向后兼容的常量（逐步迁移）
# 模型配置
LLM_MODEL_NAME = settings.LLM_MODEL_NAME
EMBED_MODEL_NAME = settings.EMBED_MODEL_NAME
LLM_TEMPERATURE = settings.LLM_TEMPERATURE
MAX_CONTEXT_LEN = settings.MAX_CONTEXT_LENGTH

# 切块配置
CHUNK_SIZE = settings.CHUNK_SIZE
CHUNK_OVERLAP = settings.CHUNK_OVERLAP

# 检索配置
DEFAULT_TOP_K = settings.DEFAULT_TOP_K
FETCH_K = settings.FETCH_K

# 服务配置
WEB_HOST = settings.WEB_HOST
WEB_PORT = settings.WEB_PORT

# 路径配置
DOCS_DIR = str(settings.docs_dir_abs)
VECTOR_DB_PATH = str(settings.vector_db_dir_abs)
LOG_DIR = str(settings.log_dir_abs)