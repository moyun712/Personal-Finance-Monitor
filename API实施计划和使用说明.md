# FastAPI AI大模型集成方案

将AI大模型功能（文本对话、文生图、文生视频）集成到FastAPI架构中的完整实施计划。

## 项目结构

```
AcountAI/
├── alembic.ini
├── requirements.txt
├── runserver.py
├── alembic/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── ai_router.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── ai_schemas.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── ai_service.py
│   └── utils/
└── config/
    └── Settings.py
```

## 实施步骤

### 1. 更新依赖文件 (requirements.txt)

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pydantic-settings==2.1.0
requests==2.31.0
python-multipart==0.0.6
aiohttp==3.9.1
```

### 2. 配置文件 (config/Settings.py)

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API配置
    API_URL_TEXT: str = "https://api.siliconflow.cn/v1/chat/completions"
    API_URL_IMAGE: str = "https://api.siliconflow.cn/v1/images/generations"
    API_URL_VIDEO: str = "https://api.siliconflow.cn/v1/videos/generations"
    API_KEY: str = "sk-prqxmvzduhivfiprsaoeiqbybhsxvmpepyhywgeryyuthlel"
    
    # 应用配置
    APP_NAME: str = "AcountAI"
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### 3. 数据模型 (app/schemas/ai_schemas.py)

```python
from pydantic import BaseModel, Field
from typing import Optional, List

class TextChatRequest(BaseModel):
    """文本对话请求"""
    message: str = Field(..., description="用户消息")
    model: str = Field(default="Qwen/Qwen2.5-7B-Instruct", description="模型名称")
    max_tokens: int = Field(default=512, description="最大token数")

class TextChatResponse(BaseModel):
    """文本对话响应"""
    message: str
    model: str
    usage: dict

class ImageGenerateRequest(BaseModel):
    """文生图请求"""
    prompt: str = Field(..., description="图片描述")
    model: str = Field(default="Kwai-Kolors/Kolors", description="模型名称")
    image_size: str = Field(default="1024x1024", description="图片尺寸")
    num_inference_steps: int = Field(default=20, description="推理步数")

class ImageGenerateResponse(BaseModel):
    """文生图响应"""
    image_url: str
    prompt: str

class VideoGenerateRequest(BaseModel):
    """文生视频请求"""
    prompt: str = Field(..., description="视频描述")
    model: str = Field(default="minimax/video-01", description="模型名称")
    duration: int = Field(default=5, description="视频时长(秒)")

class VideoGenerateResponse(BaseModel):
    """文生视频响应"""
    video_url: str
    prompt: str
```

### 4. AI服务类 (app/services/ai_service.py)

```python
import aiohttp
import requests
from datetime import datetime
from typing import Dict, Any
from config.Settings import settings

class AIService:
    """AI服务类"""
    
    @staticmethod
    async def chat_with_ai(message: str, model: str = "Qwen/Qwen2.5-7B-Instruct", max_tokens: int = 512) -> Dict[str, Any]:
        """文本对话"""
        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": message}
            ],
            "max_tokens": max_tokens,
            "temperature": 0.7
        }
        
        headers = {
            "Authorization": f"Bearer {settings.API_KEY}",
            "Content-Type": "application/json"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(settings.API_URL_TEXT, json=payload, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    return {
                        "message": result['choices'][0]['message']['content'],
                        "model": model,
                        "usage": result.get('usage', {})
                    }
                else:
                    error_text = await response.text()
                    raise Exception(f"API错误 ({response.status}): {error_text}")
    
    @staticmethod
    async def generate_image(prompt: str, model: str = "Kwai-Kolors/Kolors", 
                            image_size: str = "1024x1024", num_inference_steps: int = 20) -> Dict[str, Any]:
        """文生图"""
        payload = {
            "model": model,
            "prompt": prompt,
            "image_size": image_size,
            "num_inference_steps": num_inference_steps
        }
        
        headers = {
            "Authorization": f"Bearer {settings.API_KEY}",
            "Content-Type": "application/json"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(settings.API_URL_IMAGE, json=payload, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    image_url = result.get('images', [{}])[0].get('url', '')
                    if not image_url:
                        raise Exception("未获取到图片URL")
                    return {
                        "image_url": image_url,
                        "prompt": prompt
                    }
                else:
                    error_text = await response.text()
                    raise Exception(f"API错误 ({response.status}): {error_text}")
    
    @staticmethod
    async def generate_video(prompt: str, model: str = "minimax/video-01", duration: int = 5) -> Dict[str, Any]:
        """文生视频"""
        payload = {
            "model": model,
            "prompt": prompt,
            "duration": duration
        }
        
        headers = {
            "Authorization": f"Bearer {settings.API_KEY}",
            "Content-Type": "application/json"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(settings.API_URL_VIDEO, json=payload, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    video_url = result.get('videos', [{}])[0].get('url', '')
                    if not video_url:
                        raise Exception("未获取到视频URL")
                    return {
                        "video_url": video_url,
                        "prompt": prompt
                    }
                else:
                    error_text = await response.text()
                    raise Exception(f"API错误 ({response.status}): {error_text}")
```

### 5. API路由 (app/api/v1/ai_router.py)

```python
from fastapi import APIRouter, HTTPException
from app.schemas.ai_schemas import (
    TextChatRequest, TextChatResponse,
    ImageGenerateRequest, ImageGenerateResponse,
    VideoGenerateRequest, VideoGenerateResponse
)
from app.services.ai_service import AIService

router = APIRouter(prefix="/ai", tags=["AI功能"])

@router.post("/chat", response_model=TextChatResponse, summary="文本对话")
async def chat_with_ai(request: TextChatRequest):
    """
    与AI进行文本对话
    
    - **message**: 你要发送的消息
    - **model**: 使用的模型(可选)
    - **max_tokens**: 最大返回token数(可选)
    """
    try:
        result = await AIService.chat_with_ai(
            message=request.message,
            model=request.model,
            max_tokens=request.max_tokens
        )
        return TextChatResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-image", response_model=ImageGenerateResponse, summary="文生图")
async def generate_image(request: ImageGenerateRequest):
    """
    根据文本描述生成图片
    
    - **prompt**: 图片描述
    - **model**: 使用的模型(可选)
    - **image_size**: 图片尺寸(可选)
    - **num_inference_steps**: 推理步数(可选)
    """
    try:
        result = await AIService.generate_image(
            prompt=request.prompt,
            model=request.model,
            image_size=request.image_size,
            num_inference_steps=request.num_inference_steps
        )
        return ImageGenerateResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-video", response_model=VideoGenerateResponse, summary="文生视频")
async def generate_video(request: VideoGenerateRequest):
    """
    根据文本描述生成视频
    
    - **prompt**: 视频描述
    - **model**: 使用的模型(可选)
    - **duration**: 视频时长/秒(可选)
    """
    try:
        result = await AIService.generate_video(
            prompt=request.prompt,
            model=request.model,
            duration=request.duration
        )
        return VideoGenerateResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### 6. 路由初始化 (app/api/v1/__init__.py)

```python
from . import ai_router

__all__ = ["ai_router"]
```

### 7. 主应用文件 (app/main.py)

```python
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
```

### 8. 启动文件 (runserver.py)

```python
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
```

## 使用教程

### 安装依赖

```bash
pip install -r requirements.txt
```

### 启动服务

```bash
python runserver.py
```

服务启动后访问：`http://localhost:8000`

### 访问API文档

浏览器打开：`http://localhost:8000/docs`

这是Swagger UI交互式文档，可以直接测试所有接口。

## API接口说明

### 1. 文本对话接口

- **地址**: `POST /api/v1/ai/chat`
- **请求体**:
```json
{
  "message": "你好，请介绍一下自己",
  "model": "Qwen/Qwen2.5-7B-Instruct",
  "max_tokens": 512
}
```
- **响应**:
```json
{
  "message": "你好！我是通义千问...",
  "model": "Qwen/Qwen2.5-7B-Instruct",
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 50,
    "total_tokens": 60
  }
}
```

### 2. 文生图接口

- **地址**: `POST /api/v1/ai/generate-image`
- **请求体**:
```json
{
  "prompt": "一只可爱的猫咪在花园里玩耍",
  "model": "Kwai-Kolors/Kolors",
  "image_size": "1024x1024",
  "num_inference_steps": 20
}
```
- **响应**:
```json
{
  "image_url": "https://...",
  "prompt": "一只可爱的猫咪在花园里玩耍"
}
```

### 3. 文生视频接口

- **地址**: `POST /api/v1/ai/generate-video`
- **请求体**:
```json
{
  "prompt": "海浪拍打沙滩的场景",
  "model": "minimax/video-01",
  "duration": 5
}
```
- **响应**:
```json
{
  "video_url": "https://...",
  "prompt": "海浪拍打沙滩的场景"
}
```

## 三种使用方式

### 方式1: Swagger UI (推荐新手)

1. 访问 `http://localhost:8000/docs`
2. 选择想要测试的接口
3. 点击 "Try it out"
4. 填写参数
5. 点击 "Execute"
6. 查看响应结果

### 方式2: Python代码

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# 文本对话
response = requests.post(f"{BASE_URL}/ai/chat", json={
    "message": "你好，请介绍一下自己"
})
print(response.json())

# 文生图
response = requests.post(f"{BASE_URL}/ai/generate-image", json={
    "prompt": "一只可爱的猫咪在花园里玩耍"
})
print(response.json())

# 文生视频
response = requests.post(f"{BASE_URL}/ai/generate-video", json={
    "prompt": "海浪拍打沙滩的场景"
})
print(response.json())
```

### 方式3: curl命令

```bash
# 文本对话
curl -X POST "http://localhost:8000/api/v1/ai/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "你好"}'

# 文生图
curl -X POST "http://localhost:8000/api/v1/ai/generate-image" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "美丽的日落"}'

# 文生视频
curl -X POST "http://localhost:8000/api/v1/ai/generate-video" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "星空延时摄影"}'
```

## 快速测试流程

1. 打开终端执行 `python runserver.py`
2. 等待看到 "Application startup complete"
3. 浏览器打开 `http://localhost:8000/docs`
4. 点击 `/api/v1/ai/chat` 接口
5. 点击 "Try it out" 按钮
6. 在 message 框输入 "你好"
7. 点击 "Execute" 按钮
8. 查看下方的响应结果

对文生图和文生视频接口重复相同操作即可！

## 注意事项

1. 确保已安装所有依赖包
2. 检查API_KEY是否正确配置
3. 文生图和文生视频可能需要较长时间
4. 返回的图片/视频URL可以直接在浏览器中打开
5. 所有接口都支持CORS跨域请求

## 故障排查

- **端口被占用**: 修改 runserver.py 中的 port 参数
- **依赖安装失败**: 尝试使用 `pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt`
- **API调用失败**: 检查网络连接和API_KEY是否有效
- **导入错误**: 确保所有文件都在正确的目录结构中

## 需要创建的文件清单

1. ✅ 修改 `requirements.txt` - 添加新依赖
2. ✅ 修改 `config/Settings.py` - 添加API配置
3. ✅ 创建 `app/schemas/ai_schemas.py` - 数据模型
4. ✅ 创建 `app/services/ai_service.py` - AI服务类
5. ✅ 创建 `app/api/v1/ai_router.py` - API路由
6. ✅ 修改 `app/api/v1/__init__.py` - 导入路由
7. ✅ 修改 `app/main.py` - 注册路由
8. ✅ 修改 `runserver.py` - 启动配置


### 可用模型

本代金券适用于相关模型的在线体验、API 请求或微调训练，具体如下：
以下模型的在线体验、API 请求产生的费用：
Pro/Qwen/Qwen2.5-7B-Instruct
deepseek-ai/DeepSeek-R1-Distill-Qwen-32B
fnlp/MOSS-TTSD-v0.5
Qwen/Qwen3-VL-235B-A22B-Thinking
Qwen/Qwen3-VL-32B-Thinking
Pro/THUDM/glm-4-9b-chat
black-forest-labs/FLUX.1-schnell
Qwen/Qwen2.5-Coder-32B-Instruct
LoRA/Qwen/Qwen2.5-7B-Instruct
RVC-Boss/GPT-SoVITS
LoRA/Qwen/Qwen2.5-14B-Instruct
Qwen/Qwen3-Reranker-8B
Qwen/Qwen3-30B-A3B-Instruct-2507
Qwen/Qwen3-Omni-30B-A3B-Instruct
Qwen/Qwen2.5-7B-Instruct
Pro/BAAI/bge-m3
deepseek-ai/DeepSeek-R1-Distill-Qwen-7B
THUDM/GLM-4-32B-0414
THUDM/GLM-Z1-32B-0414
Qwen/Qwen3-Reranker-0.6B
moonshotai/Kimi-Dev-72B
TeleAI/TeleSpeechASR
Qwen/Qwen2.5-32B-Instruct
MiniMaxAI/MiniMax-M1-80k
Wan-AI/Wan2.2-I2V-A14B
Qwen/Qwen3-Omni-30B-A3B-Thinking
Qwen/Qwen3-VL-30B-A3B-Instruct
MiniMaxAI/MiniMax-M2
Pro/Qwen/Qwen2-7B-Instruct
Pro/Qwen/Qwen2.5-Coder-7B-Instruct
Qwen/Qwen2.5-72B-Instruct
Qwen/Qwen2.5-Coder-7B-Instruct
Pro/deepseek-ai/DeepSeek-R1-Distill-Qwen-7B
Qwen/Qwen3-Embedding-0.6B
Pro/THUDM/GLM-4.1V-9B-Thinking
Qwen/Qwen3-Next-80B-A3B-Instruct
deepseek-ai/DeepSeek-R1
Qwen/Qwen3-VL-30B-A3B-Thinking
LoRA/Qwen/Qwen2.5-72B-Instruct
ascend-tribe/pangu-pro-moe
stepfun-ai/step3
zai-org/GLM-4.5V
Qwen/Qwen-Image
BAAI/bge-reranker-v2-m3
THUDM/GLM-Z1-9B-0414
Qwen/Qwen3-Embedding-4B
baidu/ERNIE-4.5-VL-424B-A47B-Paddle
Wan-AI/Wan2.2-T2V-A14B
deepseek-ai/DeepSeek-V3
Qwen/Qwen3-VL-8B-Instruct
zai-org/GLM-4.6V
deepseek-ai/DeepSeek-V2.5
Qwen/Qwen3-32B
baidu/ERNIE-4.5-21B-A3B-Paddle
THUDM/GLM-4.1V-9B-Thinking
zai-org/GLM-4.5
zai-org/GLM-4.6
internlm/internlm2_5-7b-chat
LoRA/Qwen/Qwen2.5-32B-Instruct
Qwen/QVQ-72B-Preview
Qwen/Qwen3-30B-A3B-Thinking-2507
Qwen/Qwen3-Coder-30B-A3B-Instruct
Qwen/QwQ-32B
baidu/ERNIE-4.5-300B-A47B
ByteDance-Seed/Seed-OSS-36B-Instruct
Kwaipilot/KAT-Dev
FunAudioLLM/CosyVoice2-0.5B
netease-youdao/bce-reranker-base_v1
Qwen/Qwen2.5-72B-Instruct-128K
Pro/black-forest-labs/FLUX.1-schnell
Qwen/Qwen3-Coder-480B-A35B-Instruct
zai-org/GLM-4.5-Air
Qwen/Qwen-Image-Edit
Qwen/Qwen3-VL-8B-Thinking
Qwen/Qwen2.5-VL-72B-Instruct
SeedLLM/Seed-Rice-7B
deepseek-ai/DeepSeek-OCR
Qwen/Qwen2-VL-72B-Instruct
deepseek-ai/DeepSeek-R1-0528-Qwen3-8B
deepseek-ai/DeepSeek-R1-Distill-Qwen-14B
Tongyi-Zhiwen/QwenLong-L1-32B
inclusionAI/Ling-mini-2.0
Qwen/Qwen3-VL-235B-A22B-Instruct
Qwen/Qwen3-Omni-30B-A3B-Captioner
netease-youdao/bce-embedding-base_v1
Pro/Qwen/Qwen2.5-VL-7B-Instruct
Qwen/Qwen3-235B-A22B
deepseek-ai/DeepSeek-V3.2
deepseek-ai/deepseek-vl2
Qwen/Qwen2.5-VL-32B-Instruct
baidu/ERNIE-4.5-VL-28B-A3B-Paddle
THUDM/glm-4-9b-chat
Qwen/Qwen3-14B
Qwen/Qwen3-Embedding-8B
Qwen/Qwen3-Reranker-4B
tencent/Hunyuan-MT-7B
Qwen/Qwen2.5-14B-Instruct
Pro/BAAI/bge-reranker-v2-m3
Qwen/Qwen3-235B-A22B-Thinking-2507
inclusionAI/Ling-flash-2.0
moonshotai/Kimi-K2-Instruct-0905
deepseek-ai/DeepSeek-V3.1-Terminus
moonshotai/Kimi-K2-Thinking
THUDM/GLM-Z1-Rumination-32B-0414
Qwen/Qwen3-Next-80B-A3B-Thinking
Qwen/Qwen-Image-Edit-2509
IndexTeam/IndexTTS-2
Qwen/Qwen3-VL-32B-Instruct
Qwen/Qwen2-7B-Instruct
black-forest-labs/FLUX.1-dev
BAAI/bge-m3
Kwai-Kolors/Kolors
THUDM/GLM-4-9B-0414
Qwen/Qwen3-30B-A3B
tencent/Hunyuan-A13B-Instruct
Qwen/Qwen3-235B-A22B-Instruct-2507
inclusionAI/Ring-flash-2.0
Qwen/Qwen3-8B
FunAudioLLM/SenseVoiceSmall
以下模型的微调训练所产生的费用：
Qwen/Qwen2.5-7B-Instruct
Qwen/Qwen2.5-32B-Instruct
Qwen/Qwen2.5-72B-Instruct
Qwen/Qwen2.5-14B-Instruct