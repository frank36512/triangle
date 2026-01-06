"""
图片生成服务
支持Stable Diffusion、DALL-E、Midjourney等图片生成API
"""
import requests
import os
from typing import List, Optional, Callable
import base64
from io import BytesIO
from PIL import Image
from src.utils.language import lang_manager


import json

class ImageService:
    """图片生成服务类"""
    
    def __init__(self, api_provider: str = "stability", api_key: str = "", base_url: str = "", model: str = ""):
        """
        初始化图片生成服务
        
        Args:
            api_provider: API提供商 (stability, openai, midjourney, flux, custom)
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
            "stability": "stable-diffusion-xl-1024-v1-0",
            "openai": "dall-e-3",
            "midjourney": "midjourney-v6",
            "flux": "flux-pro",
            "custom": "stable-diffusion-xl-1024-v1-0"
        }
        return models.get(self.api_provider, "stable-diffusion-xl-1024-v1-0")
        
    def _get_default_url(self) -> str:
        """获取默认API地址"""
        urls = {
            "stability": "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image",
            "openai": "https://api.openai.com/v1/images/generations",
            "midjourney": "https://api.midjourney.com/v1/imagine",
            "flux": "https://api.bfl.ml/v1/flux-pro",
            "custom": "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
        }
        return urls.get(self.api_provider, urls["stability"])
    
    def _ensure_complete_url(self, url: str) -> str:
        """确保URL是完整的"""
        if not url:
            return self._get_default_url()
        
        # 对于不同提供商，智能补全URL
        if self.api_provider == "openai":
            if "/images/generations" not in url:
                url = url.rstrip("/") + "/v1/images/generations"
        elif self.api_provider == "stability":
            if "/text-to-image" not in url and "/generation/" not in url:
                url = url.rstrip("/") + "/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
        
        return url
    
    def generate_frames(self, 
                       prompts: List[str], 
                       output_dir: str,
                       width: int = 1024,
                       height: int = 1024,
                       style: str = "cinematic",
                       reference_image: str = None,
                       progress_callback: Optional[Callable[[int, str, bool], None]] = None,
                       skip_existing: bool = False,
                       start_index: int = 1) -> List[str]:
        """
        批量生成分镜图片
        
        Args:
            prompts: 分镜提示词列表
            output_dir: 输出目录
            width: 图片宽度
            height: 图片高度
            style: 图片风格
            reference_image: 参考图片路径（可选）
            progress_callback: 进度回调函数 callback(current, status, is_completed)
            skip_existing: 是否跳过已存在的图片
            start_index: 起始分镜编号（默认为1）
            
        Returns:
            生成的图片路径列表
        """
        print(f"\n[图片服务] 开始生成 {len(prompts)} 张分镜图片 (从分镜 {start_index} 开始)")
        print(f"[图片服务] 提供商: {self.api_provider}")
        print(f"[图片服务] 模型: {self.model}")
        print(f"[图片服务] 分辨率: {width}x{height}")
        print(f"[图片服务] 输出目录: {output_dir}")
        print(f"[图片服务] 跳过已存在: {skip_existing}")
        
        os.makedirs(output_dir, exist_ok=True)
        image_paths = []
        
        for i, prompt in enumerate(prompts):
            current_frame_num = start_index + i
            try:
                # 检查文件是否存在
                output_path = os.path.join(output_dir, f"frame_{current_frame_num}.png")
                if skip_existing and os.path.exists(output_path):
                    print(f"[图片服务] 分镜 {current_frame_num} 已存在，跳过生成: {output_path}")
                    image_paths.append(output_path)
                    if progress_callback:
                        progress_callback(current_frame_num, lang_manager.tr("status_frame_exists_skip").format(current_frame_num), True)
                    continue

                if progress_callback:
                    progress_callback(current_frame_num, lang_manager.tr("status_generating_frame").format(current_frame_num), False)
                
                print(f"\n[图片服务] 生成分镜 {current_frame_num}")
                print(f"[图片服务] 提示词: {prompt[:100]}...")
                
                # 如果有参考图片，将其信息添加到提示词中
                enhanced_prompt = prompt
                if reference_image and os.path.exists(reference_image):
                    enhanced_prompt = f"{prompt}. Reference style from provided image."
                
                # 定义缓存路径
                cache_path = os.path.join(output_dir, f"frame_{current_frame_num}.json")
                
                # 调用API生成图片
                if self.api_provider in ["stability", "flux", "custom"]:
                    # Stability AI 兼容接口
                    image_data = self._call_stability_compatible(enhanced_prompt, width, height, style, cache_path)
                elif self.api_provider == "openai":
                    image_data = self._call_openai_dalle(enhanced_prompt, width, height, cache_path)
                elif self.api_provider == "midjourney":
                    image_data = self._call_midjourney(enhanced_prompt, width, height, cache_path)
                else:
                    raise ValueError(f"不支持的API提供商: {self.api_provider}")
                
                # 保存图片
                self._save_image(image_data, output_path)
                
                image_paths.append(output_path)
                print(f"[图片服务] ✓ 分镜 {current_frame_num} 生成成功: {output_path}")
                
                if progress_callback:
                    # 使用 current_frame_num 而不是循环索引 i
                    # 这样 UI 层可以直接使用这个数字
                    progress_callback(current_frame_num, lang_manager.tr("status_frame_generated").format(current_frame_num), True)
                
            except Exception as e:
                error_msg = lang_manager.tr("status_frame_gen_failed").format(current_frame_num, str(e))
                print(f"[图片服务] ✗ {error_msg}")
                if progress_callback:
                    progress_callback(current_frame_num, error_msg, False)
                # 继续生成其他分镜
        
        print(f"\n[图片服务] 批量生成完成，成功 {len(image_paths)}/{len(prompts)} 张")
        return image_paths
        
        return image_paths
    
    def regenerate_frame(self, 
                        prompt: str, 
                        output_path: str,
                        width: int = 1024,
                        height: int = 1024,
                        style: str = "cinematic") -> str:
        """
        重新生成单个分镜
        
        Args:
            prompt: 分镜提示词
            output_path: 输出路径
            width: 图片宽度
            height: 图片高度
            style: 图片风格
            
        Returns:
            生成的图片路径
        """
        try:
            # 定义缓存路径
            cache_path = output_path.replace(".png", ".json")
            
            if self.api_provider in ["stability", "flux", "custom"]:
                image_data = self._call_stability_compatible(prompt, width, height, style, cache_path)
            elif self.api_provider == "openai":
                image_data = self._call_openai_dalle(prompt, width, height, cache_path)
            elif self.api_provider == "midjourney":
                image_data = self._call_midjourney(prompt, width, height, cache_path)
            else:
                raise ValueError(f"不支持的API提供商: {self.api_provider}")
            
            self._save_image(image_data, output_path)
            return output_path
        
        except Exception as e:
            raise Exception(f"重新生成失败: {str(e)}")
    
    def _call_stability_compatible(self, prompt: str, width: int, height: int, style: str, cache_path: str = None) -> bytes:
        """调用Stability AI兼容API（支持Stability、Flux、自定义接口）"""
        
        # 1. 尝试从缓存加载
        if cache_path and os.path.exists(cache_path):
            try:
                print(f"[Debug] 发现缓存文件，尝试恢复: {cache_path}")
                with open(cache_path, "r", encoding="utf-8") as f:
                    json_response = json.load(f)
                
                if "artifacts" in json_response and len(json_response["artifacts"]) > 0:
                    image_b64 = json_response["artifacts"][0]["base64"]
                    return self._safe_base64_decode(image_b64)
            except Exception as e:
                print(f"[Debug] 缓存恢复失败: {str(e)}，将重新调用API")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "text_prompts": [
                {
                    "text": prompt,
                    "weight": 1
                }
            ],
            "cfg_scale": 7,
            "height": height,
            "width": width,
            "samples": 1,
            "steps": 30,
        }
        
        # 添加风格参数（如果支持）
        if style and self.api_provider == "stability":
            data["style_preset"] = style
        
        try:
            response = requests.post(self.base_url, headers=headers, json=data, timeout=180)
            response.raise_for_status()
            
            # 调试信息
            print(f"[Debug] API Response Status: {response.status_code}")
            
            json_response = response.json()
            
            # 2. 保存原始响应到缓存
            if cache_path:
                try:
                    with open(cache_path, "w", encoding="utf-8") as f:
                        json.dump(json_response, f, ensure_ascii=False, indent=2)
                except Exception as e:
                    print(f"[Warning] 保存缓存失败: {str(e)}")
            
            if "artifacts" in json_response and len(json_response["artifacts"]) > 0:
                image_b64 = json_response["artifacts"][0]["base64"]
                
                # 统一处理Base64解码
                return self._safe_base64_decode(image_b64)
            else:
                raise Exception(f"API响应格式错误: 未找到artifacts字段. 响应内容: {json_response}")
                
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise Exception(f"图片生成API地址错误: {self.base_url}\n"
                              f"请检查系统设置中的API地址配置")
            elif e.response.status_code == 401:
                raise Exception("图片生成API密钥无效，请检查系统设置")
            else:
                raise Exception(f"图片生成API调用失败 ({e.response.status_code}): {str(e)}")
        except requests.exceptions.Timeout:
            raise Exception("图片生成API超时（180秒），请稍后重试")
        except Exception as e:
            raise Exception(f"图片生成失败: {str(e)}")
    
    def _call_stability(self, prompt: str, width: int, height: int, style: str) -> bytes:
        """调用Stability AI API（保留向后兼容）"""
        return self._call_stability_compatible(prompt, width, height, style)
    
    def _call_openai_dalle(self, prompt: str, width: int, height: int, cache_path: str = None) -> bytes:
        """调用OpenAI DALL-E API"""
        
        # 1. 尝试从缓存加载
        if cache_path and os.path.exists(cache_path):
            try:
                print(f"[Debug] 发现缓存文件，尝试恢复: {cache_path}")
                with open(cache_path, "r", encoding="utf-8") as f:
                    json_response = json.load(f)
                    
                if "data" in json_response and len(json_response["data"]) > 0:
                    image_b64 = json_response["data"][0]["b64_json"]
                    return self._safe_base64_decode(image_b64)
            except Exception as e:
                print(f"[Debug] 缓存恢复失败: {str(e)}，将重新调用API")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # DALL-E 3支持的尺寸
        size = f"{width}x{height}"
        if size not in ["1024x1024", "1792x1024", "1024x1792"]:
            size = "1024x1024"
        
        data = {
            "model": self.model,
            "prompt": prompt,
            "n": 1,
            "size": size,
            "quality": "standard",
            "response_format": "b64_json"
        }
        
        response = requests.post(self.base_url, headers=headers, json=data, timeout=120)
        response.raise_for_status()
        
        json_response = response.json()
        
        # 2. 保存原始响应到缓存
        if cache_path:
            try:
                with open(cache_path, "w", encoding="utf-8") as f:
                    json.dump(json_response, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"[Warning] 保存缓存失败: {str(e)}")
        
        image_b64 = json_response["data"][0]["b64_json"]
        
        # 统一处理Base64解码
        return self._safe_base64_decode(image_b64)

    def _safe_base64_decode(self, image_b64: str) -> bytes:
        """安全的Base64解码，自动处理各种格式问题"""
        if not image_b64:
            raise ValueError("Base64字符串为空")
            
        # 检查是否为URL（获取地址）
        if image_b64.strip().startswith(("http://", "https://")):
            print(f"[Debug] 检测到图片URL，尝试下载: {image_b64[:50]}...")
            try:
                response = requests.get(image_b64.strip(), timeout=60)
                response.raise_for_status()
                return response.content
            except Exception as e:
                raise Exception(f"从URL下载图片失败: {str(e)}")

        # 去除空白字符
        image_b64 = image_b64.replace(" ", "").replace("\n", "").replace("\r", "")
        
        # 检查base64字符串是否包含前缀
        if "," in image_b64[:100]:
            image_b64 = image_b64.split(",", 1)[1]
            
        # 尝试不同的padding和解码方式
        decoded_data = None
        last_error = None
        
        # 原始清理后的字符串
        candidates = [image_b64]
        
        # 尝试添加不同数量的padding
        for i in range(1, 5):
                candidates.append(image_b64 + "=" * i)
        
        # 尝试截断最后几个字符（处理可能的多余字符）
        for i in range(1, 5):
                candidates.append(image_b64[:-i])
        
        for candidate in candidates:
            try:
                # 确保长度是4的倍数
                padding_needed = len(candidate) % 4
                if padding_needed > 0:
                    candidate += "=" * (4 - padding_needed)
                    
                decoded_data = base64.b64decode(candidate, validate=True)
                break
            except Exception as e:
                last_error = e
                continue
        
        if decoded_data:
            return decoded_data
        else:
            print(f"[Debug] Base64解码失败: {str(last_error)}")
            print(f"[Debug] Base64前50字符: {image_b64[:50]}")
            print(f"[Debug] Base64后50字符: {image_b64[-50:]}")
            print(f"[Debug] Base64长度: {len(image_b64)}")
            raise last_error
    
    def _call_midjourney(self, prompt: str, width: int, height: int, cache_path: str = None) -> bytes:
        """调用Midjourney API（示例，实际需要根据具体API调整）"""
        
        # 1. 尝试从缓存加载（针对MJ，可能缓存的是图片URL）
        if cache_path and os.path.exists(cache_path):
            try:
                print(f"[Debug] 发现缓存文件，尝试恢复: {cache_path}")
                with open(cache_path, "r", encoding="utf-8") as f:
                    json_response = json.load(f)
                    
                if "image_url" in json_response:
                    image_url = json_response["image_url"]
                    img_response = requests.get(image_url, timeout=60)
                    img_response.raise_for_status()
                    return img_response.content
            except Exception as e:
                print(f"[Debug] 缓存恢复失败: {str(e)}，将重新调用API")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "prompt": prompt,
            "aspect_ratio": f"{width}:{height}"
        }
        
        response = requests.post(self.base_url, headers=headers, json=data, timeout=180)
        response.raise_for_status()
        
        json_response = response.json()
        
        # 2. 保存原始响应到缓存
        if cache_path:
            try:
                with open(cache_path, "w", encoding="utf-8") as f:
                    json.dump(json_response, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"[Warning] 保存缓存失败: {str(e)}")

        # 假设返回图片URL
        image_url = json_response["image_url"]
        img_response = requests.get(image_url, timeout=60)
        img_response.raise_for_status()
        
        return img_response.content
    
    def _save_image(self, image_data: bytes, output_path: str):
        """保存图片到文件"""
        with open(output_path, "wb") as f:
            f.write(image_data)
    
    @staticmethod
    def create_grid_preview(image_paths: List[str], output_path: str, frame_texts: List[str] = None, grid_size: int = 3):
        """
        创建预览图 (自适应网格大小)
        
        Args:
            image_paths: 图片路径列表
            output_path: 输出路径
            frame_texts: 分镜文字列表（可选，用于标注）
            grid_size: 建议列数（默认为3）
        """
        if len(image_paths) == 0:
            return
        
        # 加载图片
        images = []
        for path in image_paths:
            try:
                img = Image.open(path)
                images.append(img)
            except Exception as e:
                print(f"加载图片失败 {path}: {str(e)}")
        
        if not images:
            return
        
        # 获取单张图片的尺寸
        img_width, img_height = images[0].size
        
        count = len(images)
        cols = grid_size
        
        # 特殊优化：如果只有4张，使用2x2
        if count == 4:
            cols = 2
        
        # 计算行数
        rows = (count + cols - 1) // cols
        
        # 创建画布
        grid_width = img_width * cols
        grid_height = img_height * rows
        grid_image = Image.new("RGB", (grid_width, grid_height), "white")
        
        # 粘贴图片
        for i, img in enumerate(images):
            row = i // cols
            col = i % cols
            x = col * img_width
            y = row * img_height
            # 调整图片大小以适应网格（如果图片尺寸不一致）
            if img.size != (img_width, img_height):
                img = img.resize((img_width, img_height), Image.Resampling.LANCZOS)
            grid_image.paste(img, (x, y))
        
        # 如果提供了分镜文字，添加文字标注
        if frame_texts and len(frame_texts) > 0:
            from PIL import ImageDraw, ImageFont
            draw = ImageDraw.Draw(grid_image)
            
            # 尝试使用系统字体
            try:
                # Windows
                font = ImageFont.truetype("msyh.ttc", 40)
            except:
                try:
                    # Mac/Linux
                    font = ImageFont.truetype("Arial Unicode.ttf", 40)
                except:
                    font = ImageFont.load_default()
            
            for i, text in enumerate(frame_texts):
                if i >= len(images):
                    break
                    
                row = i // cols
                col = i % cols
                x = col * img_width
                y = row * img_height
                
                # 添加半透明背景
                text_bg_h = 60
                draw.rectangle([x, y + img_height - text_bg_h, x + img_width, y + img_height], fill=(0, 0, 0, 160))
                
                # 添加文字
                draw.text((x + 20, y + img_height - 45), text, font=font, fill="white")
                
        # 保存
        grid_image.save(output_path)

