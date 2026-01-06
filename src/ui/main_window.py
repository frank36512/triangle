"""
主窗口
"""
from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                             QListWidget, QPushButton, QStackedWidget, QLabel,
                             QMessageBox, QSplitter, QListWidgetItem, QDialog,
                             QTextBrowser, QDialogButtonBox)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QPixmap, QAction
from src.utils.language import lang_manager
from src.models.database import DatabaseManager
from src.models.project import Project
from .project_panel import ProjectPanel
from .prompt_panel import PromptPanel
from .frame_panel import FramePanel
from .video_panel import VideoPanel
from .settings_panel import SettingsPanel
from .help_panel import HelpPanel
from .styles import (GLOBAL_STYLE, PROJECT_LIST_STYLE, TAB_CONTAINER_STYLE,
                     apply_button_property, set_tab_active, COLORS)
import os


class MainWindow(QMainWindow):
    """主窗口类"""
    
    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager()
        self.current_project = None
        self.init_ui()
        self.load_projects()
        
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle(lang_manager.tr("app_name"))
        
        # 设置合理的初始窗口大小和位置
        from PyQt6.QtGui import QScreen
        from PyQt6.QtCore import QRect
        
        # 获取主屏幕的可用几何区域（排除任务栏等）
        screen = self.screen()
        if screen:
            available_geometry = screen.availableGeometry()
            
            # 设置窗口为屏幕的70%，确保不会太大
            width = min(1400, int(available_geometry.width() * 0.7))
            height = min(900, int(available_geometry.height() * 0.75))
            
            # 计算居中位置
            x = available_geometry.x() + (available_geometry.width() - width) // 2
            y = available_geometry.y() + (available_geometry.height() - height) // 2
            
            self.setGeometry(x, y, width, height)
        else:
            # 备选方案：使用固定大小
            self.setGeometry(100, 100, 1200, 800)
        
        # 设置最小窗口尺寸，确保界面不会太小
        self.setMinimumSize(1000, 700)
        
        # 应用全局样式
        self.setStyleSheet(GLOBAL_STYLE)
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QHBoxLayout(central_widget)
        
        # 创建分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左侧：项目列表区
        left_widget = self.create_project_list_panel()
        left_widget.setMinimumWidth(280)
        left_widget.setMaximumWidth(450)
        splitter.addWidget(left_widget)
        
        # 右侧：功能面板区
        right_widget = self.create_function_panels()
        splitter.addWidget(right_widget)
        
        # 设置分割比例 (1:4，左侧适中)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 4)
        
        main_layout.addWidget(splitter)
        
    def create_project_list_panel(self):
        """创建项目列表面板"""
        widget = QWidget()
        widget.setStyleSheet(PROJECT_LIST_STYLE)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # 标题
        title = QLabel(lang_manager.tr("project_list_title"))
        title.setProperty("class", "subtitle")
        layout.addWidget(title)
        
        # 项目列表
        self.project_list = QListWidget()
        self.project_list.setIconSize(QSize(60, 60))  # 设置图标大小
        self.project_list.setSpacing(6)  # 项目间距
        self.project_list.setWordWrap(True)
        self.project_list.itemClicked.connect(self.on_project_selected)
        layout.addWidget(self.project_list)
        
        # 按钮组
        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(8)
        
        self.new_project_btn = QPushButton(lang_manager.tr("btn_new_project"))
        apply_button_property(self.new_project_btn, "primary")
        self.new_project_btn.clicked.connect(self.create_new_project)
        self.new_project_btn.setShortcut("Ctrl+N")
        self.new_project_btn.setMinimumHeight(40)
        self.new_project_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: white;
                font-weight: 500;
                font-size: 14px;
                border-radius: 6px;
                padding: 8px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {COLORS['primary_dark']};
            }}
            QPushButton:pressed {{
                background-color: #1e3a8a;
            }}
        """)
        btn_layout.addWidget(self.new_project_btn)
        
        self.delete_project_btn = QPushButton(lang_manager.tr("btn_delete_project"))
        apply_button_property(self.delete_project_btn, "danger")
        self.delete_project_btn.clicked.connect(self.delete_project)
        self.delete_project_btn.setEnabled(False)
        self.delete_project_btn.setMinimumHeight(40)
        self.delete_project_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['danger']};
                color: white;
                font-weight: 500;
                font-size: 14px;
                border-radius: 6px;
                padding: 8px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {COLORS['danger_dark']};
            }}
            QPushButton:pressed {{
                background-color: #b91c1c;
            }}
            QPushButton:disabled {{
                background-color: #fca5a5;
                color: #fecaca;
            }}
        """)
        btn_layout.addWidget(self.delete_project_btn)
        
        self.refresh_btn = QPushButton(lang_manager.tr("btn_refresh_list"))
        apply_button_property(self.refresh_btn, "secondary")
        self.refresh_btn.clicked.connect(self.load_projects)
        self.refresh_btn.setMinimumHeight(40)
        self.refresh_btn.setShortcut("F5")
        self.refresh_btn.setStyleSheet("""
            QPushButton {{
                background-color: #64748b;
                color: white;
                font-weight: 500;
                font-size: 14px;
                border-radius: 6px;
                padding: 8px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: #475569;
            }}
            QPushButton:pressed {{
                background-color: #334155;
            }}
        """)
        btn_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(btn_layout)
        
        return widget
    
    def create_function_panels(self):
        """创建功能面板区"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 标签页切换按钮容器
        tab_container = QWidget()
        tab_container.setStyleSheet(TAB_CONTAINER_STYLE)
        tab_layout = QHBoxLayout(tab_container)
        tab_layout.setContentsMargins(16, 0, 16, 0)
        tab_layout.setSpacing(0)
        
        self.project_info_btn = QPushButton(lang_manager.tr("tab_project_info"))
        apply_button_property(self.project_info_btn, "tab")
        self.project_info_btn.clicked.connect(lambda: self.switch_panel(0))
        self.project_info_btn.setShortcut("Alt+1")
        self.project_info_btn.setToolTip(lang_manager.tr("tip_project_info"))
        tab_layout.addWidget(self.project_info_btn)
        
        self.prompt_btn = QPushButton(lang_manager.tr("tab_prompt_gen"))
        apply_button_property(self.prompt_btn, "tab")
        self.prompt_btn.clicked.connect(lambda: self.switch_panel(1))
        self.prompt_btn.setShortcut("Alt+2")
        self.prompt_btn.setToolTip(lang_manager.tr("tip_prompt_gen"))
        tab_layout.addWidget(self.prompt_btn)
        
        self.frame_btn = QPushButton(lang_manager.tr("tab_frame_gen"))
        apply_button_property(self.frame_btn, "tab")
        self.frame_btn.clicked.connect(lambda: self.switch_panel(2))
        self.frame_btn.setShortcut("Alt+3")
        self.frame_btn.setToolTip(lang_manager.tr("tip_frame_gen"))
        tab_layout.addWidget(self.frame_btn)
        
        self.video_btn = QPushButton(lang_manager.tr("tab_video_gen"))
        apply_button_property(self.video_btn, "tab")
        self.video_btn.clicked.connect(lambda: self.switch_panel(3))
        self.video_btn.setShortcut("Alt+4")
        self.video_btn.setToolTip(lang_manager.tr("tip_video_gen"))
        tab_layout.addWidget(self.video_btn)
        
        self.settings_btn = QPushButton(lang_manager.tr("tab_settings"))
        apply_button_property(self.settings_btn, "tab")
        self.settings_btn.clicked.connect(lambda: self.switch_panel(4))
        self.settings_btn.setShortcut("Alt+5")
        self.settings_btn.setToolTip(lang_manager.tr("tip_settings"))
        tab_layout.addWidget(self.settings_btn)
        
        self.help_btn = QPushButton(lang_manager.tr("tab_help"))
        apply_button_property(self.help_btn, "tab")
        self.help_btn.clicked.connect(lambda: self.switch_panel(5))
        self.help_btn.setShortcut("F1")
        self.help_btn.setToolTip(lang_manager.tr("tip_help"))
        tab_layout.addWidget(self.help_btn)
        
        tab_layout.addStretch()
        
        layout.addWidget(tab_container)
        
        # 堆叠面板
        self.stacked_widget = QStackedWidget()
        
        # 创建各功能面板
        self.project_panel = ProjectPanel(self.db_manager)
        self.project_panel.project_saved.connect(self.on_project_saved)
        self.stacked_widget.addWidget(self.project_panel)
        
        self.prompt_panel = PromptPanel(self.db_manager)
        self.prompt_panel.prompts_generated.connect(self.on_prompts_generated)
        self.stacked_widget.addWidget(self.prompt_panel)
        
        self.frame_panel = FramePanel(self.db_manager)
        self.stacked_widget.addWidget(self.frame_panel)
        
        self.video_panel = VideoPanel(self.db_manager)
        self.stacked_widget.addWidget(self.video_panel)
        
        self.settings_panel = SettingsPanel()
        self.stacked_widget.addWidget(self.settings_panel)
        
        self.help_panel = HelpPanel()
        self.stacked_widget.addWidget(self.help_panel)
        
        layout.addWidget(self.stacked_widget)
        
        # 初始状态：禁用功能面板
        self.enable_function_panels(False)
        
        return widget
    
    def switch_panel(self, index):
        """切换面板"""
        self.stacked_widget.setCurrentIndex(index)
        
        # 更新按钮样式
        buttons = [self.project_info_btn, self.prompt_btn, self.frame_btn, 
                  self.video_btn, self.settings_btn, self.help_btn]
        for i, btn in enumerate(buttons):
            set_tab_active(btn, i == index)
    
    def enable_function_panels(self, enabled: bool):
        """启用或禁用功能面板"""
        self.project_info_btn.setEnabled(enabled)
        self.prompt_btn.setEnabled(enabled)
        self.frame_btn.setEnabled(enabled)
        self.video_btn.setEnabled(enabled)
    
    def load_projects(self):
        """加载项目列表"""
        self.project_list.clear()
        projects = self.db_manager.get_all_projects()
        
        from datetime import datetime, timedelta
        today = datetime.now().date()
        
        for project in projects:
            # 格式化项目名称和信息 - 只显示日期
            create_date = project.create_time.date()
            date_str = project.create_time.strftime('%m-%d')
            item_text = f"{project.name}\n{project.type} | {date_str}"
            item = QListWidgetItem(item_text)
            
            # 检查是否过期（超过今天）
            if create_date < today:
                # 过期项目使用淡色
                item.setForeground(Qt.GlobalColor.gray)
            
            # 尝试加载参考图作为缩略图
            thumbnail_found = False
            if project.id:
                project_path = self.db_manager.get_project_path(project.id)
                print(f"[Debug] 项目路径: {project_path}")
                
                # 首先尝试加载images目录中的第一张图片
                images_dir = os.path.join(project_path, "images")
                print(f"[Debug] 图片目录: {images_dir}, 存在: {os.path.exists(images_dir)}")
                
                if os.path.exists(images_dir):
                    image_files = [f for f in os.listdir(images_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
                    print(f"[Debug] 找到图片文件: {image_files}")
                    
                    if image_files:
                        thumbnail_path = os.path.join(images_dir, image_files[0])
                        print(f"[Debug] 尝试加载缩略图: {thumbnail_path}")
                        
                        pixmap = QPixmap(thumbnail_path)
                        if not pixmap.isNull():
                            scaled_pixmap = pixmap.scaled(
                                60, 60,
                                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                                Qt.TransformationMode.SmoothTransformation
                            )
                            item.setIcon(QIcon(scaled_pixmap))
                            thumbnail_found = True
                            print(f"[Debug] 缩略图加载成功")
                        else:
                            print(f"[Debug] 缩略图加载失败: pixmap is null")
                
                # 如果没有找到，尝试reference图片
                if not thumbnail_found:
                    for ext in ['.jpg', '.png', '.jpeg']:
                        thumbnail_path = os.path.join(project_path, f"reference{ext}")
                        if os.path.exists(thumbnail_path):
                            print(f"[Debug] 找到reference图片: {thumbnail_path}")
                            pixmap = QPixmap(thumbnail_path)
                            if not pixmap.isNull():
                                scaled_pixmap = pixmap.scaled(
                                    60, 60,
                                    Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                                    Qt.TransformationMode.SmoothTransformation
                                )
                                item.setIcon(QIcon(scaled_pixmap))
                                thumbnail_found = True
                                print(f"[Debug] Reference缩略图加载成功")
                                break
            
            if not thumbnail_found:
                print(f"[Debug] 项目 {project.name} 未找到缩略图")
            
            # 保存项目ID到item的data中
            item.setData(Qt.ItemDataRole.UserRole, project.id)
            self.project_list.addItem(item)
    
    def on_project_selected(self, item):
        """项目被选中"""
        project_id = item.data(Qt.ItemDataRole.UserRole)
        self.current_project = self.db_manager.get_project(project_id)
        
        if self.current_project:
            print(f"\n{'='*60}")
            print(f"[主窗口] 加载项目: {self.current_project.name}")
            print(f"[主窗口] 项目ID: {self.current_project.id}")
            print(f"[主窗口] 项目类型: {self.current_project.type}")
            print(f"{'='*60}")
            
            # 启用功能面板
            self.enable_function_panels(True)
            self.delete_project_btn.setEnabled(True)
            
            # 加载项目数据到各面板
            print("[主窗口] 加载项目信息面板...")
            self.project_panel.load_project(self.current_project)
            print("[主窗口] 加载提示词生成面板...")
            self.prompt_panel.load_project(self.current_project)
            print("[主窗口] 加载分镜图片面板...")
            self.frame_panel.load_project(self.current_project)
            print("[主窗口] 加载视频生成面板...")
            self.video_panel.load_project(self.current_project)
            
            print("[主窗口] ✓ 项目加载完成\n")
            
            # 切换到项目信息面板
            self.switch_panel(0)
    
    def create_new_project(self):
        """创建新项目"""
        # 创建一个空项目
        new_project = Project(name=lang_manager.tr("default_project_name"))
        
        # 切换到项目信息面板进行编辑
        self.current_project = new_project
        self.project_panel.load_project(new_project)
        self.enable_function_panels(True)
        self.switch_panel(0)
    
    def delete_project(self):
        """删除项目"""
        if not self.current_project or not self.current_project.id:
            return
        
        reply = QMessageBox.question(
            self,
            lang_manager.tr("msg_confirm_delete"),
            lang_manager.tr("msg_delete_text").format(self.current_project.name),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.db_manager.delete_project(self.current_project.id)
                self.current_project = None
                self.load_projects()
                self.enable_function_panels(False)
                self.delete_project_btn.setEnabled(False)
                QMessageBox.information(self, lang_manager.tr("success"), lang_manager.tr("msg_project_deleted"))
            except Exception as e:
                QMessageBox.critical(self, lang_manager.tr("error"), f"{lang_manager.tr('error')}: {str(e)}")
    
    def on_project_saved(self, project: Project):
        """项目保存后的回调"""
        self.current_project = project
        self.load_projects()
        
        # 如果是新项目，选中它
        if project.id:
            for i in range(self.project_list.count()):
                item = self.project_list.item(i)
                if item.data(Qt.ItemDataRole.UserRole) == project.id:
                    self.project_list.setCurrentItem(item)
                    break
    
    def on_prompts_generated(self):
        """提示词生成后的回调"""
        # 刷新相关面板的数据，确保显示最新的提示词
        if self.current_project:
            self.frame_panel.load_project(self.current_project)
            self.video_panel.load_project(self.current_project)
            
        # 自动切换到分镜图片面板
        reply = QMessageBox.question(
            self,
            lang_manager.tr("msg_prompt_success_title"),
            lang_manager.tr("msg_prompt_success_text"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.switch_panel(2)
    
    def enable_function_panels(self, enabled: bool):
        """启用/禁用功能面板"""
        self.project_info_btn.setEnabled(enabled)
        self.prompt_btn.setEnabled(enabled)
        self.frame_btn.setEnabled(enabled)
        self.video_btn.setEnabled(enabled)
        
        if not enabled:
            # 清空各面板
            self.project_panel.clear()
