import aiohttp
import requests
from datetime import datetime
from typing import Dict, Any
from config.Settings import settings
import logging
import traceback
import asyncio
import random

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AIService:
    """AI服务类"""
    
    @staticmethod
    async def chat_with_ai(message: str, model: str = "Qwen/Qwen2.5-7B-Instruct", max_tokens: int = 512) -> Dict[str, Any]:
        """文本对话"""
        logger.info(f"=== 开始文本对话 ===")
        logger.info(f"消息: {message}")
        logger.info(f"模型: {model}")
        
        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": message}
            ],
            "max_tokens": max_tokens,
            "temperature": 0.7
        }
        
        headers = {
            "Authorization": f"Bearer {settings.SILICONFLOW_API_KEY}",
            "Content-Type": "application/json"
        }
        
        logger.debug(f"请求URL: {settings.API_URL_TEXT}")
        logger.debug(f"请求载荷: {payload}")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(settings.API_URL_TEXT, json=payload, headers=headers) as response:
                    logger.info(f"响应状态码: {response.status}")
                    response_text = await response.text()
                    logger.debug(f"响应内容: {response_text}")
                    
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "message": result['choices'][0]['message']['content'],
                            "model": model,
                            "usage": result.get('usage', {})
                        }
                    else:
                        logger.error(f"API错误: {response.status} - {response_text}")
                        raise Exception(f"API错误 ({response.status}): {response_text}")
        except Exception as e:
            logger.error(f"发生异常: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    
    @staticmethod
    async def generate_image(prompt: str, model: str = "Kwai-Kolors/Kolors", 
                            image_size: str = "1024x1024", num_inference_steps: int = 20) -> Dict[str, Any]:
        """文生图"""
        logger.info(f"=== 开始文生图 ===")
        logger.info(f"提示词: {prompt}")
        logger.info(f"模型: {model}")
        
        payload = {
            "model": model,
            "prompt": prompt,
            "image_size": image_size,
            "num_inference_steps": num_inference_steps
        }
        
        headers = {
            "Authorization": f"Bearer {settings.SILICONFLOW_API_KEY}",
            "Content-Type": "application/json"
        }
        
        logger.debug(f"请求URL: {settings.API_URL_IMAGE}")
        logger.debug(f"请求载荷: {payload}")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(settings.API_URL_IMAGE, json=payload, headers=headers) as response:
                    logger.info(f"响应状态码: {response.status}")
                    response_text = await response.text()
                    logger.debug(f"响应内容: {response_text}")
                    
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
                        logger.error(f"API错误: {response.status} - {response_text}")
                        raise Exception(f"API错误 ({response.status}): {response_text}")
        except Exception as e:
            logger.error(f"发生异常: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    
    @staticmethod
    async def generate_video(
        prompt: str, 
        model: str = "Wan-AI/Wan2.2-T2V-A14B", 
        image_size: str = "1280x720",
        seed: int = None,
        negative_prompt: str = "色调艳丽,过曝,静态,细节模糊不清,字幕,风格,作品,画作,画面,静止,整体发灰,最差质量,低质量,JPEG压缩残留,丑陋的,残缺的,多余的手指,画得不好的手部,画得不好的脸部,畸形的,毁容的,形态畸形的肢体,手指融合,静止不动的画面,杂乱的背景,三条腿,背景人很多,倒着走",
        image: str = None  # 可选的base64图片,用于图生视频
    ) -> Dict[str, Any]:
        """文生视频 - 异步任务模式"""
        logger.info(f"=== 开始文生视频 ===")
        logger.info(f"提示词: {prompt[:100]}...")
        logger.info(f"模型: {model}")
        
        # 如果没有提供seed,生成一个随机seed
        if seed is None:
            seed = random.randint(1000000000, 9999999999)
        
        # 构建请求体
        payload = {
            "model": model,
            "prompt": prompt,
            "image_size": image_size,
            "seed": seed,
            "negative_prompt": negative_prompt
        }
        
        # 如果提供了图片,添加到请求中
        if image:
            payload["image"] = image
        
        headers = {
            "Authorization": f"Bearer {settings.SILICONFLOW_API_KEY}",
            "Content-Type": "application/json"
        }
        
        logger.debug(f"提交任务URL: {settings.API_URL_VIDEO}")
        logger.debug(f"请求载荷: {payload}")
        
        try:
            async with aiohttp.ClientSession() as session:
                # 步骤1: 提交视频生成任务
                async with session.post(settings.API_URL_VIDEO, json=payload, headers=headers) as response:
                    logger.info(f"提交任务响应状态码: {response.status}")
                    response_text = await response.text()
                    logger.debug(f"提交任务响应内容: {response_text}")
                    
                    if response.status != 200:
                        logger.error(f"提交任务失败: {response.status} - {response_text}")
                        raise Exception(f"提交视频生成任务失败 ({response.status}): {response_text}")
                    
                    result = await response.json()
                    
                    # 提取任务ID (根据实际API响应调整)
                    task_id = result.get('id') or result.get('requestId') or result.get('requestId')
                    
                    if not task_id:
                        logger.error(f"未获取到task_id,响应: {result}")
                        raise Exception(f"未获取到任务ID,响应: {result}")
                    
                    logger.info(f"✅ 任务提交成功,task_id: {task_id}")
                
                # 步骤2: 轮询任务结果
                max_retries = 1200  # 最多轮询1200次
                retry_interval = 20  # 每20秒轮询一次
                
                for attempt in range(max_retries):
                    await asyncio.sleep(retry_interval)
                    
                    logger.info(f"第{attempt + 1}次查询任务状态")
                    
                    # 使用POST请求查询状态,任务ID在请求体中
                    status_payload = {"requestId": task_id}
                    logger.debug(f"查询URL: {settings.API_URL_VIDEO_RESULT}")
                    logger.debug(f"查询载荷: {status_payload}")
                    
                    async with session.post(settings.API_URL_VIDEO_RESULT, json=status_payload, headers=headers) as result_response:
                        response_text = await result_response.text()
                        logger.debug(f"查询响应状态码: {result_response.status}")
                        logger.debug(f"查询响应内容: {response_text}")
                        
                        if result_response.status != 200:
                            logger.warning(f"查询任务状态失败: {result_response.status}")
                            continue
                        
                        task_result = await result_response.json()
                        logger.debug(f"解析后的任务状态: {task_result}")
                        
                        # 提取状态 (根据实际API响应调整)
                        status = (
                            task_result.get('status') or 
                            task_result.get('state') or 
                            task_result.get('taskStatus')
                        )
                        
                        logger.info(f"任务状态: {status}")
                        
                        # 完成状态
                        if status in ['completed', 'success', 'Success', 'COMPLETED', 'finished', 'done']:
                            # 提取视频URL (根据实际API响应调整)
                            video_url = (
                                task_result.get('video_url') or 
                                task_result.get('videoUrl') or
                                task_result.get('url') or
                                task_result.get('result', {}).get('url') or
                                task_result.get('data', {}).get('video_url')
                            )
                            
                            if not video_url and 'videos' in task_result:
                                videos = task_result.get('videos', [])
                                if videos and len(videos) > 0:
                                    video_url = videos[0].get('url')
                            
                            if video_url:
                                logger.info(f"✅ 视频生成成功: {video_url}")
                                return {
                                    "video_url": video_url,
                                    "prompt": prompt,
                                    "task_id": task_id
                                }
                            else:
                                logger.error(f"任务完成但未找到视频URL,完整响应: {task_result}")
                                raise Exception(f"任务完成但未找到视频URL")
                        
                        # 失败状态
                        elif status in ['failed', 'error', 'Failed', 'ERROR', 'FAILED']:
                            error_msg = (
                                task_result.get('error') or 
                                task_result.get('message') or 
                                task_result.get('errorMessage') or
                                '未知错误'
                            )
                            logger.error(f"❌ 视频生成失败: {error_msg}")
                            raise Exception(f"视频生成失败: {error_msg}")
                        
                        # 处理中状态
                        elif status in ['processing', 'InQueue', 'Processing', 'PROCESSING', 'running', 'queued']:
                            progress = task_result.get('progress', 0)
                            logger.info(f"⏳ 任务处理中...({attempt + 1}/{max_retries}) 进度: {progress}%")
                            continue
                        
                        else:
                            logger.warning(f"⚠️ 未知任务状态: {status}")
                            continue
                
                # 超时
                logger.error(f"⏱️ 视频生成超时(已等待{max_retries * retry_interval}秒),任务ID: {task_id}")
                raise Exception(f"视频生成超时,任务ID: {task_id}。请稍后使用任务ID查询结果。")
                
        except Exception as e:
            logger.error(f"发生异常: {str(e)}")
            logger.error(traceback.format_exc())
            raise