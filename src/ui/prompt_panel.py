"""
提示词生成面板
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
                             QPushButton, QLabel, QMessageBox, QProgressBar,
                             QGroupBox, QComboBox, QLineEdit)
from PyQt6.QtCore import pyqtSignal, QThread, pyqtSignal as Signal, Qt
from src.models.database import DatabaseManager
from src.models.project import Project
from src.services.llm_service import LLMService
from src.utils.config import Config
from src.utils.language import lang_manager
import os


class PromptGenerationThread(QThread):
    """提示词生成线程"""
    
    finished = Signal(dict)
    error = Signal(str)
    
    def __init__(self, llm_service: LLMService, project_info: dict, image_paths: list):
        super().__init__()
        self.llm_service = llm_service
        self.project_info = project_info
        self.image_paths = image_paths
    
    def run(self):
        """执行生成任务"""
        try:
            result = self.llm_service.generate_prompts(self.project_info, self.image_paths)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class PromptPanel(QWidget):
    """提示词生成面板"""
    
    prompts_generated = pyqtSignal()
    
    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        self.db_manager = db_manager
        self.current_project = None
        self.generation_thread = None
        self.generated_segments = []  # 存储生成的分集信息
        self.episode_prompts = []     # 存储分集分镜提示词 List[List[str]]
        self.current_episode_index = 0 # 当前显示的集数索引（从0开始）
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)
        
        # 标题
        title = QLabel(lang_manager.tr("prompt_panel_title"))
        title.setProperty("class", "title")
        layout.addWidget(title)
  
        # API选择区域
        api_group = QGroupBox(lang_manager.tr("llm_api_group"))
        api_layout = QHBoxLayout()
        
        api_layout.addWidget(QLabel(lang_manager.tr("select_api_label")))
        self.api_provider_combo = QComboBox()
        self.refresh_api_list()
        self.api_provider_combo.setMinimumWidth(200)
        api_layout.addWidget(self.api_provider_combo)
        
        # 添加弹性空间，将按钮推到最右侧
        api_layout.addStretch()
        
        # 移动生成按钮到右侧
        self.generate_btn = QPushButton(lang_manager.tr("generate_prompts_btn"))
        self.generate_btn.clicked.connect(self.generate_prompts)
        self.generate_btn.setMinimumHeight(44)
        self.generate_btn.setMinimumWidth(150)
        api_layout.addWidget(self.generate_btn)
        api_group.setLayout(api_layout)
        layout.addWidget(api_group)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 0)  # 不确定进度
        self.progress_bar.setMaximumHeight(8)
        layout.addWidget(self.progress_bar)
        
        # 分集导航控制
        nav_layout = QHBoxLayout()
        nav_layout.addStretch()
        
        self.prev_ep_btn = QPushButton(lang_manager.tr("prev_episode_btn"))
        self.prev_ep_btn.setFixedWidth(100)
        self.prev_ep_btn.clicked.connect(self.prev_episode)
        self.prev_ep_btn.setEnabled(False)
        nav_layout.addWidget(self.prev_ep_btn)
        
        self.episode_label = QLabel(lang_manager.tr("episode_label_format").format(1, 1))
        self.episode_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.episode_label.setFixedWidth(120)
        self.episode_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        nav_layout.addWidget(self.episode_label)
        
        self.next_ep_btn = QPushButton(lang_manager.tr("next_episode_btn"))
        self.next_ep_btn.setFixedWidth(100)
        self.next_ep_btn.clicked.connect(self.next_episode)
        self.next_ep_btn.setEnabled(False)
        nav_layout.addWidget(self.next_ep_btn)
        
        nav_layout.addStretch()
        layout.addLayout(nav_layout)

        # 提示词编辑区 - 使用水平布局并列显示
        prompts_hlayout = QHBoxLayout()
        prompts_hlayout.setSpacing(16)
        
        # 分镜提示词编辑区（左侧）
        self.frame_group = QGroupBox(lang_manager.tr("frame_prompts_group"))
        frame_layout = QVBoxLayout()
        
        self.frame_prompts_edit = QTextEdit()
        self.frame_prompts_edit.setPlaceholderText(lang_manager.tr("frame_prompts_placeholder"))
        frame_layout.addWidget(self.frame_prompts_edit)
        self.frame_group.setLayout(frame_layout)
        prompts_hlayout.addWidget(self.frame_group, 1)
        
        # 视频提示词编辑区（右侧）
        self.video_group = QGroupBox(lang_manager.tr("video_script_group"))
        video_layout = QVBoxLayout()
        
        self.video_prompt_edit = QTextEdit()
        self.video_prompt_edit.setPlaceholderText(lang_manager.tr("video_prompt_placeholder"))
        video_layout.addWidget(self.video_prompt_edit)
        self.video_group.setLayout(video_layout)
        prompts_hlayout.addWidget(self.video_group, 1)
        
        # 将水平布局添加到主布局
        layout.addLayout(prompts_hlayout, 1)
        
        # 保存按钮 - 固定在底部
        save_btn_layout = QHBoxLayout()
        save_btn_layout.setContentsMargins(0, 12, 0, 0)
        save_btn_layout.addStretch()
        
        self.save_btn = QPushButton(lang_manager.tr("save_prompts_btn"))
        from .styles import apply_button_property
        apply_button_property(self.save_btn, "success")
        self.save_btn.clicked.connect(self.save_prompts)
        self.save_btn.setMinimumHeight(44)
        self.save_btn.setMinimumWidth(150)
        self.save_btn.setEnabled(False)
        save_btn_layout.addWidget(self.save_btn)
        
        layout.addLayout(save_btn_layout, 0)
        
    def refresh_api_list(self):
        """刷新LLM接口列表"""
        self.api_provider_combo.clear()
        config = Config()
        apis = config.get_llm_apis()
        default_api = config.get_default_llm_api()
        
        if not apis:
            self.api_provider_combo.addItem(lang_manager.tr("no_api_configured"))
            return
        
        # 默认接口放在第一位
        default_index = 0
        if default_api:
            for i, api in enumerate(apis):
                if api["name"] == default_api:
                    self.api_provider_combo.addItem(api["name"])
                    default_index = 0
                    break
        
        # 添加其他接口
        for api in apis:
            if api["name"] != default_api:
                self.api_provider_combo.addItem(api["name"])
        
        # 自动选中默认接口
        self.api_provider_combo.setCurrentIndex(default_index)
    
    def update_episode_display(self):
        """更新分集显示"""
        # 更新标题
        self.frame_group.setTitle(lang_manager.tr("frame_prompts_title_format").format(self.current_episode_index + 1))
        self.video_group.setTitle(lang_manager.tr("video_script_title_format").format(self.current_episode_index + 1))
        self.episode_label.setText(lang_manager.tr("episode_label_format").format(self.current_episode_index + 1, self.total_episodes))
        
        # 更新导航按钮状态
        self.prev_ep_btn.setEnabled(self.current_episode_index > 0)
        self.next_ep_btn.setEnabled(self.current_episode_index < self.total_episodes - 1)
        
        # 显示当前集的分镜提示词
        if self.current_episode_index < len(self.episode_prompts):
            current_prompts = self.episode_prompts[self.current_episode_index]
        else:
            current_prompts = []
            
        frame_text = ""
        for i, prompt in enumerate(current_prompts):
            frame_text += f"{i+1}. {prompt}\n"
        self.frame_prompts_edit.setText(frame_text.strip())
        
        # 显示当前集的视频脚本
        if self.current_episode_index < len(self.generated_segments):
            segment = self.generated_segments[self.current_episode_index]
            self.video_prompt_edit.setText(segment.get("prompt", ""))
        else:
            # 如果没有对应的分集脚本（兼容旧数据），显示全部或为空
            if self.current_episode_index == 0 and not self.generated_segments:
                 # 尝试显示项目的完整视频提示词
                 if self.current_project and self.current_project.video_prompt:
                     self.video_prompt_edit.setText(self.current_project.video_prompt)
                 else:
                     self.video_prompt_edit.clear()
            else:
                self.video_prompt_edit.clear()

    def save_current_episode_edits(self):
        """保存当前分集的编辑内容"""
        # 保存分镜提示词
        frame_text = self.frame_prompts_edit.toPlainText().strip()
        current_prompts = []
        for line in frame_text.split("\n"):
            line = line.strip()
            if not line:
                continue
            # 移除序号 "1. "
            if ". " in line and line.split(". ", 1)[0].isdigit():
                prompt = line.split(". ", 1)[1].strip()
            else:
                prompt = line
            current_prompts.append(prompt)
        
        # 更新到 episode_prompts
        while len(self.episode_prompts) <= self.current_episode_index:
            self.episode_prompts.append([])
            
        self.episode_prompts[self.current_episode_index] = current_prompts
                
        # 保存视频脚本
        video_text = self.video_prompt_edit.toPlainText().strip()
        if self.current_episode_index < len(self.generated_segments):
            self.generated_segments[self.current_episode_index]["prompt"] = video_text
        elif self.current_episode_index == 0 and not self.generated_segments:
             # 如果是第一集且没有分集数据，可能是在编辑旧项目的完整脚本
             pass 

    def prev_episode(self):
        """上一集"""
        if self.current_episode_index > 0:
            self.save_current_episode_edits()
            self.current_episode_index -= 1
            self.update_episode_display()
            
    def next_episode(self):
        """下一集"""
        if self.current_episode_index < self.total_episodes - 1:
            self.save_current_episode_edits()
            self.current_episode_index += 1
            self.update_episode_display()

    def load_project(self, project: Project):
        """加载项目数据"""
        self.current_project = project
        
        # 加载分镜提示词并分块
        raw_prompts = project.frame_prompts if project.frame_prompts else []
        self.episode_prompts = []
        
        # 按每集5个分块 (对应6宫格：1参考+5生成)
        if raw_prompts:
            chunk_size = 5
            # 兼容旧数据：如果是4的倍数且不是5的倍数，则按4分块
            if len(raw_prompts) % 4 == 0 and len(raw_prompts) % 5 != 0:
                chunk_size = 4
                
            for i in range(0, len(raw_prompts), chunk_size):
                self.episode_prompts.append(raw_prompts[i:i+chunk_size])
        
        # 加载分集信息
        self.generated_segments = project.video_segments if project.video_segments else []
        
        # 计算总集数
        # 优先使用 video_segments 的长度
        if self.generated_segments:
            self.total_episodes = len(self.generated_segments)
            # 确保 episode_prompts 长度匹配
            while len(self.episode_prompts) < self.total_episodes:
                self.episode_prompts.append([])
        # 否则根据分镜数量计算
        elif self.episode_prompts:
            self.total_episodes = len(self.episode_prompts)
        else:
            self.total_episodes = 1
            self.episode_prompts = [[]] # 至少有一集
        
        # 如果没有分集信息，但有总集数（来自 prompts），初始化 generated_segments
        # 这样可以确保旧项目也能正常编辑和保存
        if not self.generated_segments and self.total_episodes > 0:
            self.generated_segments = []
            for i in range(self.total_episodes):
                prompt_content = ""
                # 将原有 video_prompt 放入第一集
                if i == 0 and project.video_prompt:
                    prompt_content = project.video_prompt
                
                self.generated_segments.append({
                    "episode": i + 1,
                    "prompt": prompt_content,
                    "duration": 15 # 默认时长
                })
            
        self.current_episode_index = 0
        self.update_episode_display()
        
        self.generate_btn.setEnabled(True)
        self.save_btn.setEnabled(bool(project.frame_prompts or project.video_prompt))
    
    def generate_prompts(self):
        """生成提示词"""
        if not self.current_project:
            QMessageBox.warning(self, lang_manager.tr("warning"), lang_manager.tr("msg_select_project_first"))
            return
        
        if not self.current_project.id:
            QMessageBox.warning(self, lang_manager.tr("warning"), lang_manager.tr("msg_save_project_first"))
            return
        
        # 确认是否重新生成
        if self.frame_prompts_edit.toPlainText().strip():
            reply = QMessageBox.question(
                self,
                lang_manager.tr("confirm_regenerate_title"),
                lang_manager.tr("confirm_regenerate_msg"),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return
        else:
            # 新生成时也要确认
            reply = QMessageBox.question(
                self,
                lang_manager.tr("confirm_generate_title"),
                lang_manager.tr("confirm_generate_msg"),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
        
        # 获取配置
        config = Config()
        
        # 根据接口名称获取配置
        selected_api_name = self.api_provider_combo.currentText()
        
        if selected_api_name == lang_manager.tr("no_api_configured"):
            QMessageBox.warning(self, lang_manager.tr("warning"), lang_manager.tr("msg_configure_llm_first"))
            return
        
        llm_config = config.get_llm_api(selected_api_name)
        
        if not llm_config or not llm_config.get("api_key"):
            QMessageBox.warning(self, lang_manager.tr("warning"), lang_manager.tr("msg_api_config_incomplete").format(selected_api_name))
            return
        
        # 准备项目信息
        project_info = {
            "type": self.current_project.type,
            "product_name": self.current_project.product_name,
            "company_name": self.current_project.company_name,
            "keywords": self.current_project.keywords,
            "style": self.current_project.style,
            "duration": self.current_project.duration,
            "target_audience": self.current_project.target_audience,
            "voice_tone": self.current_project.voice_tone,
            "voice_speed": self.current_project.voice_speed
        }
        
        # 获取参考图片
        image_paths = []
        if self.current_project.id:
            images_dir = os.path.join(
                self.db_manager.get_project_path(self.current_project.id),
                "images"
            )
            if os.path.exists(images_dir):
                image_paths = [
                    os.path.join(images_dir, f)
                    for f in os.listdir(images_dir)
                    if f.lower().endswith(('.png', '.jpg', '.jpeg'))
                ]
        
        # 创建LLM服务
        llm_service = LLMService(
            api_provider=llm_config.get("provider", "openai"),
            api_key=llm_config["api_key"],
            base_url=llm_config.get("base_url", ""),
            model=llm_config.get("model", "")
        )
        
        # 启动生成线程
        self.generate_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        
        self.generation_thread = PromptGenerationThread(llm_service, project_info, image_paths)
        self.generation_thread.finished.connect(self.on_generation_finished)
        self.generation_thread.error.connect(self.on_generation_error)
        self.generation_thread.start()
    
    def on_generation_finished(self, result: dict):
        """生成完成"""
        self.progress_bar.setVisible(False)
        self.generate_btn.setEnabled(True)
        
        # 获取结果
        raw_prompts = result.get("frame_prompts", [])
        self.generated_segments = result.get("video_segments", [])
        video_prompt = result.get("video_prompt", "")
        
        # 处理分镜提示词分块
        self.episode_prompts = []
        if raw_prompts:
            # 新生成的一律按5个一组（因为模板已更新为6宫格/5生成）
            for i in range(0, len(raw_prompts), 5):
                self.episode_prompts.append(raw_prompts[i:i+5])
        
        # 计算集数
        if self.generated_segments:
            self.total_episodes = len(self.generated_segments)
            # 确保 episode_prompts 长度匹配
            while len(self.episode_prompts) < self.total_episodes:
                self.episode_prompts.append([])
        elif self.episode_prompts:
            self.total_episodes = len(self.episode_prompts)
        else:
            self.total_episodes = 1
            self.episode_prompts = [[]]
            
        # 确保 generated_segments 与 total_episodes 同步
        if len(self.generated_segments) < self.total_episodes:
            for i in range(len(self.generated_segments), self.total_episodes):
                self.generated_segments.append({
                    "episode": i + 1,
                    "prompt": video_prompt if i == 0 and not self.generated_segments else "",
                    "duration": 15
                })
             
        # 重置到第一集并显示
        self.current_episode_index = 0
        self.update_episode_display()
        
        self.save_btn.setEnabled(True)
        
        # 计算总分镜数
        total_frames = sum(len(ep) for ep in self.episode_prompts)
        
        QMessageBox.information(
            self,
            lang_manager.tr("success"),
            lang_manager.tr("msg_prompts_generated_success").format(total_frames, self.total_episodes)
        )
    
    def on_generation_error(self, error_msg: str):
        """生成失败"""
        self.progress_bar.setVisible(False)
        self.generate_btn.setEnabled(True)
        
        # 根据错误类型提供更明确的提示
        if "401" in error_msg or "Unauthorized" in error_msg:
            QMessageBox.critical(
                self, 
                lang_manager.tr("error_api_key"), 
                lang_manager.tr("msg_api_key_error").format(error_msg)
            )
        elif "403" in error_msg or "Forbidden" in error_msg:
            QMessageBox.critical(
                self, 
                lang_manager.tr("error_access_denied"), 
                lang_manager.tr("msg_access_denied_error").format(error_msg)
            )
        elif "404" in error_msg or "Not Found" in error_msg:
            QMessageBox.critical(
                self, 
                lang_manager.tr("error_api_address"), 
                lang_manager.tr("msg_api_address_error").format(error_msg)
            )
        else:
            QMessageBox.critical(
                self,
                lang_manager.tr("error"),
                lang_manager.tr("msg_generate_failed").format(error_msg)
            )
    
    def save_prompts(self):
        """保存提示词"""
        if not self.current_project or not self.current_project.id:
            QMessageBox.warning(self, lang_manager.tr("warning"), lang_manager.tr("msg_save_project_first"))
            return
        
        # 先保存当前显示的编辑内容
        self.save_current_episode_edits()
        
        # 扁平化分镜提示词
        all_frames = []
        for ep in self.episode_prompts:
            all_frames.extend(ep)
            
        # 验证提示词数量
        if not all_frames:
             QMessageBox.warning(self, lang_manager.tr("warning"), lang_manager.tr("msg_empty_prompts"))
             return
             
        # 警告如果不是5的倍数（可选）
        if len(all_frames) % 5 != 0:
            reply = QMessageBox.question(
                self,
                lang_manager.tr("msg_frame_count_warning_title"),
                lang_manager.tr("msg_frame_count_warning").format(len(all_frames)),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return

        # 保存到项目
        self.current_project.frame_prompts = all_frames
        
        # 构造完整的视频脚本（合并所有分集）
        full_video_prompt = ""
        for segment in self.generated_segments:
            header = lang_manager.tr("video_script_header_format").format(segment.get('episode', 1))
            full_video_prompt += f"{header}\n{segment.get('prompt', '')}\n\n"
            
        # 如果没有分集信息（例如手动编辑或旧项目），尝试使用当前video_prompt_edit的内容作为兜底（如果是单集）
        if not self.generated_segments and self.total_episodes == 1:
             full_video_prompt = self.video_prompt_edit.toPlainText().strip()

        self.current_project.video_prompt = full_video_prompt.strip()
        self.current_project.video_segments = self.generated_segments
        
        try:
            self.db_manager.update_project(self.current_project)
            QMessageBox.information(self, lang_manager.tr("success"), lang_manager.tr("msg_save_prompts_success"))
            self.prompts_generated.emit()
        except Exception as e:
            QMessageBox.critical(self, lang_manager.tr("error"), lang_manager.tr("msg_save_failed").format(str(e)))
    
    def clear(self):
        """清空面板"""
        self.current_project = None
        self.episode_prompts = []
        self.generated_segments = []
        self.current_episode_index = 0
        self.total_episodes = 1
        
        self.frame_prompts_edit.clear()
        self.video_prompt_edit.clear()
        self.generate_btn.setEnabled(False)
        self.save_btn.setEnabled(False)
        
        self.update_episode_display()
