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
    model: str = Field(default="Wan-AI/Wan2.2-T2V-A14B", description="模型名称")
    image_size: str = Field(default="1280x720", description="视频尺寸")
    seed: Optional[int] = Field(default=None, description="随机种子")
    negative_prompt: Optional[str] = Field(
        default="色调艳丽,过曝,静态,细节模糊不清,字幕,风格,作品,画作,画面,静止,整体发灰,最差质量,低质量,JPEG压缩残留,丑陋的,残缺的,多余的手指,画得不好的手部,画得不好的脸部,畸形的,毁容的,形态畸形的肢体,手指融合,静止不动的画面,杂乱的背景,三条腿,背景人很多,倒着走",
        description="负面提示词"
    )
    image: Optional[str] = Field(default=None, description="base64编码的图片(用于图生视频)")

class VideoGenerateResponse(BaseModel):
    """文生视频响应"""
    video_url: str
    prompt: str
    task_id: Optional[str] = None