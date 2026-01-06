"""
项目信息编辑面板
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLineEdit, QTextEdit, QSpinBox, QComboBox,
                             QPushButton, QLabel, QFileDialog, QListWidget,
                             QMessageBox, QGroupBox, QListWidgetItem, QScrollArea)
from PyQt6.QtCore import pyqtSignal, Qt, QSize
from PyQt6.QtGui import QPixmap, QIcon
from src.models.database import DatabaseManager
from src.models.project import Project
from src.utils.language import lang_manager
import os
import shutil


class ProjectPanel(QWidget):
    """项目信息编辑面板"""
    
    project_saved = pyqtSignal(Project)
    
    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        self.db_manager = db_manager
        self.current_project = None
        self.reference_images = []
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        
        # 滚动内容容器
        scroll_content = QWidget()
        layout = QVBoxLayout(scroll_content)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)
        
        # 标题
        title = QLabel(lang_manager.tr("project_info_title"))
        title.setProperty("class", "title")
        layout.addWidget(title)
        
        # 创建水平布局容器，放置基础信息和参考图片
        content_hlayout = QHBoxLayout()
        content_hlayout.setSpacing(16)
        
        # 基础信息分组
        basic_group = QGroupBox(lang_manager.tr("basic_info_group"))
        basic_group.setStyleSheet("""
            QGroupBox {
                font-weight: 600;
                font-size: 14px;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 12px;
                padding: 0 8px;
                color: #374151;
            }
        """)
        basic_layout = QVBoxLayout()
        
        # 基础信息表单
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        form_layout.setContentsMargins(16, 16, 16, 16)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        
        self.name_input = QLineEdit()
        self.name_input.setAlignment(Qt.AlignmentFlag.AlignLeft)
        form_layout.addRow(lang_manager.tr("project_name_label"), self.name_input)
        
        self.type_combo = QComboBox()
        self.type_combo.addItems([lang_manager.tr("type_ad"), lang_manager.tr("type_promo")])
        form_layout.addRow(lang_manager.tr("project_type_label"), self.type_combo)
        
        self.product_input = QLineEdit()
        self.product_input.setAlignment(Qt.AlignmentFlag.AlignLeft)
        form_layout.addRow(lang_manager.tr("product_name_label"), self.product_input)
        
        self.company_input = QLineEdit()
        self.company_input.setAlignment(Qt.AlignmentFlag.AlignLeft)
        form_layout.addRow(lang_manager.tr("company_name_label"), self.company_input)
        
        self.audience_input = QLineEdit()
        self.audience_input.setAlignment(Qt.AlignmentFlag.AlignLeft)
        form_layout.addRow(lang_manager.tr("target_audience_label"), self.audience_input)
        
        self.duration_input = QSpinBox()
        self.duration_input.setRange(5, 120)
        self.duration_input.setValue(15)
        self.duration_input.setSuffix(lang_manager.tr("seconds_suffix"))
        form_layout.addRow(lang_manager.tr("video_duration_label"), self.duration_input)
        
        self.style_combo = QComboBox()
        self.style_combo.addItems([
            lang_manager.tr("style_warm"), lang_manager.tr("style_modern"), 
            lang_manager.tr("style_tech"), lang_manager.tr("style_retro"), 
            lang_manager.tr("style_fashion"), lang_manager.tr("style_nature"), 
            lang_manager.tr("style_business"), lang_manager.tr("style_dynamic")
        ])
        form_layout.addRow(lang_manager.tr("video_style_label"), self.style_combo)
        
        self.keywords_input = QTextEdit()
        self.keywords_input.setPlaceholderText(lang_manager.tr("keywords_placeholder"))
        self.keywords_input.setMaximumHeight(80)
        form_layout.addRow(lang_manager.tr("core_selling_points_label"), self.keywords_input)
        
        # 配音设置
        self.voice_tone_combo = QComboBox()
        self.voice_tone_combo.addItems([
            lang_manager.tr("voice_male_calm"), lang_manager.tr("voice_female_gentle"), 
            lang_manager.tr("voice_male_dynamic"), lang_manager.tr("voice_female_sweet"), 
            lang_manager.tr("voice_female_mature"), lang_manager.tr("voice_male_magnetic"), 
            lang_manager.tr("voice_child"), lang_manager.tr("voice_custom")
        ])
        self.voice_tone_combo.setEditable(True)  # 允许自定义
        form_layout.addRow(lang_manager.tr("voice_tone_label"), self.voice_tone_combo)
        
        self.voice_speed_combo = QComboBox()
        self.voice_speed_combo.addItems([
            lang_manager.tr("speed_slow"), lang_manager.tr("speed_medium"), lang_manager.tr("speed_fast")
        ])
        self.voice_speed_combo.setEditable(True)
        form_layout.addRow(lang_manager.tr("voice_speed_label"), self.voice_speed_combo)
        
        basic_layout.addLayout(form_layout)
        basic_group.setLayout(basic_layout)
        content_hlayout.addWidget(basic_group, 1)
        
        # 参考图片区域
        image_group = QGroupBox(lang_manager.tr("ref_images_group"))
        image_group.setStyleSheet("""
            QGroupBox {
                font-weight: 600;
                font-size: 14px;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 12px;
                padding: 0 8px;
                color: #64748b;
            }
        """)
        image_layout = QVBoxLayout()
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        
        self.add_image_btn = QPushButton(lang_manager.tr("add_image_btn"))
        self.add_image_btn.clicked.connect(self.add_images)
        btn_layout.addWidget(self.add_image_btn)
        
        self.remove_image_btn = QPushButton(lang_manager.tr("remove_image_btn"))
        from .styles import apply_button_property
        apply_button_property(self.remove_image_btn, "secondary")
        self.remove_image_btn.clicked.connect(self.remove_image)
        btn_layout.addWidget(self.remove_image_btn)
        
        self.clear_images_btn = QPushButton(lang_manager.tr("clear_images_btn"))
        apply_button_property(self.clear_images_btn, "danger")
        self.clear_images_btn.clicked.connect(self.clear_images)
        btn_layout.addWidget(self.clear_images_btn)
        
        btn_layout.addStretch()
        image_layout.addLayout(btn_layout)
        
        self.image_list = QListWidget()
        self.image_list.setMinimumHeight(180)
        self.image_list.setMaximumHeight(220)
        self.image_list.setIconSize(QSize(140, 140))  # 设置缩略图大小
        self.image_list.setViewMode(QListWidget.ViewMode.IconMode)  # 图标模式
        self.image_list.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.image_list.setSpacing(12)
        self.image_list.setWordWrap(True)
        self.image_list.setTextElideMode(Qt.TextElideMode.ElideMiddle)  # 文本省略模式
        self.image_list.setUniformItemSizes(False)  # 允许不同大小的项
        self.image_list.setGridSize(QSize(160, 180))  # 设置网格大小以容纳图标和文本
        image_layout.addWidget(self.image_list)
        
        image_group.setLayout(image_layout)
        content_hlayout.addWidget(image_group, 1)
        
        # 将水平布局添加到主布局
        layout.addLayout(content_hlayout)
        layout.addStretch()
        
        # 设置滚动区域
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)
        
        # 保存按钮 - 固定在底部
        save_btn_layout = QHBoxLayout()
        save_btn_layout.setContentsMargins(24, 12, 24, 16)
        save_btn_layout.addStretch()
        
        self.save_btn = QPushButton(lang_manager.tr("save_project_btn"))
        from .styles import apply_button_property
        apply_button_property(self.save_btn, "success")
        self.save_btn.clicked.connect(self.save_project)
        self.save_btn.setMinimumWidth(150)
        self.save_btn.setMinimumHeight(44)
        save_btn_layout.addWidget(self.save_btn)
        
        main_layout.addLayout(save_btn_layout)

        
    def load_project(self, project: Project):
        """加载项目数据"""
        self.current_project = project
        
        self.name_input.setText(project.name)
        self.type_combo.setCurrentText(project.type)
        self.product_input.setText(project.product_name)
        self.company_input.setText(project.company_name)
        self.audience_input.setText(project.target_audience)
        self.duration_input.setValue(project.duration)
        self.style_combo.setCurrentText(project.style)
        self.keywords_input.setText(project.keywords)
        
        # 加载参考图片
        self.reference_images = []
        self.image_list.clear()
        
        if project.id:
            images_dir = os.path.join(self.db_manager.get_project_path(project.id), "images")
            print(f"[Debug] 加载项目参考图，目录: {images_dir}")
            
            if os.path.exists(images_dir):
                image_files = sorted([f for f in os.listdir(images_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
                print(f"[Debug] 找到 {len(image_files)} 个图片文件")
                
                for filename in image_files:
                    img_path = os.path.join(images_dir, filename)
                    self.reference_images.append(img_path)
                    
                    # 创建带缩略图的列表项
                    # 截断过长的文件名
                    if len(filename) > 20:
                        display_name = filename[:17] + "..."
                    else:
                        display_name = filename
                    
                    item = QListWidgetItem(display_name)
                    item.setToolTip(filename)  # 完整文件名作为提示
                    
                    # 加载并缩放图片作为图标
                    print(f"[Debug] 加载图片: {img_path}")
                    pixmap = QPixmap(img_path)
                    
                    if not pixmap.isNull():
                        print(f"[Debug] 图片尺寸: {pixmap.width()}x{pixmap.height()}")
                        scaled_pixmap = pixmap.scaled(
                            140, 140,
                            Qt.AspectRatioMode.KeepAspectRatio,
                            Qt.TransformationMode.SmoothTransformation
                        )
                        print(f"[Debug] 缩放后尺寸: {scaled_pixmap.width()}x{scaled_pixmap.height()}")
                        
                        icon = QIcon(scaled_pixmap)
                        item.setIcon(icon)
                        
                        # 验证图标是否设置成功
                        if not item.icon().isNull():
                            print(f"[Debug] 图标设置成功: {filename}")
                        else:
                            print(f"[Debug] 图标设置失败: {filename}")
                    else:
                        print(f"[Debug] 无法加载图片: {filename}")
                    
                    self.image_list.addItem(item)
            else:
                print(f"[Debug] 图片目录不存在: {images_dir}")
    
    def add_images(self):
        """添加参考图片"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            lang_manager.tr("select_ref_images"),
            "",
            lang_manager.tr("dialog_filter_images")
        )
        
        if files:
            for file_path in files:
                if file_path not in self.reference_images:
                    self.reference_images.append(file_path)
                    
                    # 创建带缩略图的列表项
                    filename = os.path.basename(file_path)
                    # 截断过长的文件名
                    if len(filename) > 20:
                        display_name = filename[:17] + "..."
                    else:
                        display_name = filename
                    
                    item = QListWidgetItem(display_name)
                    item.setToolTip(filename)  # 完整文件名作为提示
                    
                    # 加载并缩放图片作为图标
                    print(f"[Debug] 添加图片: {file_path}")
                    pixmap = QPixmap(file_path)
                    
                    if not pixmap.isNull():
                        print(f"[Debug] 图片尺寸: {pixmap.width()}x{pixmap.height()}")
                        scaled_pixmap = pixmap.scaled(
                            140, 140,
                            Qt.AspectRatioMode.KeepAspectRatio,
                            Qt.TransformationMode.SmoothTransformation
                        )
                        print(f"[Debug] 缩放后尺寸: {scaled_pixmap.width()}x{scaled_pixmap.height()}")
                        
                        icon = QIcon(scaled_pixmap)
                        item.setIcon(icon)
                        
                        # 验证图标是否设置成功
                        if not item.icon().isNull():
                            print(f"[Debug] 图标设置成功")
                        else:
                            print(f"[Debug] 图标设置失败")
                    else:
                        print(f"[Debug] 无法加载图片: {file_path}")
                    
                    self.image_list.addItem(item)
    
    def remove_image(self):
        """删除选中的图片"""
        current_row = self.image_list.currentRow()
        if current_row >= 0:
            reply = QMessageBox.question(
                self,
                lang_manager.tr("msg_confirm_delete"),
                lang_manager.tr("confirm_delete_image_msg"),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.reference_images.pop(current_row)
                self.image_list.takeItem(current_row)
    
    def clear_images(self):
        """清空所有图片"""
        if not self.reference_images:
            return
            
        reply = QMessageBox.question(
            self,
            lang_manager.tr("confirm_clear"),
            lang_manager.tr("confirm_clear_images_msg").format(len(self.reference_images)),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.reference_images.clear()
            self.image_list.clear()
    
    def save_project(self):
        """保存项目"""
        # 验证必填字段
        if not self.name_input.text().strip():
            QMessageBox.warning(self, lang_manager.tr("warning"), lang_manager.tr("msg_enter_project_name"))
            return
        
        # 如果没有当前项目，创建新项目
        if not self.current_project:
            from src.models.project import Project
            self.current_project = Project(
                name="",
                type=lang_manager.tr("type_ad")
            )
        
        # 更新项目数据
        self.current_project.name = self.name_input.text().strip()
        self.current_project.type = self.type_combo.currentText()
        self.current_project.product_name = self.product_input.text().strip()
        self.current_project.company_name = self.company_input.text().strip()
        self.current_project.target_audience = self.audience_input.text().strip()
        self.current_project.duration = self.duration_input.value()
        self.current_project.style = self.style_combo.currentText()
        self.current_project.keywords = self.keywords_input.toPlainText().strip()
        self.current_project.voice_tone = self.voice_tone_combo.currentText().strip()
        self.current_project.voice_speed = self.voice_speed_combo.currentText().strip()
        
        try:
            # 保存到数据库
            if self.current_project.id:
                self.db_manager.update_project(self.current_project)
            else:
                project_id = self.db_manager.create_project(self.current_project)
                self.current_project.id = project_id
            
            # 保存参考图片
            if self.current_project.id and self.reference_images:
                images_dir = os.path.join(
                    self.db_manager.get_project_path(self.current_project.id),
                    "images"
                )
                os.makedirs(images_dir, exist_ok=True)
                
                # 清空原有图片
                for filename in os.listdir(images_dir):
                    os.remove(os.path.join(images_dir, filename))
                
                # 复制新图片
                for img_path in self.reference_images:
                    filename = os.path.basename(img_path)
                    dest_path = os.path.join(images_dir, filename)
                    if img_path != dest_path:  # 避免复制到自己
                        shutil.copy2(img_path, dest_path)
            
            QMessageBox.information(self, lang_manager.tr("success"), lang_manager.tr("msg_project_saved"))
            self.project_saved.emit(self.current_project)
            
        except Exception as e:
            QMessageBox.critical(self, lang_manager.tr("error"), lang_manager.tr("msg_save_failed").format(str(e)))

    
    def clear(self):
        """清空面板"""
        self.current_project = None
        self.name_input.clear()
        self.type_combo.setCurrentIndex(0)
        self.product_input.clear()
        self.company_input.clear()
        self.audience_input.clear()
        self.duration_input.setValue(15)
        self.style_combo.setCurrentIndex(0)
        self.keywords_input.clear()
        self.clear_images()
