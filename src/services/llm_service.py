"""
LLM提示词生成服务
支持GPT-4o、文心一言、通义千问等主流LLM
"""
import requests
import base64
import json
import re
from typing import List, Dict, Optional
from PIL import Image
import io


class LLMService:
    """LLM服务类，用于生成分镜和视频提示词"""
    
    # 广告视频提示词模板（参考蜡烛示例）
    PROMPT_TEMPLATE_AD = """你是专业的广告视频分镜设计师和视频脚本策划师，擅长将产品广告创意转化为详细的分镜图片提示词和视频叙事脚本。

请根据以下产品信息生成广告视频的分镜图片提示词（按分集生成，每集6个分镜，其中第1个为固定的参考图，你需要生成第2-6个分镜的提示词）和对应的视频提示词：

**产品信息**
产品名称：{product_name}
公司名称：{company_name}
核心卖点：{keywords}
视频风格：{style}
视频时长：{duration}秒
总集数：{episode_count}集（每集15秒）
目标受众：{target_audience}

**任务要求**
1. 分镜图片提示词：请生成全部{episode_count}集的分镜提示词。
   - 每集必须包含5个**生成的**分镜提示词（对应镜头2-6）。
   - 镜头1默认为参考图，不需要你生成。
   - **所有生成的分镜提示词必须明确指定画面风格为“黑白线稿”（Black and white line art/sketch style），画面简洁清晰。**
   - 必须严格按照【第1集】、【第2集】...【第{episode_count}集】的格式输出。

2. 视频脚本提示词：请生成全部{episode_count}集的分集视频脚本。
   - 必须严格按照【第1集】、【第2集】...【第{episode_count}集】的格式输出。
   - 每集脚本需包含6个镜头的详细描述（包含第1个参考图镜头）。
   - 格式必须包含：【广告主题】、【时长】、【旁白配置】、以及按时间轴的详细分镜描述。
   - 不要遗漏任何一集。

**输出格式**
**分镜图片提示词**
【第1集】
1. 镜头2：[画面描述]
2. 镜头3：[画面描述]
3. 镜头4：[画面描述]
4. 镜头5：[画面描述]
5. 镜头6：[画面描述]

**对应的视频提示词**
【第1集】
【广告主题】{product_name} + {keywords} + {style} + {target_audience}
【时长】15秒，16:9画幅，4K，{style}色调
【旁白配置】[声音类型]，音量-10dB，语速120字/分钟
0-2.5秒（对应分镜1）：[景别]+[运镜]，[画面描述]；光线：[光线]；音效：[音效]；旁白：[旁白内容]
2.5-5秒（对应分镜2）：[景别]+[运镜]，[画面描述]；光线：[光线]；音效：[音效]；旁白：[旁白内容]
5-7.5秒（对应分镜3）：...
7.5-10秒（对应分镜4）：...
10-12.5秒（对应分镜5）：...
12.5-15秒（对应分镜6）：...

【第2集】
...
"""
    
    # 宣传片提示词模板
    PROMPT_TEMPLATE_PROMO = """你是专业的宣传片分镜设计师和视频脚本策划师。

请根据以下信息生成宣传片的分镜图片提示词（按分集生成，每集6个分镜，其中第1个为固定的参考图，你需要生成第2-6个分镜的提示词）和对应的视频提示词：

**输入信息**
- 宣传主题：{product_name}
- 视频时长：{duration}秒
- 核心内容：{keywords}
- 目标受众：{target_audience}
- 视觉风格：{style}
- 拍摄场景：结合核心内容和视觉风格设计
- 背景音乐：符合视觉风格
- 旁白风格：符合目标受众偏好
- 总集数：{episode_count}集（每集15秒）

**任务要求**
1. 分镜图片提示词：请生成全部{episode_count}集的分镜提示词。
   - 每集必须包含5个**生成的**分镜提示词（对应镜头2-6）。
   - 镜头1默认为参考图，不需要你生成。
   - **所有生成的分镜提示词必须明确指定画面风格为“黑白线稿”（Black and white line art/sketch style），画面简洁清晰。**
   - 必须严格按照【第1集】、【第2集】...【第{episode_count}集】的格式输出。

2. 视频脚本提示词：请生成全部{episode_count}集的分集视频脚本。
   - 必须严格按照【第1集】、【第2集】...【第{episode_count}集】的格式输出。
   - 每集脚本需包含6个镜头的详细描述（包含第1个参考图镜头）。
   - 格式必须包含：【广告主题】、【时长】、【旁白配置】、以及按时间轴的详细分镜描述。
   - 旁白配置必须统一使用：{voice_tone}，音量-10dB，语速{voice_speed}。
   - 不要遗漏任何一集。

**输出格式**
**分镜图片提示词**
【第1集】
1. 镜头2：[画面描述]
2. 镜头3：[画面描述]
3. 镜头4：[画面描述]
4. 镜头5：[画面描述]
5. 镜头6：[画面描述]

**对应的视频提示词**
【第1集】
【广告主题】{product_name} + {keywords} + {style} + {target_audience}
【时长】15秒，16:9画幅，4K，{style}色调
【旁白配置】{voice_tone}，音量-10dB，语速{voice_speed}
0-3秒（对应分镜1）：[景别]+[运镜]，[画面描述]；光线：[光线]；音效：[音效]；旁白：[旁白内容]
3-6秒（对应分镜2）：[景别]+[运镜]，[画面描述]；光线：[光线]；音效：[音效]；旁白：[旁白内容]
6-9秒（对应分镜3）：...
9-12秒（对应分镜4）：...
12-15秒（对应分镜5）：...

【第2集】
...
"""
    
    def __init__(self, api_provider: str = "openai", api_key: str = "", base_url: str = "", model: str = ""):
        """
        初始化LLM服务
        
        Args:
            api_provider: API提供商 (openai, deepseek, wenxin, tongyi, custom)
            api_key: API密钥
            base_url: API基础URL（可选）
            model: 模型名称（可选，留空使用默认）
        """
        self.api_provider = api_provider
        self.api_key = api_key
        self.model = model or self._get_default_model()
        # 确保URL完整
        if base_url:
            self.base_url = self._ensure_complete_url(base_url)
        else:
            self.base_url = self._get_default_url()
    
    def _get_default_model(self) -> str:
        """获取默认模型名称"""
        models = {
            "openai": "gpt-4o",
            "deepseek": "deepseek-chat",
            "wenxin": "ernie-4.0",
            "tongyi": "qwen-max",
            "custom": "gpt-4o"  # 自定义接口默认使用gpt-4o
        }
        return models.get(self.api_provider, "gpt-4o")
        
    def _get_default_url(self) -> str:
        """获取默认API地址"""
        urls = {
            "openai": "https://api.openai.com/v1/chat/completions",
            "deepseek": "https://api.deepseek.com/v1/chat/completions",
            "wenxin": "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions",
            "tongyi": "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
            "custom": "https://api.openai.com/v1/chat/completions"  # 自定义接口示例
        }
        return urls.get(self.api_provider, urls["openai"])
    
    def _ensure_complete_url(self, url: str) -> str:
        """确保URL是完整的，如果只提供了基础URL则补全"""
        if not url:
            return self._get_default_url()
        
        # 对于OpenAI兼容的接口（openai, deepseek, custom），自动补全URL
        if self.api_provider in ["openai", "deepseek", "custom"]:
            if url.endswith("/v1") or url.endswith("/v1/"):
                url = url.rstrip("/") + "/chat/completions"
            elif "/chat/completions" not in url and "/v1" not in url:
                url = url.rstrip("/") + "/v1/chat/completions"
        
        return url
    
    def generate_prompts(self, project_info: Dict, image_paths: List[str] = None) -> Dict[str, any]:
        """
        生成分镜和视频提示词
        
        Args:
            project_info: 项目信息字典
            image_paths: 参考图片路径列表（可选）
            
        Returns:
            包含frame_prompts和video_prompt的字典
        """
        # 选择提示词模板
        if project_info.get("type") == "广告视频":
            template = self.PROMPT_TEMPLATE_AD
        else:
            template = self.PROMPT_TEMPLATE_PROMO
        
        # 计算集数
        duration = project_info.get("duration", 15)
        episode_count = max(1, (duration + 14) // 15)

        # 填充模板
        prompt = template.format(
            product_name=project_info.get("product_name", ""),
            company_name=project_info.get("company_name", ""),
            keywords=project_info.get("keywords", ""),
            style=project_info.get("style", ""),
            duration=duration,
            episode_count=episode_count,
            target_audience=project_info.get("target_audience", "")
        )
        
        # 处理图片（如果有）
        image_data = []
        if image_paths:
            image_data = self._process_images(image_paths)
        
        # 调用LLM API
        try:
            if self.api_provider in ["openai", "deepseek", "custom"]:
                # OpenAI兼容接口统一处理
                result = self._call_openai_compatible(prompt, image_data)
            elif self.api_provider == "wenxin":
                result = self._call_wenxin(prompt, image_data)
            elif self.api_provider == "tongyi":
                result = self._call_tongyi(prompt, image_data)
            else:
                raise ValueError(f"不支持的API提供商: {self.api_provider}")
            
            # 解析结果
            return self._parse_prompts(result)
        
        except Exception as e:
            raise Exception(f"LLM调用失败: {str(e)}")
    
    def _process_images(self, image_paths: List[str]) -> List[str]:
        """处理图片，转换为base64"""
        image_data = []
        for path in image_paths:
            try:
                with Image.open(path) as img:
                    # 调整图片大小以减少token消耗
                    img.thumbnail((512, 512))
                    buffer = io.BytesIO()
                    img.save(buffer, format="JPEG")
                    img_base64 = base64.b64encode(buffer.getvalue()).decode()
                    image_data.append(img_base64)
            except Exception as e:
                print(f"处理图片失败 {path}: {str(e)}")
        return image_data
    
    def _call_openai_compatible(self, prompt: str, image_data: List[str] = None) -> str:
        """调用OpenAI兼容API（支持OpenAI、DeepSeek、自定义接口）"""
        print(f"\n[LLM服务] 调用{self.api_provider}接口")
        print(f"[LLM服务] 模型: {self.model}")
        print(f"[LLM服务] URL: {self.base_url}")
        print(f"[LLM服务] API Key: {self.api_key[:10]}...{self.api_key[-4:] if len(self.api_key) > 14 else ''}")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # 构造消息
        if image_data:
            content = [{"type": "text", "text": prompt}]
            for img_b64 in image_data:
                content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}
                })
            messages = [{"role": "user", "content": content}]
        else:
            messages = [{"role": "user", "content": prompt}]
        
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 4000
        }
        
        print(f"[LLM服务] 发送请求...")
        try:
            response = requests.post(self.base_url, headers=headers, json=data, timeout=120)
            print(f"[LLM服务] 响应状态码: {response.status_code}")
            response.raise_for_status()
            result = response.json()["choices"][0]["message"]["content"]
            print(f"[LLM服务] ✓ 调用成功，返回内容长度: {len(result)} 字符")
            return result
        except requests.exceptions.HTTPError as e:
            print(f"[LLM服务] ✗ HTTP错误: {e.response.status_code}")
            if e.response.status_code == 404:
                raise Exception(f"API地址配置错误: {self.base_url}\n"
                              f"404错误通常表示URL不完整。\n"
                              f"OpenAI兼容API的完整地址应该是: https://your-domain/v1/chat/completions\n"
                              f"当前配置: {self.base_url}")
            elif e.response.status_code == 401:
                raise Exception("API密钥无效或已过期，请检查系统设置中的API密钥配置")
            else:
                error_detail = e.response.text if hasattr(e.response, 'text') else str(e)
                print(f"[LLM服务] 错误详情: {error_detail}")
                raise Exception(f"LLM API调用失败 ({e.response.status_code}): {error_detail}")
        except Exception as e:
            print(f"[LLM服务] ✗ 请求异常: {str(e)}")
            raise
        except requests.exceptions.Timeout:
            raise Exception("LLM API调用超时（120秒），请检查网络连接或稍后重试")
        except requests.exceptions.RequestException as e:
            raise Exception(f"LLM API网络请求失败: {str(e)}")
    
    def _call_wenxin(self, prompt: str, image_data: List[str] = None) -> str:
        """调用文心一言API"""
        headers = {
            "Content-Type": "application/json"
        }
        
        # 文心一言需要access_token
        url = f"{self.base_url}?access_token={self.api_key}"
        
        messages = [{"role": "user", "content": prompt}]
        data = {
            "messages": messages,
            "temperature": 0.7,
            "max_output_tokens": 4000
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=120)
        response.raise_for_status()
        
        return response.json()["result"]
    
    def _call_tongyi(self, prompt: str, image_data: List[str] = None) -> str:
        """调用通义千问API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "input": {
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            },
            "parameters": {
                "temperature": 0.7,
                "max_tokens": 4000
            }
        }
        
        response = requests.post(self.base_url, headers=headers, json=data, timeout=120)
        response.raise_for_status()
        
        return response.json()["output"]["text"]
    
    def _parse_prompts(self, raw_text: str) -> Dict[str, any]:
        """
        解析LLM返回的提示词
        
        Returns:
            {"frame_prompts": [...], "video_prompt": "...", "video_segments": [...]}
        """
        frame_prompts = []
        video_prompt = ""
        video_segments = []
        
        lines = raw_text.split("\n")
        in_frame_section = False
        in_video_section = False
        video_lines = []
        
        current_segment_lines = []
        current_episode = 0
        
        for line in lines:
            line = line.strip()
            
            # 检测分镜提示词部分
            if "分镜图片提示词" in line or "分镜提示词" in line:
                in_frame_section = True
                in_video_section = False
                continue
            
            # 检测视频提示词部分
            if "视频提示词" in line or "对应的视频提示词" in line:
                in_frame_section = False
                in_video_section = True
                continue
            
            # 提取分镜提示词（格式：1. 或 镜头1：）
            if in_frame_section and line:
                if line.startswith(("1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.")):
                    # 移除序号
                    prompt = line.split(".", 1)[1].strip()
                    if prompt.startswith("镜头"):
                        prompt = prompt.split("：", 1)[1].strip() if "：" in prompt else prompt
                    frame_prompts.append(prompt)
                elif line.startswith("镜头"):
                    prompt = line.split("：", 1)[1].strip() if "：" in line else line
                    frame_prompts.append(prompt)
            
            # 收集视频提示词和分集
            if in_video_section and line:
                video_lines.append(line)
                
                # 检测分集标记 【第X集】
                # 支持格式：【第1集】、**【第1集】**、### 【第1集】等
                ep_match = re.search(r"【第(\d+)集】", line)
                if ep_match:
                    # 如果已有正在收集的分集，先保存
                    if current_episode > 0 and current_segment_lines:
                        video_segments.append({
                            "episode": current_episode,
                            "prompt": "\n".join(current_segment_lines).strip(),
                            "duration": 15
                        })
                        current_segment_lines = []
                    
                    # 提取新的集数
                    try:
                        current_episode = int(ep_match.group(1))
                    except:
                        current_episode += 1
                        
                    # 标记行通常不作为内容的一部分，这里不保留，避免保存后重复
                    # current_segment_lines.append(line)
                else:
                    if current_episode > 0:
                        current_segment_lines.append(line)
                    # 如果还没有遇到第一个分集标记，但有内容，可能是引言或第一集的内容（如果标记丢失）
                    elif not current_episode and line:
                         # 假设是第一集
                         current_episode = 1
                         current_segment_lines.append(line)
        
        # 保存最后一个分集
        if current_episode > 0 and current_segment_lines:
            video_segments.append({
                "episode": current_episode,
                "prompt": "\n".join(current_segment_lines).strip(),
                "duration": 15
            })
            
        # 如果没有检测到分集标记，但有视频内容，则作为第一集
        if not video_segments and video_lines:
             video_segments.append({
                "episode": 1,
                "prompt": "\n".join(video_lines).strip(),
                "duration": 15
            })
        
        # 合并视频提示词
        video_prompt = "\n".join(video_lines)
        
        return {
            "frame_prompts": frame_prompts,
            "video_prompt": video_prompt,
            "video_segments": video_segments
        }
