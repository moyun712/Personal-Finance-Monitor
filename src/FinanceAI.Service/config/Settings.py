import os
import logging
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    # API配置 - 从环境变量读取
    API_URL_TEXT: str = "https://api.siliconflow.cn/v1/chat/completions"
    API_URL_IMAGE: str = "https://api.siliconflow.cn/v1/images/generations"
    API_URL_VIDEO: str = "https://api.siliconflow.cn/v1/video/submit"
    API_URL_VIDEO_RESULT: str = "https://api.siliconflow.cn/v1/video/status"
    
    # 敏感配置 - 必须从环境变量获取
    SILICONFLOW_API_KEY: str = ""
    
    # 应用配置
    APP_NAME: str = "AcountAI"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    class Config:
        # 获取当前文件所在目录(config目录)
        env_file = Path(__file__).parent / ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._validate_required_settings()
        
    def _validate_required_settings(self):
        """验证必要的配置项"""
        if not self.SILICONFLOW_API_KEY:
            error_msg = (
                "❌ SILICONFLOW_API_KEY is required!\n"
                "请通过以下方式之一设置:\n"
                "1. 创建 .env 文件: SILICONFLOW_API_KEY=your_key\n"
                "2. 设置环境变量: set SILICONFLOW_API_KEY=your_key (Windows)\n"
                "3. 设置环境变量: export SILICONFLOW_API_KEY=your_key (Linux/Mac)"
            )
            logger.error(error_msg)
            raise ValueError(error_msg)
            
    @property
    def masked_api_key(self) -> str:
        """返回掩码后的API密钥用于日志"""
        if len(self.SILICONFLOW_API_KEY) <= 8:
            return "*" * len(self.SILICONFLOW_API_KEY)
        return f"{self.SILICONFLOW_API_KEY[:4]}{'*' * (len(self.SILICONFLOW_API_KEY) - 8)}{self.SILICONFLOW_API_KEY[-4:]}"

# 创建全局配置实例
try:
    settings = Settings()
    logger.info(f"✅ 配置加载成功. API密钥: {settings.masked_api_key}")
except Exception as e:
    logger.error(f"❌ 配置加载失败: {e}")
    raise