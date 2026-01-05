from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API配置
    API_URL_TEXT: str = "https://api.siliconflow.cn/v1/chat/completions"
    API_URL_IMAGE: str = "https://api.siliconflow.cn/v1/images/generations"
    API_URL_VIDEO: str = "https://api.siliconflow.cn/v1/video/submit"  # 修改这里
    API_URL_VIDEO_RESULT: str = "https://api.siliconflow.cn/v1/video/status"  # 新增轮询端点
    API_KEY: str = ""
    
    # 应用配置
    APP_NAME: str = "AcountAI"
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"

settings = Settings()