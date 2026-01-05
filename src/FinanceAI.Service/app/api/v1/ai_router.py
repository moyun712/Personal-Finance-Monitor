from fastapi import APIRouter, HTTPException
from app.schemas.ai_schemas import (
    TextChatRequest, TextChatResponse,
    ImageGenerateRequest, ImageGenerateResponse,
    VideoGenerateRequest, VideoGenerateResponse
)
from app.services.ai_service import AIService
import asyncio

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
    - **image_size**: 视频尺寸(可选,默认1280x720)
    - **seed**: 随机种子(可选)
    - **negative_prompt**: 负面提示词(可选)
    """
    try:
        result = await AIService.generate_video(
            prompt=request.prompt,
            model=request.model,
            image_size=request.image_size,
            seed=request.seed,
            negative_prompt=request.negative_prompt
        )
        return VideoGenerateResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))