"""
项目数据模型
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Project:
    """项目数据模型"""
    id: Optional[int] = None
    name: str = ""
    type: str = "广告视频"  # 广告视频/宣传片视频
    product_name: str = ""
    company_name: str = ""
    target_audience: str = ""
    duration: int = 15  # 视频时长（秒）
    style: str = "温暖治愈"  # 视频风格
    keywords: str = ""  # 核心卖点关键词
    voice_tone: str = "沉稳男声"  # 旁白音色
    voice_speed: str = "适中(120字/分钟)"  # 语速
    reference_image: str = ""  # 参考图片文件名
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None
    
    # 生成的提示词
    frame_prompts: list[str] = None  # 9个分镜提示词
    video_prompt: str = ""  # 视频提示词
    video_segments: list[dict] = None  # 视频分集列表 [{"episode": 1, "prompt": "...", "duration": 15}, ...]
    
    def __post_init__(self):
        if self.frame_prompts is None:
            self.frame_prompts = []
        if self.video_segments is None:
            self.video_segments = []
        if self.create_time is None:
            self.create_time = datetime.now()
        if self.update_time is None:
            self.update_time = datetime.now()
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'product_name': self.product_name,
            'company_name': self.company_name,
            'target_audience': self.target_audience,
            'duration': self.duration,
            'style': self.style,
            'keywords': self.keywords,
            'voice_tone': self.voice_tone,
            'voice_speed': self.voice_speed,
            'reference_image': self.reference_image,
            'create_time': self.create_time.isoformat() if self.create_time else None,
            'update_time': self.update_time.isoformat() if self.update_time else None,
            'frame_prompts': self.frame_prompts,
            'video_prompt': self.video_prompt,
            'video_segments': self.video_segments
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """从字典创建项目对象"""
        if 'create_time' in data and data['create_time']:
            data['create_time'] = datetime.fromisoformat(data['create_time'])
        if 'update_time' in data and data['update_time']:
            data['update_time'] = datetime.fromisoformat(data['update_time'])
        return cls(**data)
