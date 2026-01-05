from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import ai_router
from config.Settings import settings

app = FastAPI(
    title=settings.APP_NAME,
    description="AI多功能API服务 - 支持文本对话、文生图、文生视频",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(ai_router.router, prefix="/api/v1")

@app.get("/", tags=["根路径"])
async def root():
    return {
        "message": "欢迎使用AcountAI API",
        "docs": "/docs",
        "endpoints": {
            "文本对话": "/api/v1/ai/chat",
            "文生图": "/api/v1/ai/generate-image",
            "文生视频": "/api/v1/ai/generate-video"
        }
    }

@app.get("/health", tags=["健康检查"])
async def health_check():
    return {"status": "healthy"}
