"""
视频生成和预览面板
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QMessageBox, QProgressBar, QTextEdit,
                             QComboBox, QFormLayout, QGroupBox, QFileDialog, QLineEdit,
                             QListWidget, QListWidgetItem, QSizePolicy, QDialog,
                             QDialogButtonBox, QAbstractItemView, QCheckBox)
from PyQt6.QtCore import pyqtSignal, QThread, Qt, QSize
from PyQt6.QtGui import QPixmap, QIcon, QColor, QBrush
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
from src.models.database import DatabaseManager
from src.models.project import Project
from src.services.video_service import VideoService
from src.services.image_service import ImageService
from src.utils.config import Config
import os
import cv2
import re
import shutil


class VideoGenerationThread(QThread):
    """视频生成线程"""
    
    progress = pyqtSignal(str)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, video_service: VideoService, video_prompt: str, frame_images: list,
                 output_path: str, duration: int, resolution: str, fps: int, grid_image: str = None):
        super().__init__()
        self.video_service = video_service
        self.video_prompt = video_prompt
        self.frame_images = frame_images
        self.output_path = output_path
        self.duration = duration
        self.resolution = resolution
        self.fps = fps
        self.grid_image = grid_image
    
    def run(self):
        """执行生成任务"""
        try:
            video_path = self.video_service.generate_video(
                self.video_prompt,
                self.frame_images,
                self.output_path,
                self.duration,
                self.resolution,
                self.fps,
                self.grid_image,
                progress_callback=self.progress.emit
            )
            self.finished.emit(video_path)
        except Exception as e:
            self.error.emit(str(e))


class VideoMergeThread(QThread):
    """视频合并线程"""
    
    progress = pyqtSignal(str)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, video_service: VideoService, video_paths: list, output_path: str, subtitle_map: dict = None):
        super().__init__()
        self.video_service = video_service
        self.video_paths = video_paths
        self.output_path = output_path
        self.subtitle_map = subtitle_map
        
    def run(self):
        """执行合并任务"""
        try:
            video_path = self.video_service.merge_videos(
                self.video_paths,
                self.output_path,
                subtitle_map=self.subtitle_map,
                progress_callback=self.progress.emit
            )
            self.finished.emit(video_path)
        except Exception as e:
            self.error.emit(str(e))


from src.utils.language import lang_manager

class VideoSelectionDialog(QDialog):
    """视频选择对话框"""
    
    def __init__(self, video_files, parent=None):
        super().__init__(parent)
        self.setWindowTitle(lang_manager.tr("select_videos_merge_title"))
        self.resize(600, 500)
        self.video_files = video_files
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # 说明标签
        info_label = QLabel(lang_manager.tr("merge_videos_instruction"))
        info_label.setStyleSheet("color: #666; font-weight: bold; margin-bottom: 5px;")
        layout.addWidget(info_label)
        
        # 列表控件
        self.list_widget = QListWidget()
        self.list_widget.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.list_widget.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.list_widget.setStyleSheet("""
            QListWidget {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #eee;
            }
        """)
        
        # 预处理：识别每集最新的视频
        latest_files = set()
        episode_map = {}
        import re
        
        for f in self.video_files:
            filename = os.path.basename(f)
            match = re.match(r"episode_(\d+)_", filename)
            if match:
                ep_num = int(match.group(1))
                if ep_num not in episode_map:
                    episode_map[ep_num] = f
                else:
                    if os.path.getctime(f) > os.path.getctime(episode_map[ep_num]):
                        episode_map[ep_num] = f
        
        latest_files = set(episode_map.values())
        
        # 智能排序：按集数排序
        def natural_sort_key(path):
            filename = os.path.basename(path)
            # Try to find episode number
            match = re.search(r'episode_(\d+)_', filename)
            if match:
                # Episodes go first (1, num)
                return (1, int(match.group(1)), filename)
            # Others go last (2, 0, filename)
            return (2, 0, filename)
            
        sorted_files = sorted(self.video_files, key=natural_sort_key)
        
        # 填充列表
        for video_path in sorted_files:
            filename = os.path.basename(video_path)
            
            # 创建列表项
            item = QListWidgetItem(filename)
            item.setData(Qt.ItemDataRole.UserRole, video_path)
            # 确保启用拖拽和选择
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsDragEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            
            # 如果是该集最新的，默认选中
            if video_path in latest_files:
                item.setCheckState(Qt.CheckState.Checked)
                # 高亮显示
                item.setForeground(QBrush(QColor("#000000")))
                item.setBackground(QBrush(QColor("#f0f9ff")))
            else:
                item.setCheckState(Qt.CheckState.Unchecked)
                item.setForeground(QBrush(QColor("#666666")))
            
            self.list_widget.addItem(item)
            
        layout.addWidget(self.list_widget)

        # 选项区域
        options_layout = QHBoxLayout()
        self.subtitle_checkbox = QCheckBox(lang_manager.tr("generate_subtitles_option"))
        self.subtitle_checkbox.setToolTip(lang_manager.tr("generate_subtitles_tooltip"))
        options_layout.addWidget(self.subtitle_checkbox)
        options_layout.addStretch()
        layout.addLayout(options_layout)
        
        # 底部按钮
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
    def get_selected_files(self):
        """获取选中的文件列表（按列表顺序）"""
        selected = []
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                selected.append(item.data(Qt.ItemDataRole.UserRole))
        return selected

    def is_subtitle_enabled(self):
        """是否启用了字幕"""
        return self.subtitle_checkbox.isChecked()


class VideoPanel(QWidget):
    """视频生成面板"""
    
    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        self.db_manager = db_manager
        self.current_project = None
        self.generation_thread = None
        self.media_player = None
        self.audio_output = None
        self.selected_grid_image_path = None  # 当前选中的参考图路径
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # === 左侧和中间区域 ===
        center_widget = QWidget()
        center_layout = QVBoxLayout(center_widget)
        center_layout.setContentsMargins(24, 24, 24, 24)
        center_layout.setSpacing(20)
        
        # 视频预览区域（包含视频列表和播放器）
        preview_container = QHBoxLayout()
        
        # 左侧：视频列表
        video_list_group = QGroupBox(lang_manager.tr("generated_videos_group"))
        video_list_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e5e7eb;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 12px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
                color: #1f2937;
                background-color: transparent;
            }
        """)
        video_list_layout = QVBoxLayout()
        
        self.video_list_widget = QListWidget()
        # Removed fixed maximum width for adaptive display
        self.video_list_widget.setMinimumWidth(150)
        self.video_list_widget.setIconSize(QSize(180, 100))
        self.video_list_widget.setSpacing(12)
        self.video_list_widget.setViewMode(QListWidget.ViewMode.IconMode)
        self.video_list_widget.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.video_list_widget.setGridSize(QSize(190, 140))
        self.video_list_widget.setWordWrap(True)
        self.video_list_widget.itemClicked.connect(self.on_video_selected)
        self.video_list_widget.setStyleSheet("""
            QListWidget {
                border: none;
                background-color: transparent;
                color: #1f2937;
            }
            QListWidget::item {
                border: 1px solid #e5e7eb;
                border-radius: 4px;
                background-color: white;
                margin: 2px;
                color: #1f2937;
            }
            QListWidget::item:selected {
                border: 2px solid #2563eb;
                background-color: #eff6ff;
                color: #1f2937;
            }
        """)
        video_list_layout.addWidget(self.video_list_widget)
        
        video_list_group.setLayout(video_list_layout)
        preview_container.addWidget(video_list_group, 1)
        
        # 右侧：视频播放器
        preview_group = QGroupBox(lang_manager.tr("video_preview_group"))
        preview_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e5e7eb;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 12px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
                color: #1f2937;
                background-color: transparent;
            }
        """)
        preview_layout = QVBoxLayout()
        
        # 视频播放器
        self.video_widget = QVideoWidget()
        self.video_widget.setMinimumHeight(200)
        self.video_widget.setMinimumWidth(250)
        # 移除固定最大高度，让视频区域可以自适应
        self.video_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.video_widget.setStyleSheet("""
            QVideoWidget {
                border: none;
                background-color: #000000;
            }
        """)
        preview_layout.addWidget(self.video_widget)
        
        # 播放控制
        player_control_layout = QHBoxLayout()
        
        # 简洁的播放控制按钮样式
        control_btn_style = """
            QPushButton {
                background-color: #f3f4f6;
                border: 1px solid #d1d5db;
                border-radius: 4px;
                padding: 4px 12px;
                color: #374151;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #e5e7eb;
                border-color: #9ca3af;
            }
            QPushButton:pressed {
                background-color: #d1d5db;
            }
            QPushButton:disabled {
                background-color: #f9fafb;
                color: #9ca3af;
                border-color: #e5e7eb;
            }
        """
        
        self.play_btn = QPushButton(lang_manager.tr("play_btn"))
        self.play_btn.clicked.connect(self.play_video)
        self.play_btn.setEnabled(False)
        self.play_btn.setMaximumWidth(70)
        self.play_btn.setStyleSheet(control_btn_style)
        player_control_layout.addWidget(self.play_btn)
        
        self.pause_btn = QPushButton(lang_manager.tr("pause_btn"))
        self.pause_btn.clicked.connect(self.pause_video)
        self.pause_btn.setEnabled(False)
        self.pause_btn.setMaximumWidth(70)
        self.pause_btn.setStyleSheet(control_btn_style)
        player_control_layout.addWidget(self.pause_btn)
        
        self.stop_btn = QPushButton(lang_manager.tr("stop_btn"))
        self.stop_btn.clicked.connect(self.stop_video)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setMaximumWidth(70)
        self.stop_btn.setStyleSheet(control_btn_style)
        player_control_layout.addWidget(self.stop_btn)
        
        player_control_layout.addStretch()
        
        self.video_info_label = QLabel()
        player_control_layout.addWidget(self.video_info_label)
        
        preview_layout.addLayout(player_control_layout)
        preview_group.setLayout(preview_layout)
        preview_container.addWidget(preview_group, 3)
        
        # 视频预览区域占据更多比例 (例如 3:2)
        center_layout.addLayout(preview_container, 3)
        
        # 中间下部：提示词和九宫格（并排显示）
        bottom_layout = QHBoxLayout()
        
        # 视频提示词预览
        prompt_group = QGroupBox(lang_manager.tr("video_script_group"))
        prompt_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e5e7eb;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 12px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
                color: #1f2937;
                background-color: transparent;
            }
        """)
        prompt_layout = QVBoxLayout()
        
        # 分集选择
        segment_layout = QHBoxLayout()
        segment_layout.addWidget(QLabel(lang_manager.tr("select_episode_label")))
        self.segment_combo = QComboBox()
        self.segment_combo.addItem(lang_manager.tr("full_script_option"), -1)
        self.segment_combo.currentIndexChanged.connect(self.on_segment_changed)
        segment_layout.addWidget(self.segment_combo)
        segment_layout.addStretch()
        prompt_layout.addLayout(segment_layout)
        
        self.prompt_preview = QTextEdit()
        self.prompt_preview.setReadOnly(False)  # 允许用户编辑提示词
        self.prompt_preview.setPlaceholderText(lang_manager.tr("video_prompt_input_placeholder"))
        self.prompt_preview.setMinimumHeight(120)
        # 移除最大高度限制，允许垂直扩展
        self.prompt_preview.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        prompt_layout.addWidget(self.prompt_preview)
        
        prompt_group.setLayout(prompt_layout)
        bottom_layout.addWidget(prompt_group, 1)
        
        # 六宫格参考图预览
        grid_group = QGroupBox(lang_manager.tr("grid_reference_group"))
        grid_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e5e7eb;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 12px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
                color: #1f2937;
                background-color: transparent;
            }
        """)
        grid_layout = QVBoxLayout()
        
        # Create horizontal container for side-by-side display
        grid_content_layout = QHBoxLayout()
        
        # 左侧：参考图列表
        self.grid_list_widget = QListWidget()
        self.grid_list_widget.setViewMode(QListWidget.ViewMode.IconMode)
        self.grid_list_widget.setIconSize(QSize(100, 80))
        self.grid_list_widget.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.grid_list_widget.setSpacing(5)
        self.grid_list_widget.setMaximumWidth(220)  # Limit width for side panel
        self.grid_list_widget.itemClicked.connect(self.on_grid_selected)
        self.grid_list_widget.setStyleSheet("""
            QListWidget {
                border: 1px solid #e5e7eb;
                border-radius: 4px;
                background-color: #f9fafb;
            }
            QListWidget::item {
                border: 1px solid transparent;
                border-radius: 4px;
                padding: 2px;
            }
            QListWidget::item:selected {
                border: 2px solid #2563eb;
                background-color: #eff6ff;
            }
        """)
        grid_content_layout.addWidget(self.grid_list_widget)
        
        # 右侧：大图预览
        self.grid_image_label = QLabel()
        self.grid_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.grid_image_label.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc;")
        self.grid_image_label.setMinimumSize(200, 200)
        # 移除最大高度限制，让图片可以完整显示
        self.grid_image_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.grid_image_label.setScaledContents(True)  # 允许自动缩放以适应窗口
        self.grid_image_label.setText(lang_manager.tr("no_reference_selected"))
        grid_content_layout.addWidget(self.grid_image_label, 1)
        
        grid_layout.addLayout(grid_content_layout)
        
        # 底部：上传按钮
        self.upload_grid_btn = QPushButton(lang_manager.tr("upload_grid_btn"))
        self.upload_grid_btn.clicked.connect(self.upload_grid_image)
        from .styles import apply_button_property
        apply_button_property(self.upload_grid_btn, "secondary")
        grid_layout.addWidget(self.upload_grid_btn)
        
        grid_group.setLayout(grid_layout)
        bottom_layout.addWidget(grid_group, 1)
        
        center_layout.addLayout(bottom_layout, 1)
        
        # 进度条和状态
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 0)
        center_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel()
        self.status_label.setVisible(False)
        center_layout.addWidget(self.status_label)
        
        main_layout.addLayout(center_layout, 4)
        
        # === 右侧：设置区域 ===
        right_panel_widget = QWidget()
        right_panel_widget.setMinimumWidth(200)
        right_panel_widget.setMaximumWidth(220)  # 进一步缩小右侧面板宽度
        right_panel = QVBoxLayout(right_panel_widget)
        right_panel.setContentsMargins(5, 5, 5, 5)  # 减少边距
        
        # API选择区域
        api_group = QGroupBox(lang_manager.tr("video_api_group"))
        api_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e5e7eb;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 12px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
                color: #1f2937;
                background-color: transparent;
            }
        """)
        api_layout = QVBoxLayout()
        
        api_layout.addWidget(QLabel(lang_manager.tr("select_api_label")))
        self.api_provider_combo = QComboBox()
        self.refresh_api_list()
        api_layout.addWidget(self.api_provider_combo)
        
        api_group.setLayout(api_layout)
        right_panel.addWidget(api_group)
        
        # 生成参数设置
        params_group = QGroupBox(lang_manager.tr("generation_params_group"))
        params_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e5e7eb;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 12px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
                color: #1f2937;
                background-color: transparent;
            }
        """)
        params_layout = QFormLayout()
        
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems(["720p", "1080p", "4k"])
        self.resolution_combo.setCurrentText("1080p")
        params_layout.addRow(lang_manager.tr("resolution_label"), self.resolution_combo)
        
        self.fps_combo = QComboBox()
        self.fps_combo.addItems(["24", "30", "60"])
        self.fps_combo.setCurrentText("30")
        params_layout.addRow(lang_manager.tr("fps_label"), self.fps_combo)
        
        params_group.setLayout(params_layout)
        right_panel.addWidget(params_group)
        
        # 生成和保存按钮
        self.generate_btn = QPushButton(lang_manager.tr("generate_video_btn"))
        self.generate_btn.clicked.connect(self.generate_video)
        self.generate_btn.setMinimumHeight(44)
        right_panel.addWidget(self.generate_btn)
        
        self.save_btn = QPushButton(lang_manager.tr("save_video_btn"))
        from .styles import apply_button_property
        apply_button_property(self.save_btn, "success")
        self.save_btn.clicked.connect(self.save_video)
        self.save_btn.setEnabled(False)
        self.save_btn.setMinimumHeight(44)
        right_panel.addWidget(self.save_btn)

        self.merge_btn = QPushButton(lang_manager.tr("merge_videos_btn"))
        apply_button_property(self.merge_btn, "primary")
        self.merge_btn.clicked.connect(self.merge_videos)
        self.merge_btn.setMinimumHeight(44)
        right_panel.addWidget(self.merge_btn)
        
        right_panel.addStretch()
        
        # 添加中间区域到主布局
        main_layout.addWidget(center_widget, 1)
        
        # 添加右侧面板到主布局
        main_layout.addWidget(right_panel_widget)
        
        # 初始化媒体播放器
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        self.media_player.setVideoOutput(self.video_widget)
        
    def refresh_api_list(self):
        """刷新视频接口列表"""
        self.api_provider_combo.clear()
        config = Config()
        apis = config.get_video_apis()
        default_api = config.get_default_video_api()
        
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

    def parse_segments_from_text(self, text: str):
        """从提示词文本中解析分集信息"""
        try:
            segments = []
            # Split by 【第x集】
            pattern = r'(?=【第\d+集】)'
            parts = re.split(pattern, text)
            
            for part in parts:
                if not part.strip():
                    continue
                    
                # Extract episode number
                match = re.search(r'【第(\d+)集】', part)
                if match:
                    episode_num = int(match.group(1))
                    
                    # Extract duration if present
                    duration = 15
                    dur_match = re.search(r'【时长】\s*(\d+)', part)
                    if dur_match:
                        duration = int(dur_match.group(1))
                    
                    segments.append({
                        'episode': episode_num,
                        'duration': duration,
                        'prompt': part.strip()
                    })
            
            if segments:
                self.current_project.video_segments = segments
                print(lang_manager.tr("log_parse_segments_success").format(len(segments)))
        except Exception as e:
            print(lang_manager.tr("log_parse_segments_failed").format(e))

    def refresh_grid_list(self):
        """刷新九宫格/四宫格参考图列表"""
        self.grid_list_widget.clear()
        self.selected_grid_image_path = None
        self.grid_image_label.setText(lang_manager.tr("no_reference_selected"))
        
        if not self.current_project or not self.current_project.id:
            return
            
        frames_dir = os.path.join(
            self.db_manager.get_project_path(self.current_project.id),
            "frames"
        )
        
        # 确定分集目录
        episode = -1
        if self.segment_combo.currentIndex() > 0:
            episode = self.segment_combo.currentData()
            
        if episode != -1:
            frames_dir = os.path.join(frames_dir, f"ep_{episode}")
        
        if not os.path.exists(frames_dir):
            return
            
        # 1. 查找现有的 grid*.png
        import glob
        grid_files = glob.glob(os.path.join(frames_dir, "grid*.png"))
        
        # 2. 如果没有任何 grid 图片，尝试自动生成默认 grid.png
        if not grid_files:
            grid_path = os.path.join(frames_dir, "grid.png")
            # 检查是否有足够的分镜图片
            frame_images = []
            
            # 确定需要的图片数量
            required_count = 4 if episode != -1 else 9
            
            for i in range(required_count):
                frame_path = os.path.join(frames_dir, f"frame_{i+1}.png")
                if os.path.exists(frame_path):
                    frame_images.append(frame_path)
            
            if len(frame_images) >= required_count:
                try:
                    print(lang_manager.tr("log_auto_generate_grid_count").format(len(frame_images)))
                    # 获取分镜文字
                    frame_texts = [lang_manager.tr("status_reference_image")] if episode != -1 else []
                    
                    # 确定网格大小
                    grid_size = 2 if episode != -1 else 3
                    
                    ImageService.create_grid_preview(frame_images, grid_path, frame_texts, grid_size=grid_size)
                    grid_files.append(grid_path)
                except Exception as e:
                    print(lang_manager.tr("log_auto_generate_grid_failed").format(e))

        # 3. 填充列表
        for grid_path in sorted(grid_files, key=os.path.getmtime, reverse=True):
            filename = os.path.basename(grid_path)
            item = QListWidgetItem(filename)
            item.setData(Qt.ItemDataRole.UserRole, grid_path)
            item.setToolTip(filename)
            
            # 设置图标
            pixmap = QPixmap(grid_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(
                    100, 80,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                item.setIcon(QIcon(scaled_pixmap))
            
            self.grid_list_widget.addItem(item)
            
        # 默认选中第一个（最新的）
        if self.grid_list_widget.count() > 0:
            self.grid_list_widget.setCurrentRow(0)
            first_item = self.grid_list_widget.item(0)
            self.on_grid_selected(first_item)

    def upload_grid_image(self):
        """上传/添加参考图"""
        if not self.current_project or not self.current_project.id:
            return
            
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            lang_manager.tr("select_ref_images"),
            "",
            lang_manager.tr("dialog_filter_images")
        )
        
        if file_path:
            try:
                frames_dir = os.path.join(
                    self.db_manager.get_project_path(self.current_project.id),
                    "frames"
                )
                if not os.path.exists(frames_dir):
                    os.makedirs(frames_dir)
                    
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                target_filename = f"grid_custom_{timestamp}.png"
                target_path = os.path.join(frames_dir, target_filename)
                
                import shutil
                shutil.copy2(file_path, target_path)
                
                # 刷新列表
                self.refresh_grid_list()
                QMessageBox.information(self, lang_manager.tr("success"), lang_manager.tr("msg_grid_add_success"))
                
            except Exception as e:
                QMessageBox.critical(self, lang_manager.tr("error"), lang_manager.tr("msg_grid_add_failed").format(str(e)))

    def on_grid_selected(self, item):
        """参考图被选中"""
        grid_path = item.data(Qt.ItemDataRole.UserRole)
        self.selected_grid_image_path = grid_path
        self.load_grid_image(grid_path)
    
    def load_project(self, project: Project):
        """加载项目数据"""
        self.current_project = project
        
        # 尝试解析分集信息（如果缺少）
        if not project.video_segments and project.video_prompt:
             self.parse_segments_from_text(project.video_prompt)
        
        # 填充集数下拉框
        self.segment_combo.blockSignals(True)
        self.segment_combo.clear()
        self.segment_combo.addItem(lang_manager.tr("full_script_option"), -1)
        
        if project.video_segments:
            for segment in project.video_segments:
                ep = segment.get('episode', 0)
                duration = segment.get('duration', 15)
                self.segment_combo.addItem(lang_manager.tr("episode_combo_format").format(ep, duration), ep)
        
        self.segment_combo.blockSignals(False)
        
        # 检查是否有视频提示词
        if not project.video_prompt:
            self.generate_btn.setEnabled(False)
            QMessageBox.information(
                self,
                lang_manager.tr("info"),
                lang_manager.tr("msg_generate_video_prompt_first")
            )
        else:
            self.generate_btn.setEnabled(True)
            self.prompt_preview.setText(project.video_prompt)
            
        # 刷新九宫格列表和视频列表
        self.refresh_grid_list()
        self.load_video_list()
        
        # 触发一次分集变更以加载对应内容
        self.on_segment_changed(self.segment_combo.currentIndex())

    def on_segment_changed(self, index):
        """分集选择变更"""
        if index < 0 or not self.current_project:
            return
            
        data = self.segment_combo.currentData()
        
        if data == -1:
            # 完整脚本
            self.prompt_preview.setText(self.current_project.video_prompt)
        else:
            # 特定分集
            if self.current_project.video_segments:
                for segment in self.current_project.video_segments:
                    if segment.get('episode') == data:
                        self.prompt_preview.setText(segment.get('prompt', ''))
                        break
        
        # 检查是否已有生成的视频
        if self.current_project.id:
            video_dir = os.path.join(
                self.db_manager.get_project_path(self.current_project.id),
                "video"
            )
            
            target_video = None
            if os.path.exists(video_dir):
                import glob
                files = []
                if data == -1:
                    # 找最新的 video_*.mp4 或 output.mp4
                    files = glob.glob(os.path.join(video_dir, "video_*.mp4"))
                    if not files and os.path.exists(os.path.join(video_dir, "output.mp4")):
                         files.append(os.path.join(video_dir, "output.mp4"))
                else:
                    # 找最新的 episode_{data}_*.mp4
                    files = glob.glob(os.path.join(video_dir, f"episode_{data}_*.mp4"))
                
                if files:
                    # Sort by modification time
                    target_video = max(files, key=os.path.getctime)
            
            if target_video:
                self.load_video(target_video)
            
            # 刷新九宫格参考图列表
            self.refresh_grid_list()
            
            # 加载视频列表
            self.load_video_list()
    
    def load_video_list(self):
        """加载项目的视频列表"""
        if not self.current_project or not self.current_project.id:
            return
        
        self.video_list_widget.clear()
        video_dir = os.path.join(
            self.db_manager.get_project_path(self.current_project.id),
            "video"
        )
        
        if not os.path.exists(video_dir):
            return
        
        # 查找所有视频文件
        import glob
        video_files = glob.glob(os.path.join(video_dir, "*.mp4"))
        
        for video_path in sorted(video_files, reverse=True):  # 最新的在前
            # 获取文件名和创建时间
            filename = os.path.basename(video_path)
            file_time = os.path.getctime(video_path)
            from datetime import datetime
            time_str = datetime.fromtimestamp(file_time).strftime("%Y-%m-%d %H:%M")
            
            # 创建列表项 - 只显示日期和时间
            date_str = datetime.fromtimestamp(file_time).strftime("%m-%d %H:%M")
            list_item = QListWidgetItem(date_str)
            list_item.setData(Qt.ItemDataRole.UserRole, video_path)
            list_item.setToolTip(time_str)  # 完整时间显示在工具提示中
            list_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)  # 文字居中
            
            # 设置文字颜色为深色，确保可见
            from PyQt6.QtGui import QBrush, QColor
            list_item.setForeground(QBrush(QColor("#1f2937")))
            
            # 提取视频第一帧作为缩略图
            try:
                cap = cv2.VideoCapture(video_path)
                ret, frame = cap.read()
                if ret:
                    # 转换BGR到RGB
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    height, width, channel = frame_rgb.shape
                    bytes_per_line = 3 * width
                    from PyQt6.QtGui import QImage
                    q_image = QImage(frame_rgb.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
                    pixmap = QPixmap.fromImage(q_image)
                    
                    # 缩放缩略图
                    scaled_pixmap = pixmap.scaled(
                        180, 100,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    list_item.setIcon(QIcon(scaled_pixmap))
                cap.release()
            except Exception as e:
                print(f"[视频面板] 提取视频封面失败: {str(e)}")
            
            self.video_list_widget.addItem(list_item)
        
        print(f"[视频面板] 加载了 {len(video_files)} 个视频文件")
    
    def on_video_selected(self, item):
        """视频列表项被选中"""
        video_path = item.data(Qt.ItemDataRole.UserRole)
        print(lang_manager.tr("log_video_selected").format(video_path))
        
        # 停止当前播放
        if self.media_player:
            self.media_player.stop()
        
        # 加载新视频
        self.load_video(video_path)
    
    def load_grid_image(self, grid_path: str):
        """加载九宫格图片"""
        if os.path.exists(grid_path):
            pixmap = QPixmap(grid_path)
            # 直接设置图片，依靠setScaledContents(True)自适应大小
            self.grid_image_label.setPixmap(pixmap)
        else:
            self.grid_image_label.setText(lang_manager.tr("msg_grid_not_found"))
    
    def generate_video(self):
        """生成视频"""
        # 防止重复点击
        if not self.generate_btn.isEnabled():
            return
        
        if not self.current_project or not self.current_project.id:
            QMessageBox.warning(self, lang_manager.tr("warning"), lang_manager.tr("msg_save_project_first"))
            return
        
        if not self.current_project.video_prompt:
            QMessageBox.warning(self, lang_manager.tr("warning"), lang_manager.tr("msg_generate_video_prompt_first"))
            return
        
        # 确定当前分集
        episode = -1
        if self.segment_combo.currentIndex() > 0:
            episode = self.segment_combo.currentData()

        # 检查分镜图片
        project_path = self.db_manager.get_project_path(self.current_project.id)
        frames_dir = os.path.join(project_path, "frames")
        if episode != -1:
            frames_dir = os.path.join(frames_dir, f"ep_{episode}")

        required_count = 4 if episode != -1 else 9
        frame_images = [os.path.join(frames_dir, f"frame_{i+1}.png") for i in range(required_count)]
        
        if not all(os.path.exists(p) for p in frame_images):
            QMessageBox.warning(self, lang_manager.tr("warning"), lang_manager.tr("msg_generate_frames_first"))
            return
        
        # 确认生成
        reply = QMessageBox.question(
            self,
            lang_manager.tr("confirm_generate_title"),
            lang_manager.tr("confirm_generate_video_msg"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # 获取配置
        config = Config()
        
        # 根据接口名称获取配置
        selected_api_name = self.api_provider_combo.currentText()
        
        if selected_api_name == lang_manager.tr("no_api_configured"):
            QMessageBox.warning(self, lang_manager.tr("warning"), lang_manager.tr("msg_configure_video_api_first"))
            return
        
        video_config = config.get_video_api(selected_api_name)
        
        if not video_config or not video_config.get("api_key"):
            QMessageBox.warning(self, lang_manager.tr("warning"), lang_manager.tr("msg_api_config_incomplete").format(selected_api_name))
            return
        
        # 生成带时间戳的输出文件名（精确到毫秒）
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:17]  # 精确到毫秒
        
        if episode != -1:
            output_filename = f"episode_{episode}_{timestamp}.mp4"
        else:
            output_filename = f"video_{timestamp}.mp4"

        output_path = os.path.join(
            project_path,
            "video",
            output_filename
        )
        
        # 确保文件名唯一（理论上不会冲突，但做双重保护）
        if os.path.exists(output_path):
            import time
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f") + f"_{int(time.time() * 1000000) % 1000}"
            if episode != -1:
                output_filename = f"episode_{episode}_{timestamp}.mp4"
            else:
                output_filename = f"video_{timestamp}.mp4"
            output_path = os.path.join(
                project_path,
                "video",
                output_filename
            )
        
        # 创建视频服务
        video_service = VideoService(
            api_provider=video_config.get("provider", "sora"),
            api_key=video_config["api_key"],
            base_url=video_config.get("base_url", ""),
            model=video_config.get("model", "")
        )
        
        # 获取当前提示词和时长
        video_prompt = self.prompt_preview.toPlainText()
        if not video_prompt.strip():
             QMessageBox.warning(self, lang_manager.tr("warning"), lang_manager.tr("msg_prompt_empty"))
             return

        # 计算时长
        duration = 15 # 默认时长
        segment_data = self.segment_combo.currentData()
        if segment_data != -1 and self.current_project.video_segments:
            for segment in self.current_project.video_segments:
                if segment.get('episode') == segment_data:
                    duration = segment.get('duration', 15)
                    break
        
        # 确定参考图路径
        grid_image_path = self.selected_grid_image_path
        
        # 如果当前未选择有效的参考图，尝试自动生成默认九宫格
        if not grid_image_path or not os.path.exists(grid_image_path):
            try:
                default_grid_path = os.path.join(frames_dir, "grid.png")
                
                # 如果默认九宫格不存在，先生成
                if not os.path.exists(default_grid_path):
                    self.status_label.setText(lang_manager.tr("status_generating_grid"))
                    self.status_label.setVisible(True)
                    
                    # 获取分镜文字
                    frame_texts = [lang_manager.tr("status_reference_image")] if episode != -1 else []
                    
                    grid_size = 2 if episode != -1 else 3
                    ImageService.create_grid_preview(frame_images, default_grid_path, frame_texts, grid_size=grid_size)
                    
                if os.path.exists(default_grid_path):
                    grid_image_path = default_grid_path
                    # 刷新列表并选中
                    self.refresh_grid_list()
                    
            except Exception as e:
                print(f"生成默认参考图失败: {str(e)}")
                # 继续生成视频，即使参考图生成失败
        
        # 启动生成线程
        self.generate_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.status_label.setVisible(True)
        
        # 根据分集选择调整使用的图片
        # 即使选择了特定分集，也传入所有分镜图片，以便保持一致性
        # 但可以通过Prompt来指定关注的内容
        target_frame_images = frame_images
        target_grid_image = grid_image_path
        
        self.generation_thread = VideoGenerationThread(
            video_service,
            video_prompt,  # 使用文本框中的提示词
            target_frame_images,
            output_path,
            duration,  # 使用计算后的时长
            self.resolution_combo.currentText(),
            int(self.fps_combo.currentText()),
            target_grid_image
        )
        self.generation_thread.progress.connect(self.on_generation_progress)
        self.generation_thread.finished.connect(self.on_generation_finished)
        self.generation_thread.error.connect(self.on_generation_error)
        self.generation_thread.start()
    
    def on_generation_progress(self, status: str):
        """生成进度更新"""
        self.status_label.setText(status)
    
    def on_generation_finished(self, video_path: str):
        """生成完成"""
        self.progress_bar.setVisible(False)
        self.status_label.setVisible(False)
        self.generate_btn.setEnabled(True)
        
        QMessageBox.information(self, lang_manager.tr("success"), lang_manager.tr("msg_video_generated_success").format(video_path))
        
        # 刷新视频列表
        self.load_video_list()
        
        # 加载视频
        self.load_video(video_path)
    
    def on_generation_error(self, error_msg: str):
        """生成失败"""
        self.progress_bar.setVisible(False)
        self.status_label.setVisible(False)
        self.generate_btn.setEnabled(True)
        
        # 根据错误类型提供更明确的提示
        if "401" in error_msg or "Unauthorized" in error_msg:
            QMessageBox.critical(
                self, 
                lang_manager.tr("error_api_key_invalid_title"), 
                lang_manager.tr("msg_api_key_invalid").format(error_msg)
            )
        elif "403" in error_msg or "Forbidden" in error_msg:
            QMessageBox.critical(
                self, 
                lang_manager.tr("error_api_forbidden_title"), 
                lang_manager.tr("msg_api_forbidden").format(error_msg)
            )
        elif "404" in error_msg or "Not Found" in error_msg:
            QMessageBox.critical(
                self, 
                lang_manager.tr("error_api_not_found_title"), 
                lang_manager.tr("msg_api_not_found").format(error_msg)
            )
        else:
            QMessageBox.critical(self, lang_manager.tr("error"), lang_manager.tr("msg_video_generation_failed").format(error_msg))
    
    def load_video(self, video_path: str):
        """加载视频"""
        if os.path.exists(video_path):
            from PyQt6.QtCore import QUrl
            self.media_player.setSource(QUrl.fromLocalFile(video_path))
            
            # 获取视频信息
            video_info = VideoService.get_video_info(video_path)
            if video_info:
                info_text = (lang_manager.tr("video_info_format").format(
                           video_info.get('duration', 0),
                           video_info.get('width', 0),
                           video_info.get('height', 0),
                           video_info.get('fps', 0)))
                self.video_info_label.setText(info_text)
            
            # 启用播放控制
            self.play_btn.setEnabled(True)
            self.pause_btn.setEnabled(True)
            self.stop_btn.setEnabled(True)
            self.save_btn.setEnabled(True)
    
    def play_video(self):
        """播放视频"""
        self.media_player.play()
    
    def pause_video(self):
        """暂停视频"""
        self.media_player.pause()
    
    def stop_video(self):
        """停止视频"""
        self.media_player.stop()
    
    def save_video(self):
        """保存视频到指定位置"""
        if not self.current_project or not self.current_project.id:
            return
            
        # 获取当前播放的视频路径
        source_url = self.media_player.source()
        if source_url.isEmpty():
             QMessageBox.warning(self, lang_manager.tr("warning"), lang_manager.tr("msg_no_video_loaded"))
             return
             
        source_path = source_url.toLocalFile()
        
        if not os.path.exists(source_path):
            QMessageBox.warning(self, lang_manager.tr("warning"), lang_manager.tr("msg_video_file_not_found"))
            return
        
        save_path, _ = QFileDialog.getSaveFileName(
            self,
            lang_manager.tr("save_video_dialog_title"),
            f"{self.current_project.name}.mp4",
            "MP4视频 (*.mp4)"
        )
        
        if save_path:
            try:
                import shutil
                shutil.copy2(source_path, save_path)
                QMessageBox.information(self, lang_manager.tr("success"), lang_manager.tr("msg_video_saved_success").format(save_path))
            except Exception as e:
                QMessageBox.critical(self, lang_manager.tr("error"), lang_manager.tr("msg_video_save_failed").format(str(e)))
    
    def clear(self):
        """清空面板"""
        self.current_project = None
        self.prompt_preview.clear()
        self.generate_btn.setEnabled(False)
        self.save_btn.setEnabled(False)
        self.play_btn.setEnabled(False)
        self.pause_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        self.video_info_label.clear()
        
        if self.media_player:
            self.media_player.stop()

    def merge_videos(self):
        """合并所有分集视频"""
        if not self.current_project or not self.current_project.id:
            QMessageBox.warning(self, lang_manager.tr("warning"), lang_manager.tr("msg_save_project_first"))
            return
            
        # 防止重复点击
        if not self.merge_btn.isEnabled():
            return
            
        video_dir = os.path.join(
            self.db_manager.get_project_path(self.current_project.id),
            "video"
        )
        
        if not os.path.exists(video_dir):
            QMessageBox.warning(self, lang_manager.tr("warning"), lang_manager.tr("msg_video_dir_not_found"))
            return
            
        # 查找所有视频文件
        import glob
        all_videos = glob.glob(os.path.join(video_dir, "*.mp4"))
        
        # 过滤掉之前的合并结果（可选，防止递归合并）
        # 这里假设生成的视频是以 episode_ 开头，或者我们就列出所有让用户选
        candidate_videos = []
        for v in all_videos:
            filename = os.path.basename(v)
            # 排除以 merged_ 开头的文件，避免混淆，或者留给用户决定？
            # 用户可能想把之前的合并结果再合并？不太可能。
            # 安全起见，只列出 episode_ 开头的，或者是所有非 merged_ 的
            if not filename.startswith("merged_"):
                candidate_videos.append(v)
                
        if not candidate_videos:
            QMessageBox.warning(self, lang_manager.tr("warning"), lang_manager.tr("msg_no_videos_to_merge"))
            return
            
        # 弹出选择对话框
        dialog = VideoSelectionDialog(candidate_videos, self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
            
        selected_files = dialog.get_selected_files()
        
        if not selected_files:
            return
            
        if len(selected_files) < 2:
            reply = QMessageBox.question(
                self,
                lang_manager.tr("confirm_title"),
                lang_manager.tr("confirm_merge_single_video"),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
        
        # 处理字幕
        subtitle_map = None
        if dialog.is_subtitle_enabled():
            try:
                subtitle_map = self._extract_subtitles_for_videos(selected_files)
            except Exception as e:
                QMessageBox.warning(self, lang_manager.tr("warning"), lang_manager.tr("msg_subtitle_extract_failed").format(str(e)))
                subtitle_map = None

        # 准备输出路径
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"merged_video_{timestamp}.mp4"
        output_path = os.path.join(video_dir, output_filename)
        
        # 禁用按钮
        self.merge_btn.setEnabled(False)
        self.generate_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.status_label.setVisible(True)
        self.status_label.setText(lang_manager.tr("status_merging_videos"))
        
        # 启动线程
        # 只需要一个 VideoService 实例
        video_service = VideoService()
        
        self.merge_thread = VideoMergeThread(
            video_service,
            selected_files,
            output_path,
            subtitle_map
        )
        self.merge_thread.progress.connect(self.on_merge_progress)
        self.merge_thread.finished.connect(self.on_merge_finished)
        self.merge_thread.error.connect(self.on_merge_error)
        self.merge_thread.start()

    def _extract_subtitles_for_videos(self, video_files):
        """为选中的视频提取字幕信息"""
        if not self.current_project or not self.current_project.video_segments:
            return None
            
        subtitle_map = {}
        import re
        
        # 建立分集映射
        segment_map = {}
        for seg in self.current_project.video_segments:
            ep = seg.get('episode')
            if ep:
                segment_map[ep] = seg.get('prompt', '')
                
        for video_path in video_files:
            filename = os.path.basename(video_path)
            # 尝试从文件名提取集数
            match = re.search(r'episode_(\d+)_', filename)
            if not match:
                continue
                
            episode_num = int(match.group(1))
            prompt_text = segment_map.get(episode_num)
            
            if not prompt_text:
                continue
                
            # 解析字幕
            # 格式预期：0-3秒...；旁白：XXX
            subtitles = []
            lines = prompt_text.split('\n')
            for line in lines:
                # 匹配时间范围和旁白
                # 兼容多种格式：
                # 0-3秒（...）：...；旁白：内容
                # 0-3秒：... 旁白：内容
                
                # 1. 提取时间
                time_match = re.search(r'^(\d+)[-~](\d+)秒', line)
                if not time_match:
                    continue
                    
                start_sec = int(time_match.group(1))
                end_sec = int(time_match.group(2))
                
                # 2. 提取旁白
                narration_match = re.search(r'旁白[：:](.+)$', line)
                if narration_match:
                    content = narration_match.group(1).strip()
                    # 去除可能存在的【】或其他标记
                    content = re.sub(r'^【(.*?)】', r'\1', content)
                    content = content.strip()
                    
                    # 去除首尾标点符号
                    content = re.sub(r'^[，。！？、：；,.!?:;"\'“”‘’]+|[，。！？、：；,.!?:;"\'“”‘’]+$', '', content)
                    content = content.strip()
                    
                    if content and content != "【无】" and content != "无":
                        subtitles.append({
                            "start": start_sec,
                            "end": end_sec,
                            "text": content
                        })
            
            if subtitles:
                subtitle_map[video_path] = subtitles
                
        return subtitle_map
        
    def on_merge_progress(self, status: str):
        """合并进度"""
        self.status_label.setText(status)
        
    def on_merge_finished(self, video_path: str):
        """合并完成"""
        self.progress_bar.setVisible(False)
        self.status_label.setVisible(False)
        self.merge_btn.setEnabled(True)
        self.generate_btn.setEnabled(True)
        
        QMessageBox.information(self, lang_manager.tr("success"), lang_manager.tr("msg_video_merged_success"))
        
        # 刷新列表并加载
        self.load_video_list()
        self.load_video(video_path)
        
    def on_merge_error(self, error_msg: str):
        """合并失败"""
        self.progress_bar.setVisible(False)
        self.status_label.setVisible(False)
        self.merge_btn.setEnabled(True)
        self.generate_btn.setEnabled(True)
        
        QMessageBox.critical(self, lang_manager.tr("error"), lang_manager.tr("msg_merge_failed").format(error_msg))
