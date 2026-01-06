"""
分镜图片生成和展示面板
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QPushButton, QLabel, QMessageBox, QProgressBar,
                             QFileDialog, QScrollArea, QFrame, QGroupBox, 
                             QComboBox, QLineEdit, QSizePolicy)
from PyQt6.QtCore import pyqtSignal, QThread, Qt, QRect, QSize
from PyQt6.QtGui import QPixmap
from src.models.database import DatabaseManager
from src.models.project import Project
from src.services.image_service import ImageService
from src.utils.config import Config
from src.utils.language import lang_manager
from .flow_layout import FlowLayout
import os


class FrameGenerationThread(QThread):
    """分镜生成线程"""
    
    progress = pyqtSignal(int, str, bool)
    finished = pyqtSignal(list)
    error = pyqtSignal(str)
    
    def __init__(self, image_service: ImageService, prompts: list, output_dir: str, style: str = "cinematic", reference_image: str = None, skip_existing: bool = False, start_index: int = 1):
        super().__init__()
        self.image_service = image_service
        self.prompts = prompts
        self.output_dir = output_dir
        self.style = style
        self.reference_image = reference_image
        self.skip_existing = skip_existing
        self.start_index = start_index
    
    def run(self):
        """执行生成任务"""
        try:
            image_paths = self.image_service.generate_frames(
                self.prompts,
                self.output_dir,
                style=self.style,
                reference_image=self.reference_image,
                progress_callback=self.progress.emit,
                skip_existing=self.skip_existing,
                start_index=self.start_index
            )
            self.finished.emit(image_paths)
        except Exception as e:
            self.error.emit(str(e))


class SingleFrameGenerationThread(QThread):
    """单个分镜生成线程"""
    
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, image_service: ImageService, prompt: str, output_path: str, style: str):
        super().__init__()
        self.image_service = image_service
        self.prompt = prompt
        self.output_path = output_path
        self.style = style
    
    def run(self):
        """执行生成任务"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
            
            image_path = self.image_service.regenerate_frame(
                self.prompt,
                self.output_path,
                style=self.style
            )
            self.finished.emit(image_path)
        except Exception as e:
            self.error.emit(str(e))


class FrameWidget(QFrame):
    """单个分镜部件"""
    
    regenerate_clicked = pyqtSignal(int)
    replace_clicked = pyqtSignal(int)
    delete_clicked = pyqtSignal(int)
    
    def __init__(self, frame_number: int):
        super().__init__()
        self.frame_number = frame_number
        self.image_path = None
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        self.setLineWidth(1)
        self.setFixedSize(260, 360)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
            }
            QFrame:hover {
                border: 2px solid #2563eb;
                background-color: #f8fafc;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 15)
        layout.setSpacing(8)
        
        # 标题
        title = QLabel(lang_manager.tr("frame_title_format").format(self.frame_number))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            font-weight: bold; 
            font-size: 14px; 
            color: #1f2937;
            background-color: transparent;
            padding: 4px;
        """)
        layout.addWidget(title)
        
        # 图片显示容器
        image_container = QWidget()
        image_container.setFixedSize(218, 218)
        image_container.setStyleSheet("background-color: transparent;")
        image_container_layout = QVBoxLayout(image_container)
        image_container_layout.setContentsMargins(0, 0, 0, 0)
        
        self.image_label = QLabel()
        self.image_label.setFixedSize(218, 218)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("""
            background-color: #f3f4f6; 
            border: 1px solid #d1d5db; 
            border-radius: 6px;
            color: #9ca3af;
        """)
        self.image_label.setText(lang_manager.tr("status_not_generated"))
        self.image_label.setScaledContents(False)
        self.image_label.setToolTip(lang_manager.tr("frame_title_format").format(self.frame_number))
        image_container_layout.addWidget(self.image_label)
        
        # 删除按钮（悬浮在右上角）
        self.delete_btn = QPushButton("×", image_container)
        self.delete_btn.setFixedSize(24, 24)
        self.delete_btn.move(188, 6)  # 定位到右上角
        self.delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(0, 0, 0, 0.5);
                color: white;
                border-radius: 12px;
                font-weight: bold;
                font-size: 16px;
                border: none;
                padding-bottom: 2px;
            }
            QPushButton:hover {
                background-color: rgba(220, 38, 38, 0.9);
            }
        """)
        self.delete_btn.clicked.connect(lambda: self.delete_clicked.emit(self.frame_number))
        self.delete_btn.setVisible(False)  # 默认隐藏
        
        layout.addWidget(image_container, 0, Qt.AlignmentFlag.AlignCenter)
        
        # 按钮组
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        from .styles import apply_button_property
        
        self.regenerate_btn = QPushButton(lang_manager.tr("regenerate_btn"))
        self.regenerate_btn.clicked.connect(lambda: self.regenerate_clicked.emit(self.frame_number))
        self.regenerate_btn.setEnabled(False)
        apply_button_property(self.regenerate_btn, "secondary")
        self.regenerate_btn.setFixedHeight(32)
        self.regenerate_btn.setFixedWidth(110)
        btn_layout.addWidget(self.regenerate_btn)
        
        self.replace_btn = QPushButton(lang_manager.tr("replace_btn"))
        self.replace_btn.clicked.connect(lambda: self.replace_clicked.emit(self.frame_number))
        apply_button_property(self.replace_btn, "info")
        self.replace_btn.setFixedHeight(32)
        self.replace_btn.setFixedWidth(110)
        btn_layout.addWidget(self.replace_btn)
        
        layout.addLayout(btn_layout)
        
    def set_image(self, image_path: str):
        """设置图片"""
        if image_path and os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            scaled_pixmap = pixmap.scaled(
                208, 208,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)
            self.image_path = image_path
            self.regenerate_btn.setEnabled(True)
            self.delete_btn.setVisible(True)
            self.image_label.setToolTip(f"{lang_manager.tr('frame_title_format').format(self.frame_number)}\n{os.path.basename(image_path)}")
        else:
            self.clear_image()

    def clear_image(self):
        """清除图片"""
        self.image_label.clear()
        self.image_label.setText(lang_manager.tr("status_not_generated"))
        self.image_path = None
        self.regenerate_btn.setEnabled(False)
        self.delete_btn.setVisible(False)
        self.image_label.setToolTip(lang_manager.tr("frame_title_format").format(self.frame_number))


class FramePanel(QWidget):
    """分镜图片面板"""
    
    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        self.db_manager = db_manager
        self.current_project = None
        self.frame_widgets = []
        self.generation_thread = None
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)
        
        # 标题
        title = QLabel(lang_manager.tr("frame_panel_title"))
        title.setProperty("class", "title")
        layout.addWidget(title)
        
        # 控制区域（接口选择 + 分集选择）
        control_group = QGroupBox(lang_manager.tr("generation_settings_group"))
        control_layout = QGridLayout()
        control_layout.setSpacing(15)
        
        # 1. 接口选择
        control_layout.addWidget(QLabel(lang_manager.tr("image_api_label")), 0, 0)
        self.api_provider_combo = QComboBox()
        self.api_provider_combo.setMinimumWidth(200)
        self.refresh_api_list()
        control_layout.addWidget(self.api_provider_combo, 0, 1)
        
        # 2. 分集选择
        control_layout.addWidget(QLabel(lang_manager.tr("select_episode_label")), 0, 2)
        self.episode_combo = QComboBox()
        self.episode_combo.setMinimumWidth(150)
        self.episode_combo.currentIndexChanged.connect(self.on_episode_changed)
        control_layout.addWidget(self.episode_combo, 0, 3)
        
        # 3. 操作按钮
        btn_layout = QHBoxLayout()
        
        self.clear_episode_btn = QPushButton(lang_manager.tr("clear_episode_btn"))
        self.clear_episode_btn.clicked.connect(self.clear_episode_frames)
        from .styles import apply_button_property
        apply_button_property(self.clear_episode_btn, "danger")
        btn_layout.addWidget(self.clear_episode_btn)
        
        self.generate_episode_btn = QPushButton(lang_manager.tr("generate_episode_btn"))
        self.generate_episode_btn.clicked.connect(self.generate_episode_frames)
        self.generate_episode_btn.setMinimumWidth(150)
        btn_layout.addWidget(self.generate_episode_btn)
        
        self.export_grid_btn = QPushButton(lang_manager.tr("export_grid_btn"))
        apply_button_property(self.export_grid_btn, "info")
        self.export_grid_btn.clicked.connect(self.export_grid)
        self.export_grid_btn.setEnabled(False)
        btn_layout.addWidget(self.export_grid_btn)
        
        control_layout.addLayout(btn_layout, 0, 4)
        control_layout.setColumnStretch(4, 1)
        
        # 4. 提示词输入区
        prompt_layout = QVBoxLayout()
        prompt_layout.setSpacing(5)  # 减小标题和文本框的间距
        prompt_layout.addWidget(QLabel(lang_manager.tr("current_episode_prompts_label")))
        
        from PyQt6.QtWidgets import QTextEdit
        self.prompts_edit = QTextEdit()
        self.prompts_edit.setPlaceholderText(lang_manager.tr("frame_prompts_input_placeholder"))
        self.prompts_edit.setMinimumHeight(100)  # 增加高度
        prompt_layout.addWidget(self.prompts_edit)
        
        control_layout.addLayout(prompt_layout, 1, 0, 1, 5)
        
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumHeight(8)
        layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel()
        self.status_label.setVisible(False)
        layout.addWidget(self.status_label)
        
        # 六宫格显示区
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #f9fafb;
            }
            QWidget {
                background-color: #f9fafb;
            }
        """)
        
        grid_container = QWidget()
        # 使用FlowLayout替代QGridLayout
        self.grid_layout = FlowLayout(grid_container)
        self.grid_layout.setSpacing(20)
        self.grid_layout.setContentsMargins(20, 20, 20, 20)
        
        # 创建6个分镜卡片
        self.frame_widgets = []
        for i in range(6):
            widget = FrameWidget(i + 1)
            widget.regenerate_clicked.connect(self.regenerate_frame)
            widget.replace_clicked.connect(self.replace_frame)
            widget.delete_clicked.connect(self.delete_frame)
            
            self.grid_layout.addWidget(widget)
            self.frame_widgets.append(widget)
            
            # 第1个分镜特殊处理 (参考图)
            if i == 0:
                widget.regenerate_btn.setVisible(False) # 参考图不能重新生成
                widget.delete_btn.setVisible(False) # 参考图不能删除? 或者可以删除但逻辑不同
                widget.image_label.setText(lang_manager.tr("status_reference_image"))
        
        scroll_area.setWidget(grid_container)
        layout.addWidget(scroll_area)
        
    def refresh_api_list(self):
        """刷新图片接口列表"""
        self.api_provider_combo.clear()
        config = Config()
        apis = config.get_image_apis()
        default_api = config.get_default_image_api()
        
        if not apis:
            self.api_provider_combo.addItem(lang_manager.tr("api_not_configured"))
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
    
    def load_project(self, project: Project):
        """加载项目数据"""
        self.current_project = project
        
        # 初始化分集下拉框
        self.episode_combo.blockSignals(True)
        self.episode_combo.clear()
        
        # 确定总集数
        episode_count = 1
        if project.video_segments:
            episode_count = len(project.video_segments)
        else:
            # 根据时长计算 (每集15秒)
            duration = project.duration if project.duration else 15
            episode_count = max(1, (duration + 14) // 15)
            
        # 填充下拉框
        for i in range(episode_count):
             self.episode_combo.addItem(lang_manager.tr("episode_combo_format").format(i+1))
            
        self.episode_combo.blockSignals(False)
        
        # 加载当前集数据
        self.on_episode_changed(0)
        
    def on_episode_changed(self, index):
        """分集切换处理"""
        if index < 0 or not self.current_project:
            return
            
        episode = index + 1
        frames_dir = os.path.join(self.db_manager.get_project_path(self.current_project.id), "frames", f"ep_{episode}")
        
        # 1. 更新提示词显示
        # 尝试从项目数据中获取该集的提示词
        # 这里假设 frame_prompts 可能按顺序存储了各集的提示词，或者我们需要新的存储方式
        # 暂时逻辑：如果 frame_prompts 足够长，则切片；否则留空
        prompts_text = ""
        start_idx = (episode - 1) * 5
        if self.current_project.frame_prompts and len(self.current_project.frame_prompts) >= start_idx + 5:
            current_prompts = self.current_project.frame_prompts[start_idx:start_idx+5]
            prompts_text = "\n".join(current_prompts)
        
        self.prompts_edit.setText(prompts_text)
        
        # 2. 加载图片
        for i, frame_widget in enumerate(self.frame_widgets):
            frame_path = os.path.join(frames_dir, f"frame_{i+1}.png")
            if os.path.exists(frame_path):
                frame_widget.set_image(frame_path)
            else:
                frame_widget.clear_image()
                if i == 0:
                    frame_widget.image_label.setText(lang_manager.tr("status_reference_image"))
                else:
                    frame_widget.image_label.setText(lang_manager.tr("status_not_generated"))
        
        # 3. 更新按钮状态
        self.check_episode_frames_generated()

    def check_episode_frames_generated(self):
        """检查当前集分镜生成状态"""
        if not self.current_project:
            return
            
        episode = self.episode_combo.currentIndex() + 1
        frames_dir = os.path.join(self.db_manager.get_project_path(self.current_project.id), "frames", f"ep_{episode}")
        
        all_generated = True
        for i in range(6): # 6个分镜
            if not os.path.exists(os.path.join(frames_dir, f"frame_{i+1}.png")):
                all_generated = False
                break
        
        self.export_grid_btn.setEnabled(all_generated)
    
    def generate_episode_frames(self):
        """生成当前集分镜"""
        if not self.current_project or not self.current_project.id:
            QMessageBox.warning(self, lang_manager.tr("warning"), lang_manager.tr("msg_save_project_first"))
            return
        
        # 获取提示词
        prompts_text = self.prompts_edit.toPlainText().strip()
        if not prompts_text:
            QMessageBox.warning(self, lang_manager.tr("warning"), lang_manager.tr("msg_enter_frame_prompts"))
            return
            
        prompts = [p.strip() for p in prompts_text.split('\n') if p.strip()]
        if len(prompts) < 5:
             QMessageBox.warning(self, lang_manager.tr("warning"), lang_manager.tr("msg_prompts_count_error"))
             return
             
        # 只取前5个
        prompts = prompts[:5]
        
        # 确认生成
        reply = QMessageBox.question(
            self,
            lang_manager.tr("confirm_generate"),
            lang_manager.tr("confirm_generate_frame_msg").format(self.episode_combo.currentIndex() + 1),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # 获取配置
        config = Config()
        selected_api_name = self.api_provider_combo.currentText()
        
        if selected_api_name == lang_manager.tr("api_not_configured"):
            QMessageBox.warning(self, lang_manager.tr("warning"), lang_manager.tr("msg_configure_image_api_first"))
            return
        
        image_config = config.get_image_api(selected_api_name)
        if not image_config or not image_config.get("api_key"):
            QMessageBox.warning(self, lang_manager.tr("warning"), lang_manager.tr("msg_api_config_incomplete_simple").format(selected_api_name))
            return
            
        # 准备目录
        episode = self.episode_combo.currentIndex() + 1
        frames_dir = os.path.join(self.db_manager.get_project_path(self.current_project.id), "frames", f"ep_{episode}")
        os.makedirs(frames_dir, exist_ok=True)
        
        # 创建图片服务
        image_service = ImageService(
            api_provider=image_config.get("provider", "stability"),
            api_key=image_config["api_key"],
            base_url=image_config.get("base_url", ""),
            model=image_config.get("model", "")
        )
        
        # UI状态更新
        self.generate_episode_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(5)  # 生成5张
        self.progress_bar.setValue(0)
        self.status_label.setVisible(True)
        
        # 1. 处理参考图 (Frame 1)
        reference_image = None
        if self.current_project.reference_image:
            ref_path = os.path.join(
                self.db_manager.get_project_path(self.current_project.id),
                "reference",
                os.path.basename(self.current_project.reference_image)
            )
            if os.path.exists(ref_path):
                reference_image = ref_path
                try:
                    target_path = os.path.join(frames_dir, "frame_1.png")
                    import shutil
                    shutil.copy2(ref_path, target_path)
                    self.frame_widgets[0].set_image(target_path)
                except Exception as e:
                    print(lang_manager.tr("log_copy_ref_failed").format(e))

        # 2. 准备提示词 (添加风格)
        modified_prompts = [f"{p}, line art, sketch style, black and white, no realistic humans" for p in prompts]
        
        # 3. 启动线程
        # 强制使用线稿风格
        style_preset = "line-art" 
        
        self.generation_thread = FrameGenerationThread(
            image_service,
            modified_prompts,
            frames_dir,
            style_preset,
            reference_image,
            skip_existing=True, # 总是跳过存在的? 或者由用户决定? 这里暂时强制跳过
            start_index=2  # 从frame_2开始
        )
        self.generation_thread.progress.connect(self.on_generation_progress)
        self.generation_thread.finished.connect(self.on_generation_finished)
        self.generation_thread.error.connect(self.on_generation_error)
        self.generation_thread.start()

    def on_generation_progress(self, current: int, status: str, is_completed: bool):
        """生成进度更新"""
        # current 现在直接是 frame_num (例如 2, 3, 4, 5, 6)
        
        # 进度条仍然需要 0-5 的值，或者我们调整进度条的范围
        # 为了简单，我们让进度条只是一个视觉指示
        # 计算生成的数量： current - start_index + 1
        # start_index 是 2
        progress_val = current - 1 
        self.progress_bar.setValue(progress_val)
        self.status_label.setText(status)
        
        if is_completed:
             frame_idx = current
             
             episode = self.episode_combo.currentIndex() + 1
             frames_dir = os.path.join(self.db_manager.get_project_path(self.current_project.id), "frames", f"ep_{episode}")
             frame_path = os.path.join(frames_dir, f"frame_{frame_idx}.png")
             
             if os.path.exists(frame_path) and 1 <= frame_idx <= 6:
                 # frame_widgets 索引是 0-based, frame_idx 是 1-based
                 self.frame_widgets[frame_idx - 1].set_image(frame_path)
    
    def on_generation_finished(self, image_paths: list):
        """生成完成"""
        self.progress_bar.setVisible(False)
        self.status_label.setVisible(False)
        self.generate_episode_btn.setEnabled(True)
        
        # 强制重新加载当前集的所有图片，确保最终状态一致
        self.on_episode_changed(self.episode_combo.currentIndex())
        
        self.check_episode_frames_generated()
        QMessageBox.information(self, lang_manager.tr("success"), lang_manager.tr("msg_frame_generation_complete"))

    def on_generation_error(self, error_msg: str):
        """生成错误处理"""
        self.progress_bar.setVisible(False)
        self.status_label.setVisible(False)
        self.generate_episode_btn.setEnabled(True)
        QMessageBox.critical(self, lang_manager.tr("error"), lang_manager.tr("msg_frame_generation_failed").format(error_msg))
        
    def clear_episode_frames(self):
        """清空当前集分镜"""
        if not self.current_project:
            return
            
        episode = self.episode_combo.currentIndex() + 1
        reply = QMessageBox.question(
            self,
            lang_manager.tr("msg_confirm_clear_episode_title"),
            lang_manager.tr("msg_confirm_clear_episode").format(episode),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            frames_dir = os.path.join(self.db_manager.get_project_path(self.current_project.id), "frames", f"ep_{episode}")
            if os.path.exists(frames_dir):
                import shutil
                shutil.rmtree(frames_dir)
                os.makedirs(frames_dir, exist_ok=True)
            
            # 刷新显示
            self.on_episode_changed(self.episode_combo.currentIndex())


    def delete_frame(self, frame_number: int):
        """删除单个分镜"""
        if not self.current_project or not self.current_project.id:
            return
            
        reply = QMessageBox.question(
            self,
            lang_manager.tr("msg_confirm_delete_frame_title"),
            lang_manager.tr("msg_confirm_delete_frame").format(frame_number),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                episode = self.episode_combo.currentIndex() + 1
                frames_dir = os.path.join(self.db_manager.get_project_path(self.current_project.id), "frames", f"ep_{episode}")
                file_path = os.path.join(frames_dir, f"frame_{frame_number}.png")
                
                if os.path.exists(file_path):
                    os.remove(file_path)
                
                # 删除对应的缓存文件
                json_path = os.path.join(frames_dir, f"frame_{frame_number}.json")
                if os.path.exists(json_path):
                    os.remove(json_path)
                    
                self.frame_widgets[frame_number - 1].clear_image()
                if frame_number == 1:
                    self.frame_widgets[frame_number - 1].image_label.setText(lang_manager.tr("status_reference_image"))
                else:
                    self.frame_widgets[frame_number - 1].image_label.setText(lang_manager.tr("status_not_generated"))

                self.check_episode_frames_generated()
                
            except Exception as e:
                QMessageBox.critical(self, lang_manager.tr("error"), lang_manager.tr("msg_delete_failed").format(str(e)))

    def regenerate_frame(self, frame_number: int):
        """重新生成单个分镜"""
        if not self.current_project or not self.current_project.id:
            return
            
        # frame_1 是参考图，不能重新生成
        if frame_number == 1:
            return
            
        reply = QMessageBox.question(
            self,
            lang_manager.tr("confirm_regenerate_title"),
            lang_manager.tr("msg_confirm_regenerate_frame").format(frame_number),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return

        # 获取配置
        config = Config()
        selected_api_name = self.api_provider_combo.currentText()
        
        if selected_api_name == lang_manager.tr("api_not_configured"):
            QMessageBox.warning(self, lang_manager.tr("warning"), lang_manager.tr("msg_configure_image_api_first"))
            return
            
        image_config = config.get_image_api(selected_api_name)
        if not image_config or not image_config.get("api_key"):
            QMessageBox.warning(self, lang_manager.tr("warning"), lang_manager.tr("msg_api_config_incomplete_simple").format(selected_api_name))
            return
            
        # 准备提示词
        prompts_text = self.prompts_edit.toPlainText().strip()
        prompts = [p.strip() for p in prompts_text.split('\n') if p.strip()]
        
        # frame_2 对应 prompts[0], frame_3 对应 prompts[1], frame_4 对应 prompts[2]
        prompt_index = frame_number - 2
        
        if prompt_index < 0 or prompt_index >= len(prompts):
             QMessageBox.warning(self, lang_manager.tr("warning"), lang_manager.tr("msg_missing_prompt_for_frame").format(frame_number))
             return
             
        prompt = prompts[prompt_index]
        
        # 添加风格
        prompt = f"{prompt}, line art, sketch style, black and white, no realistic humans"
             
        # Create ImageService
        image_service = ImageService(
            api_provider=image_config.get("provider", "stability"),
            api_key=image_config["api_key"],
            base_url=image_config.get("base_url", ""),
            model=image_config.get("model", "")
        )
        
        episode = self.episode_combo.currentIndex() + 1
        frames_dir = os.path.join(self.db_manager.get_project_path(self.current_project.id), "frames", f"ep_{episode}")
        os.makedirs(frames_dir, exist_ok=True)
        output_path = os.path.join(frames_dir, f"frame_{frame_number}.png")
        
        # Disable button
        self.frame_widgets[frame_number - 1].regenerate_btn.setEnabled(False)
        self.frame_widgets[frame_number - 1].image_label.setText(lang_manager.tr("status_generating"))
        
        # Start thread
        self.single_gen_thread = SingleFrameGenerationThread(
            image_service,
            prompt,
            output_path,
            image_config.get("style", "cinematic")
        )
        self.single_gen_thread.finished.connect(lambda path: self.on_single_frame_finished(path, frame_number))
        self.single_gen_thread.error.connect(lambda err: self.on_single_frame_error(err, frame_number))
        self.single_gen_thread.start()

    def on_single_frame_finished(self, path: str, frame_number: int):
        """单个分镜生成完成"""
        if os.path.exists(path):
            self.frame_widgets[frame_number - 1].set_image(path)
            QMessageBox.information(self, lang_manager.tr("success"), lang_manager.tr("msg_regenerate_success").format(frame_number))
        self.check_episode_frames_generated()
        
    def on_single_frame_error(self, error: str, frame_number: int):
        """单个分镜生成失败"""
        self.frame_widgets[frame_number - 1].regenerate_btn.setEnabled(True)
        self.frame_widgets[frame_number - 1].image_label.setText(lang_manager.tr("status_generate_failed"))
        QMessageBox.critical(self, lang_manager.tr("error"), lang_manager.tr("msg_regenerate_failed").format(frame_number, error))
    
    def replace_frame(self, frame_number: int):
        """替换分镜图片"""
        if not self.current_project or not self.current_project.id:
            return
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            lang_manager.tr("title_replace_frame").format(frame_number),
            "",
            lang_manager.tr("dialog_filter_images")
        )
        
        if file_path:
            try:
                import shutil
                episode = self.episode_combo.currentIndex() + 1
                frames_dir = os.path.join(self.db_manager.get_project_path(self.current_project.id), "frames", f"ep_{episode}")
                os.makedirs(frames_dir, exist_ok=True)
                frame_path = os.path.join(frames_dir, f"frame_{frame_number}.png")
                
                shutil.copy2(file_path, frame_path)
                self.frame_widgets[frame_number - 1].set_image(frame_path)
                QMessageBox.information(self, lang_manager.tr("success"), lang_manager.tr("msg_replace_success"))
                self.check_episode_frames_generated()
            except Exception as e:
                QMessageBox.critical(self, lang_manager.tr("error"), lang_manager.tr("msg_replace_failed").format(str(e)))
    
    def export_grid(self):
        """导出六宫格"""
        if not self.current_project or not self.current_project.id:
            return
        
        episode = self.episode_combo.currentIndex() + 1
        frames_dir = os.path.join(self.db_manager.get_project_path(self.current_project.id), "frames", f"ep_{episode}")
        # 获取6张图片
        image_paths = [os.path.join(frames_dir, f"frame_{i+1}.png") for i in range(6)]
        
        # 检查所有图片是否存在
        if not all(os.path.exists(p) for p in image_paths):
            QMessageBox.warning(self, lang_manager.tr("warning"), lang_manager.tr("msg_export_grid_warning"))
            return
        
        # 选择保存路径
        save_path, _ = QFileDialog.getSaveFileName(
            self,
            lang_manager.tr("title_save_grid"),
            f"{self.current_project.name}_ep{episode}{lang_manager.tr('filename_suffix_grid')}.png",
            lang_manager.tr("dialog_filter_png")
        )
        
        if save_path:
            try:
                # 获取分镜文字
                frame_texts = [lang_manager.tr("status_reference_image")]
                prompts_text = self.prompts_edit.toPlainText().strip()
                prompts = [p.strip() for p in prompts_text.split('\n') if p.strip()]
                
                # prompts 对应 frame 2, 3, 4, 5, 6
                for i in range(5):
                    if i < len(prompts):
                        prompt = prompts[i]
                        prefix = lang_manager.tr("frame_prefix").format(i+2)
                        text = f"{prefix}: {prompt[:30]}..." if len(prompt) > 30 else f"{prefix}: {prompt}"
                        frame_texts.append(text)
                    else:
                        frame_texts.append(lang_manager.tr("frame_prefix").format(i+2))
                
                # 调用ImageService生成六宫格
                # grid_size=3 (3列 x 2行)
                ImageService.create_grid_preview(image_paths, save_path, frame_texts, grid_size=3)
                QMessageBox.information(self, lang_manager.tr("success"), lang_manager.tr("msg_grid_exported").format(save_path))
            except Exception as e:
                QMessageBox.critical(self, lang_manager.tr("error"), lang_manager.tr("msg_export_failed").format(str(e)))
    
    def clear(self):
        """清空面板"""
        self.current_project = None
        self.generate_episode_btn.setEnabled(True)
        self.export_grid_btn.setEnabled(False)
        self.clear_episode_btn.setEnabled(True)
        
        for frame_widget in self.frame_widgets:
            frame_widget.clear_image()
