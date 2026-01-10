"""
配置管理模块
"""
import json
import os
import sys
from typing import Dict, Any


class Config:
    """配置管理类"""
    
    def __init__(self, config_file: str = None):
        if config_file is None:
            if getattr(sys, 'frozen', False):
                # If frozen (EXE), look in the same directory as the executable
                project_root = os.path.dirname(sys.executable)
            else:
                # If running from source
                # src/utils/config.py -> src/utils -> src -> root
                current_dir = os.path.dirname(os.path.abspath(__file__))
                project_root = os.path.dirname(os.path.dirname(current_dir))
            
            config_file = os.path.join(project_root, "data", "config.json")
            
        self.config_file = config_file
        self.config_data = {}
        self.load()
        
    def load(self):
        """加载配置"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:
                        self.config_data = json.loads(content)
                    else:
                        # 文件为空，使用默认配置
                        self.config_data = self._get_default_config()
                        self.save()
            except Exception as e:
                print(f"加载配置失败: {str(e)}")
                self.config_data = self._get_default_config()
                self.save()
        else:
            # 初始化默认配置
            self.config_data = self._get_default_config()
            self.save()
    
    def save(self):
        """保存配置"""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(self.config_data, f, ensure_ascii=False, indent=2)
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "llm_apis": [],  # LLM接口列表
            "image_apis": [],  # 图片接口列表
            "video_apis": [],  # 视频接口列表
            "default_llm_api": None,  # 默认LLM接口名称
            "default_image_api": None,  # 默认图片接口名称
            "default_video_api": None,  # 默认视频接口名称
            "general": {
                "projects_dir": "./projects",
                "theme": "light",
                "language": "zh"
            }
        }
    
    def get_llm_apis(self) -> list:
        """获取所有LLM接口配置"""
        return self.config_data.get("llm_apis", [])
    
    def add_llm_api(self, name: str, provider: str, api_key: str, base_url: str = "", model: str = ""):
        """添加LLM接口配置"""
        if "llm_apis" not in self.config_data:
            self.config_data["llm_apis"] = []
        
        # 检查名称是否已存在
        for api in self.config_data["llm_apis"]:
            if api["name"] == name:
                # 更新现有配置
                api["provider"] = provider
                api["api_key"] = api_key
                api["base_url"] = base_url
                api["model"] = model
                return
        
        # 添加新配置
        self.config_data["llm_apis"].append({
            "name": name,
            "provider": provider,
            "api_key": api_key,
            "base_url": base_url,
            "model": model
        })
    
    def delete_llm_api(self, name: str):
        """删除LLM接口配置"""
        if "llm_apis" in self.config_data:
            self.config_data["llm_apis"] = [api for api in self.config_data["llm_apis"] if api["name"] != name]
    
    def get_llm_api(self, name: str) -> Dict[str, str]:
        """根据名称获取LLM接口配置"""
        for api in self.get_llm_apis():
            if api["name"] == name:
                return api
        return {}
    
    def get_default_llm_api(self) -> str:
        """获取默认LLM接口名称"""
        return self.config_data.get("default_llm_api", "")
    
    def set_default_llm_api(self, name: str):
        """设置默认LLM接口"""
        self.config_data["default_llm_api"] = name
    
    def get_llm_config(self) -> Dict[str, str]:
        """获取默认LLM配置（向后兼容）"""
        default_name = self.get_default_llm_api()
        if default_name:
            return self.get_llm_api(default_name)
        apis = self.get_llm_apis()
        return apis[0] if apis else {}
    
    def set_llm_config(self, provider: str, api_key: str, base_url: str = "", model: str = ""):
        """设置LLM配置（向后兼容）"""
        # 迁移旧配置格式到新格式
        if "llm" in self.config_data:
            old_config = self.config_data["llm"]
            name = f"{old_config.get('provider', 'openai')}_接口"
            self.add_llm_api(name, old_config.get('provider', ''), old_config.get('api_key', ''), 
                           old_config.get('base_url', ''), old_config.get('model', ''))
            self.set_default_llm_api(name)
            del self.config_data["llm"]
        
        # 添加新配置
        name = f"{provider}_接口"
        self.add_llm_api(name, provider, api_key, base_url, model)
        if not self.get_default_llm_api():
            self.set_default_llm_api(name)
    
    def get_image_apis(self) -> list:
        """获取所有图片接口配置"""
        return self.config_data.get("image_apis", [])
    
    def add_image_api(self, name: str, provider: str, api_key: str, base_url: str = "", model: str = ""):
        """添加图片接口配置"""
        if "image_apis" not in self.config_data:
            self.config_data["image_apis"] = []
        
        for api in self.config_data["image_apis"]:
            if api["name"] == name:
                api["provider"] = provider
                api["api_key"] = api_key
                api["base_url"] = base_url
                api["model"] = model
                return
        
        self.config_data["image_apis"].append({
            "name": name,
            "provider": provider,
            "api_key": api_key,
            "base_url": base_url,
            "model": model
        })
    
    def delete_image_api(self, name: str):
        """删除图片接口配置"""
        if "image_apis" in self.config_data:
            self.config_data["image_apis"] = [api for api in self.config_data["image_apis"] if api["name"] != name]
    
    def get_image_api(self, name: str) -> Dict[str, str]:
        """根据名称获取图片接口配置"""
        for api in self.get_image_apis():
            if api["name"] == name:
                return api
        return {}
    
    def get_default_image_api(self) -> str:
        """获取默认图片接口名称"""
        return self.config_data.get("default_image_api", "")
    
    def set_default_image_api(self, name: str):
        """设置默认图片接口"""
        self.config_data["default_image_api"] = name
    
    def get_image_config(self) -> Dict[str, str]:
        """获取默认图片配置（向后兼容）"""
        default_name = self.get_default_image_api()
        if default_name:
            return self.get_image_api(default_name)
        apis = self.get_image_apis()
        return apis[0] if apis else {}
    
    def set_image_config(self, provider: str, api_key: str, base_url: str = "", model: str = ""):
        """设置图片配置（向后兼容）"""
        if "image" in self.config_data:
            old_config = self.config_data["image"]
            name = f"{old_config.get('provider', 'stability')}_接口"
            self.add_image_api(name, old_config.get('provider', ''), old_config.get('api_key', ''),
                             old_config.get('base_url', ''), old_config.get('model', ''))
            self.set_default_image_api(name)
            del self.config_data["image"]
        
        name = f"{provider}_接口"
        self.add_image_api(name, provider, api_key, base_url, model)
        if not self.get_default_image_api():
            self.set_default_image_api(name)
    
    def get_video_apis(self) -> list:
        """获取所有视频接口配置"""
        return self.config_data.get("video_apis", [])
    
    def add_video_api(self, name: str, provider: str, api_key: str, base_url: str = "", model: str = ""):
        """添加视频接口配置"""
        if "video_apis" not in self.config_data:
            self.config_data["video_apis"] = []
        
        for api in self.config_data["video_apis"]:
            if api["name"] == name:
                api["provider"] = provider
                api["api_key"] = api_key
                api["base_url"] = base_url
                api["model"] = model
                return
        
        self.config_data["video_apis"].append({
            "name": name,
            "provider": provider,
            "api_key": api_key,
            "base_url": base_url,
            "model": model
        })
    
    def delete_video_api(self, name: str):
        """删除视频接口配置"""
        if "video_apis" in self.config_data:
            self.config_data["video_apis"] = [api for api in self.config_data["video_apis"] if api["name"] != name]
    
    def get_video_api(self, name: str) -> Dict[str, str]:
        """根据名称获取视频接口配置"""
        for api in self.get_video_apis():
            if api["name"] == name:
                return api
        return {}
    
    def get_default_video_api(self) -> str:
        """获取默认视频接口名称"""
        return self.config_data.get("default_video_api", "")
    
    def set_default_video_api(self, name: str):
        """设置默认视频接口"""
        self.config_data["default_video_api"] = name
    
    def get_video_config(self) -> Dict[str, str]:
        """获取默认视频配置（向后兼容）"""
        default_name = self.get_default_video_api()
        if default_name:
            return self.get_video_api(default_name)
        apis = self.get_video_apis()
        return apis[0] if apis else {}
    
    def set_video_config(self, provider: str, api_key: str, base_url: str = "", model: str = ""):
        """设置视频配置（向后兼容）"""
        if "video" in self.config_data:
            old_config = self.config_data["video"]
            name = f"{old_config.get('provider', 'sora')}_接口"
            self.add_video_api(name, old_config.get('provider', ''), old_config.get('api_key', ''),
                             old_config.get('base_url', ''), old_config.get('model', ''))
            self.set_default_video_api(name)
            del self.config_data["video"]
        
        name = f"{provider}_接口"
        self.add_video_api(name, provider, api_key, base_url, model)
        if not self.get_default_video_api():
            self.set_default_video_api(name)
    
    def get_general_config(self) -> Dict[str, str]:
        """获取通用配置"""
        return self.config_data.get("general", {})
    
    def set_general_config(self, **kwargs):
        """设置通用配置"""
        if "general" not in self.config_data:
            self.config_data["general"] = {}
        self.config_data["general"].update(kwargs)
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项"""
        keys = key.split(".")
        value = self.config_data
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default
    
    def set(self, key: str, value: Any):
        """设置配置项"""
        keys = key.split(".")
        config = self.config_data
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
