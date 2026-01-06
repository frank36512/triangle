"""
视频生成服务
支持Sora 2、Pika Labs、Runway等视频生成API
"""
import requests
import os
import time
import base64
from typing import Dict, Optional, Callable


class VideoService:
    """视频生成服务类"""
    
    def __init__(self, api_provider: str = "sora", api_key: str = "", base_url: str = "", model: str = ""):
        """
        初始化视频生成服务
        
        Args:
            api_provider: API提供商 (sora, pika, runway, luma, custom)
            api_key: API密钥
            base_url: API基础URL（可选）
            model: 模型名称（可选，留空使用默认）
        """
        self.api_provider = api_provider
        self.api_key = api_key
        self.model = model or self._get_default_model()
        if base_url:
            self.base_url = self._ensure_complete_url(base_url)
        else:
            self.base_url = self._get_default_url()
    
    def _get_default_model(self) -> str:
        """获取默认模型名称"""
        models = {
            "sora": "sora-2",
            "pika": "pika-1.0",
            "runway": "gen-3",
            "luma": "luma-1.6",
            "custom": "sora-2"
        }
        return models.get(self.api_provider, "sora-2")
        
    def _get_default_url(self) -> str:
        """获取默认API地址"""
        urls = {
            "sora": "https://api.openai.com/v1/video/generations",
            "pika": "https://api.pika.art/v1/generate",
            "runway": "https://api.runwayml.com/v1/generate",
            "luma": "https://api.lumalabs.ai/dream-machine/v1/generations",
            "custom": "https://api.openai.com/v1/video/generations"
        }
        return urls.get(self.api_provider, urls["sora"])
    
    def _ensure_complete_url(self, url: str) -> str:
        """确保URL是完整的"""
        if not url:
            return self._get_default_url()
        
        # 对于不同提供商，智能补全URL
        if self.api_provider == "sora":
            if "/video/generations" not in url:
                url = url.rstrip("/") + "/v1/video/generations"
        elif self.api_provider == "pika":
            if "/generate" not in url:
                url = url.rstrip("/") + "/v1/generate"
        elif self.api_provider == "runway":
            if "/generate" not in url:
                url = url.rstrip("/") + "/v1/generate"
        
        return url

    def _image_to_base64(self, image_path: str) -> str:
        """
        将图片转换为Base64编码字符串
        
        Args:
            image_path: 图片路径
            
        Returns:
            str: Base64编码的图片字符串 (包含 data:image/png;base64, 前缀)
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"图片文件不存在: {image_path}")
            
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            
        # 根据文件扩展名确定MIME类型
        ext = os.path.splitext(image_path)[1].lower()
        if ext in ['.jpg', '.jpeg']:
            mime_type = 'image/jpeg'
        elif ext == '.png':
            mime_type = 'image/png'
        elif ext == '.webp':
            mime_type = 'image/webp'
        else:
            mime_type = 'image/png'  # 默认使用png
            
        return f"data:{mime_type};base64,{encoded_string}"
    
    def generate_video(self,
                      video_prompt: str,
                      frame_images: list,
                      output_path: str,
                      duration: int = 15,
                      resolution: str = "1080p",
                      fps: int = 30,
                      grid_image: str = None,
                      progress_callback: Optional[Callable[[str], None]] = None) -> str:
        """
        生成视频
        
        Args:
            video_prompt: 视频提示词
            frame_images: 分镜图片路径列表
            output_path: 输出视频路径
            duration: 视频时长（秒）
            resolution: 分辨率 (720p, 1080p, 4k)
            fps: 帧率
            grid_image: 九宫格图片路径（可选，用于参考）
            progress_callback: 进度回调函数
            
        Returns:
            生成的视频路径
        """
        print(f"\n[视频服务] 开始生成视频")
        print(f"[视频服务] 提供商: {self.api_provider}")
        print(f"[视频服务] 模型: {self.model}")
        
        # 验证Sora模型名称
        if self.api_provider in ["sora", "custom"] and "sora" in self.model.lower():
            valid_sora_models = ["sora-1.0", "sora-2"]
            if self.model not in valid_sora_models:
                print(f"[视频服务] 警告: 模型名称 '{self.model}' 可能不正确")
                print(f"[视频服务] 支持的Sora模型: {', '.join(valid_sora_models)}")
                print(f"[视频服务] 尝试使用当前模型: {self.model}")
        
        print(f"[视频服务] URL: {self.base_url}")
        print(f"[视频服务] 时长: {duration}秒")
        print(f"[视频服务] 分辨率: {resolution}")
        print(f"[视频服务] 帧率: {fps}fps")
        print(f"[视频服务] 九宫格参考图: {grid_image if grid_image else '无'}")
        print(f"[视频服务] 提示词: {video_prompt[:100]}...")
        
        try:
            if progress_callback:
                progress_callback("开始生成视频...")
            
            # 调用API生成视频
            if self.api_provider == "sora":
                print(f"[视频服务] 使用 Sora 接口")
                video_data = self._call_sora(video_prompt, frame_images, duration, resolution, fps, grid_image, progress_callback)
            elif self.api_provider == "pika":
                print(f"[视频服务] 使用 Pika 接口")
                video_data = self._call_pika(video_prompt, frame_images, duration, resolution, grid_image, progress_callback)
            elif self.api_provider == "runway":
                print(f"[视频服务] 使用 Runway 接口")
                video_data = self._call_runway(video_prompt, frame_images, duration, resolution, grid_image, progress_callback)
            elif self.api_provider == "luma":
                print(f"[视频服务] 使用 Luma 接口")
                video_data = self._call_luma(video_prompt, frame_images, duration, resolution, grid_image, progress_callback)
            elif self.api_provider == "custom":
                print(f"[视频服务] 使用自定义接口（Sora兼容格式）")
                # 自定义接口，默认使用 Sora 兼容格式
                video_data = self._call_sora(video_prompt, frame_images, duration, resolution, fps, grid_image, progress_callback)
            else:
                raise ValueError(f"不支持的API提供商: {self.api_provider}")
            
            # 保存视频
            print(f"[视频服务] 保存视频到: {output_path}")
            dir_name = os.path.dirname(output_path)
            if dir_name:
                os.makedirs(dir_name, exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(video_data)
            
            print(f"[视频服务] ✓ 视频生成成功")
            if progress_callback:
                progress_callback("视频生成完成！")
            
            return output_path
        
        except Exception as e:
            print(f"[视频服务] ✗ 视频生成失败: {str(e)}")
            raise Exception(f"视频生成失败: {str(e)}")
    
    def _call_sora(self, 
                   prompt: str, 
                   frame_images: list,
                   duration: int,
                   resolution: str,
                   fps: int,
                   grid_image: str = None,
                   progress_callback: Optional[Callable] = None) -> bytes:
        """调用Sora 2 API（基于gpt-best.apifox.cn文档）"""
        print(f"\n[视频服务] 调用{self.model}")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # 准备图片URL列表
        image_urls = []
        
        # 优先使用分镜图片列表（如果有）
        has_frame_images = False
        if frame_images and len(frame_images) > 0:
            print(f"[视频服务] 使用分镜图片作为参考: {len(frame_images)}张")
            has_frame_images = True
            for img_path in frame_images:
                if os.path.exists(img_path):
                    try:
                        base64_image = self._image_to_base64(img_path)
                        image_urls.append(base64_image)
                    except Exception as e:
                        print(f"[视频服务] 转换图片失败 {img_path}: {str(e)}")
        
        # 如果没有分镜图片，尝试使用九宫格图片作为参考
        # 注意：如果有分镜图片，则不使用九宫格图片，以免Sora生成九宫格形式的视频
        if not has_frame_images and grid_image and os.path.exists(grid_image):
            print(f"[视频服务] 使用九宫格图片作为参考")
            try:
                base64_image = self._image_to_base64(grid_image)
                image_urls.append(base64_image)
                print(f"[视频服务] 已将九宫格图片转换为Base64")
            except Exception as e:
                print(f"[视频服务] 转换图片失败: {str(e)}")
        elif has_frame_images and grid_image:
            print(f"[视频服务] 已使用分镜图片，跳过九宫格图片以避免生成网格视频")
        
        # 构建请求数据（根据API文档格式）
        data = {
            "prompt": prompt,
            "model": self.model,
            "images": image_urls,  # 图片URL数组
            "aspect_ratio": self._get_aspect_ratio(resolution),
            "hd": resolution in ["1080p", "4k"],
            "duration": str(duration),
            "watermark": False,
            "private": True
        }
        
        print(f"[视频服务] 请求参数:")
        print(f"  - prompt: {prompt[:100]}...")
        print(f"  - model: {self.model}")
        print(f"  - aspect_ratio: {data['aspect_ratio']}")
        print(f"  - hd: {data['hd']}")
        print(f"  - duration: {data['duration']}")
        print(f"  - images: {len(image_urls)} 张")
        
        if progress_callback:
            progress_callback("提交视频生成请求...")
        
        # 提交生成请求
        try:
            print(f"[视频服务] 发送POST请求到: {self.base_url}")
            response = requests.post(self.base_url, headers=headers, json=data, timeout=60)
            print(f"[视频服务] 响应状态码: {response.status_code}")
            response.raise_for_status()
            
            # 获取任务ID
            response_data = response.json()
            print(f"[视频服务] 响应数据: {response_data}")
            task_id = response_data.get("task_id")
            
            if not task_id:
                raise Exception(f"API返回中没有任务ID。返回数据: {response_data}")
            
            print(f"[视频服务] ✓ 任务已提交，task_id: {task_id}")
            if progress_callback:
                progress_callback(f"视频生成中... (任务ID: {task_id})")
            
            # 轮询任务状态
            video_url = self._poll_sora_task(task_id, progress_callback)
            
            if progress_callback:
                progress_callback("下载视频...")
            
            print(f"[视频服务] 下载视频: {video_url}")
            # 下载视频
            video_response = requests.get(video_url, timeout=300)
            video_response.raise_for_status()
            
            print(f"[视频服务] ✓ 视频下载完成，大小: {len(video_response.content)} 字节")
            return video_response.content
            
        except requests.exceptions.RequestException as e:
            error_msg = f"API请求失败: {str(e)}"
            print(f"[视频服务] ✗ {error_msg}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    print(f"[视频服务] 错误详情: {error_detail}")
                    error_msg += f"\n{error_detail}"
                except:
                    print(f"[视频服务] 响应内容: {e.response.text}")
                    error_msg += f"\n{e.response.text}"
            raise Exception(error_msg)
    
    def _poll_sora_task(self, 
                       task_id: str, 
                       progress_callback: Optional[Callable] = None,
                       max_retries: int = 120,
                       retry_interval: int = 10) -> str:
        """
        轮询Sora任务状态（基于gpt-best API）
        
        Returns:
            视频URL
        """
        # 构建查询URL: GET /v2/videos/generations/{task_id}
        # base_url 是 POST 的URL，例如 https://api.example.com/v2/videos/generations
        # 查询URL应该是: https://api.example.com/v2/videos/generations/{task_id}
        status_url = f"{self.base_url}/{task_id}"
        
        print(f"[视频服务] 开始轮询任务状态")
        print(f"[视频服务] 任务ID: {task_id}")
        print(f"[视频服务] 查询URL: {status_url}")
        print(f"[视频服务] 最大重试次数: {max_retries}, 间隔: {retry_interval}秒")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        
        for i in range(max_retries):
            try:
                time.sleep(retry_interval)
                
                print(f"[视频服务] 第{i+1}次查询任务状态...")
                response = requests.get(status_url, headers=headers, timeout=30)
                print(f"[视频服务] 响应状态码: {response.status_code}")
                response.raise_for_status()
                
                result = response.json()
                status = result.get("status")
                progress = result.get("progress", "0%")
                
                print(f"[视频服务] 状态: {status}, 进度: {progress}")
                
                if status == "SUCCESS":
                    video_url = result.get("data", {}).get("output")
                    if not video_url:
                        raise Exception(f"任务完成但未返回视频URL。返回数据: {result}")
                    print(f"[视频服务] ✓ 视频生成成功")
                    print(f"[视频服务] 视频URL: {video_url}")
                    return video_url
                    
                elif status == "FAILURE":
                    fail_reason = result.get("fail_reason", "未知错误")
                    print(f"[视频服务] ✗ 视频生成失败: {fail_reason}")
                    raise Exception(f"视频生成失败: {fail_reason}")
                    
                elif status in ["NOT_START", "IN_PROGRESS"]:
                    # 仍在处理中
                    if progress_callback:
                        progress_callback(f"视频生成中... 进度: {progress} ({i+1}/{max_retries})")
                else:
                    print(f"[视频服务] 未知状态: {status}")
                    if progress_callback:
                        progress_callback(f"处理中... 状态: {status}")
            
            except requests.exceptions.RequestException as e:
                print(f"[视频服务] ✗ 查询任务状态失败: {str(e)}")
                if hasattr(e, 'response') and e.response is not None:
                    print(f"[视频服务] 响应内容: {e.response.text[:500]}")
                if i < max_retries - 1:
                    print(f"[视频服务] 将在 {retry_interval} 秒后重试...")
                    continue
                raise
        
        # 超时
        raise Exception(f"视频生成超时，已等待 {max_retries * retry_interval} 秒")
    
    def _call_pika(self, 
                   prompt: str,
                   frame_images: list,
                   duration: int,
                   resolution: str,
                   grid_image: str = None,
                   progress_callback: Optional[Callable] = None) -> bytes:
        """调用Pika Labs API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        width, height = self._parse_resolution(resolution)
        
        # 优先使用九宫格图片作为参考
        reference_image_url = None
        if grid_image and os.path.exists(grid_image):
            # 这里需要实际上传图片
            pass
        
        data = {
            "prompt": prompt,
            "duration": duration,
            "aspect_ratio": f"{width}:{height}",
            "motion": 3  # 运动强度
        }
        
        if progress_callback:
            progress_callback("提交视频生成请求...")
        
        response = requests.post(self.base_url, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        
        task_id = response.json().get("id")
        
        if progress_callback:
            progress_callback(f"视频生成中... (任务ID: {task_id})")
        
        video_url = self._poll_task_status(task_id, progress_callback)
        
        if progress_callback:
            progress_callback("下载视频...")
        
        video_response = requests.get(video_url, timeout=300)
        video_response.raise_for_status()
        
        return video_response.content
    
    def _call_runway(self, 
                    prompt: str,
                    frame_images: list,
                    duration: int,
                    resolution: str,
                    grid_image: str = None,
                    progress_callback: Optional[Callable] = None) -> bytes:
        """调用Runway API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        width, height = self._parse_resolution(resolution)
        
        # 优先使用九宫格图片作为参考
        reference_image = None
        if grid_image and os.path.exists(grid_image):
            # 这里需要实际上传图片
            pass
        
        data = {
            "prompt": prompt,
            "duration": duration,
            "width": width,
            "height": height
        }
        
        if progress_callback:
            progress_callback("提交视频生成请求...")
        
        response = requests.post(self.base_url, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        
        task_id = response.json().get("id")
        
        if progress_callback:
            progress_callback(f"视频生成中... (任务ID: {task_id})")
        
        video_url = self._poll_task_status(task_id, progress_callback)
        
        if progress_callback:
            progress_callback("下载视频...")
        
        video_response = requests.get(video_url, timeout=300)
        video_response.raise_for_status()
        
        return video_response.content
    
    def _call_luma(self, 
                   prompt: str, 
                   frame_images: list, 
                   duration: int,
                   resolution: str,
                   grid_image: Optional[str] = None,
                   progress_callback: Optional[Callable] = None) -> bytes:
        """调用Luma Dream Machine API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        width, height = self._parse_resolution(resolution)
        
        # 优先使用九宫格图片作为参考
        reference_image = None
        if grid_image and os.path.exists(grid_image):
            # 这里需要实际上传图片
            pass
        
        data = {
            "prompt": prompt,
            "aspect_ratio": f"{width}:{height}",
            "loop": False,
            "keyframes": {
                "frame0": {
                    "type": "generation",
                    "prompt": prompt
                }
            }
        }
        
        if progress_callback:
            progress_callback("提交视频生成请求...")
        
        response = requests.post(self.base_url, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        
        task_id = response.json().get("id")
        
        if progress_callback:
            progress_callback(f"视频生成中... (任务ID: {task_id})")
        
        video_url = self._poll_task_status(task_id, progress_callback)
        
        if progress_callback:
            progress_callback("下载视频...")
        
        video_response = requests.get(video_url, timeout=300)
        video_response.raise_for_status()
        
        return video_response.content
    
    def _poll_task_status(self, 
                         task_id: str, 
                         progress_callback: Optional[Callable] = None,
                         max_retries: int = 60,
                         retry_interval: int = 10) -> str:
        """
        轮询任务状态
        
        Returns:
            视频URL
        """
        status_url = f"{self.base_url}/{task_id}"
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        
        for i in range(max_retries):
            try:
                response = requests.get(status_url, headers=headers, timeout=30)
                response.raise_for_status()
                
                result = response.json()
                status = result.get("status")
                
                if status == "completed":
                    return result.get("video_url")
                elif status == "failed":
                    raise Exception(f"视频生成失败: {result.get('error')}")
                else:
                    # 仍在处理中
                    if progress_callback:
                        progress_callback(f"视频生成中... ({i+1}/{max_retries})")
                    time.sleep(retry_interval)
            
            except Exception as e:
                if i == max_retries - 1:
                    raise
                time.sleep(retry_interval)
        
        raise Exception("视频生成超时")
    
    def _parse_resolution(self, resolution: str) -> tuple:
        """解析分辨率字符串"""
        resolutions = {
            "720p": (1280, 720),
            "1080p": (1920, 1080),
            "4k": (3840, 2160)
        }
        return resolutions.get(resolution.lower(), (1920, 1080))
    
    def _get_aspect_ratio(self, resolution: str) -> str:
        """根据分辨率获取宽高比"""
        ratios = {
            "720p": "16:9",
            "1080p": "16:9",
            "4k": "16:9"
        }
        return ratios.get(resolution.lower(), "16:9")
    
    @staticmethod
    def _create_subtitle_clip(text, fontsize=40, font='SimHei', color='white', stroke_color='black', stroke_width=2, size=None):
        """
        使用 PIL 创建字幕图片 Clip (无需 ImageMagick)
        """
        from moviepy.editor import ImageClip
        from PIL import Image, ImageDraw, ImageFont
        import numpy as np
        
        # 创建透明背景图像
        # 如果未指定大小，则根据文本自动计算，但通常字幕是覆盖在视频底部的固定区域
        # 这里我们创建一个足够大的画布，然后裁剪
        
        # 预估文字大小
        # 注意：Windows下 SimHei 可能需要指定完整路径，或者系统能找到
        # 尝试常见字体路径
        font_path = "C:/Windows/Fonts/simhei.ttf"
        if not os.path.exists(font_path):
             font_path = "C:/Windows/Fonts/msyh.ttc" # 微软雅黑
        
        try:
            pil_font = ImageFont.truetype(font_path, fontsize)
        except:
            pil_font = ImageFont.load_default()
            
        # 计算文本尺寸
        left, top, right, bottom = pil_font.getbbox(text)
        text_width = right - left
        text_height = bottom - top
        
        # 增加一点padding
        w = text_width + stroke_width * 4 + 20
        h = text_height + stroke_width * 4 + 20
        
        img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # 绘制描边
        x = w // 2 - text_width // 2
        y = h // 2 - text_height // 2
        
        if stroke_width > 0:
            for adj_x in range(-stroke_width, stroke_width + 1):
                for adj_y in range(-stroke_width, stroke_width + 1):
                    draw.text((x + adj_x, y + adj_y), text, font=pil_font, fill=stroke_color)
        
        # 绘制文字
        draw.text((x, y), text, font=pil_font, fill=color)
        
        # 转换为 numpy 数组
        img_np = np.array(img)
        
        # 创建 ImageClip
        clip = ImageClip(img_np)
        return clip

    @staticmethod
    def merge_videos(video_paths: list, output_path: str, subtitle_map: dict = None, progress_callback: Optional[Callable[[str], None]] = None) -> str:
        """
        合并多个视频
        
        Args:
            video_paths: 视频路径列表
            output_path: 输出视频路径
            subtitle_map: 字幕映射 {video_path: [{"start": 0, "end": 3, "text": "..."}]}
            progress_callback: 进度回调
            
        Returns:
            合并后的视频路径
        """
        try:
            from moviepy.editor import VideoFileClip, concatenate_videoclips, CompositeVideoClip
            
            if progress_callback:
                progress_callback("正在加载视频片段...")
                
            clips = []
            for path in video_paths:
                if os.path.exists(path):
                    print(f"[视频服务] 加载视频片段: {path}")
                    video_clip = VideoFileClip(path)
                    
                    # 检查是否有字幕需要添加
                    if subtitle_map and path in subtitle_map:
                        subtitles = subtitle_map[path]
                        subtitle_clips = [video_clip] # 基础视频
                        
                        print(f"[视频服务] 为视频 {os.path.basename(path)} 添加 {len(subtitles)} 条字幕")
                        
                        for sub in subtitles:
                            start_time = sub["start"]
                            end_time = sub["end"]
                            text = sub["text"]
                            
                            # 限制字幕时间不超过视频时长
                            if start_time >= video_clip.duration:
                                continue
                            if end_time > video_clip.duration:
                                end_time = video_clip.duration
                            
                            duration = end_time - start_time
                            if duration <= 0:
                                continue
                                
                            # 创建字幕 Clip
                            try:
                                txt_clip = VideoService._create_subtitle_clip(
                                    text, 
                                    fontsize=int(video_clip.h * 0.05), # 根据视频高度动态调整字号
                                    color='white', 
                                    stroke_color='black', 
                                    stroke_width=2
                                )
                                
                                # 设置位置（底部居中）
                                txt_clip = txt_clip.set_position(('center', 0.85), relative=True).set_start(start_time).set_duration(duration)
                                subtitle_clips.append(txt_clip)
                            except Exception as e:
                                print(f"[视频服务] 创建字幕失败: {e}")
                        
                        # 合成带字幕的片段
                        if len(subtitle_clips) > 1:
                            video_clip = CompositeVideoClip(subtitle_clips)
                            
                    clips.append(video_clip)
            
            if not clips:
                raise Exception("没有有效的视频片段可合并")
                
            if progress_callback:
                progress_callback("正在合并视频...")
                
            final_clip = concatenate_videoclips(clips)
            
            if progress_callback:
                progress_callback("正在导出合并后的视频...")
                
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # 使用 moviepy 写入视频
            # logger=None 禁止 moviepy 输出到控制台，避免干扰
            final_clip.write_videofile(
                output_path, 
                codec="libx264", 
                audio_codec="aac",
                logger=None 
            )
            
            # 释放资源
            # 注意：CompositeVideoClip 需要关闭其 subclips，但这里我们只保留了最后的 final_clip
            # 实际上 VideoFileClip 需要显式关闭
            # 遍历 clips 列表可能不够，因为 CompositeVideoClip 包装了原始 clip
            # 递归关闭
            def close_clip(clip):
                try:
                    clip.close()
                    if hasattr(clip, 'clips'):
                        for c in clip.clips:
                            close_clip(c)
                except:
                    pass

            close_clip(final_clip)
            
            if progress_callback:
                progress_callback("视频合并完成！")
                
            return output_path
            
        except Exception as e:
            print(f"合并视频失败: {str(e)}")
            raise Exception(f"合并视频失败: {str(e)}")

    @staticmethod
    def get_video_info(video_path: str) -> Dict:
        """
        获取视频信息
        
        Returns:
            包含duration, width, height, fps等信息的字典
        """
        try:
            import cv2
            cap = cv2.VideoCapture(video_path)
            
            info = {
                "duration": int(cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS)),
                "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                "fps": int(cap.get(cv2.CAP_PROP_FPS)),
                "frame_count": int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            }
            
            cap.release()
            return info
        
        except Exception as e:
            print(f"获取视频信息失败: {str(e)}")
            return {}
