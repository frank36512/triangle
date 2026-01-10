"""
系统设置面板
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLineEdit, QComboBox, QPushButton, QLabel,
                             QGroupBox, QMessageBox, QTextEdit, QTabWidget,
                             QListWidget, QListWidgetItem)
from PyQt6.QtCore import Qt
from src.utils.config import Config
from src.utils.language import lang_manager


class SettingsPanel(QWidget):
    """系统设置面板"""
    
    def __init__(self):
        super().__init__()
        self.config = Config()
        self.init_ui()
        self.load_settings()
        
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # 标题
        title = QLabel(lang_manager.tr("settings_title"))
        title.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)
        
        # 标签页
        tab_widget = QTabWidget()
        
        # LLM API设置
        llm_tab = self.create_llm_settings_tab()
        tab_widget.addTab(llm_tab, lang_manager.tr("tab_llm_api"))
        
        # 图片生成API设置
        image_tab = self.create_image_settings_tab()
        tab_widget.addTab(image_tab, lang_manager.tr("tab_image_api"))
        
        # 视频生成API设置
        video_tab = self.create_video_settings_tab()
        tab_widget.addTab(video_tab, lang_manager.tr("tab_video_api"))
        
        # 通用设置
        general_tab = self.create_general_settings_tab()
        tab_widget.addTab(general_tab, lang_manager.tr("tab_general_settings"))
        
        layout.addWidget(tab_widget, 1)
        
        # 保存按钮 - 固定在底部
        save_btn_layout = QHBoxLayout()
        save_btn_layout.setContentsMargins(0, 12, 0, 0)
        save_btn_layout.addStretch()
        
        self.save_btn = QPushButton(lang_manager.tr("save_settings_btn"))
        self.save_btn.clicked.connect(self.save_settings)
        from .styles import apply_button_property
        apply_button_property(self.save_btn, "success")
        self.save_btn.setMinimumHeight(44)
        self.save_btn.setMinimumWidth(150)
        save_btn_layout.addWidget(self.save_btn)
        
        layout.addLayout(save_btn_layout, 0)
        
    def create_llm_settings_tab(self):
        """创建LLM设置标签页"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        
        # 左侧：接口列表
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel(lang_manager.tr("configured_apis").format("LLM")))
        
        self.llm_list = QListWidget()
        self.llm_list.itemClicked.connect(self.load_llm_api_config)
        left_layout.addWidget(self.llm_list)
        
        list_btn_layout = QHBoxLayout()
        add_llm_btn = QPushButton(lang_manager.tr("add_api_btn"))
        add_llm_btn.clicked.connect(self.add_new_llm_api)
        list_btn_layout.addWidget(add_llm_btn)
        
        del_llm_btn = QPushButton(lang_manager.tr("delete_api_btn"))
        del_llm_btn.clicked.connect(self.delete_llm_api)
        list_btn_layout.addWidget(del_llm_btn)
        left_layout.addLayout(list_btn_layout)
        
        layout.addLayout(left_layout, 1)
        
        # 右侧：接口配置表单
        right_layout = QVBoxLayout()
        
        group = QGroupBox(lang_manager.tr("api_config_group"))
        form_layout = QFormLayout()
        
        self.llm_name_input = QLineEdit()
        self.llm_name_input.setPlaceholderText(lang_manager.tr("api_name_placeholder").format("OpenAI / DeepSeek"))
        form_layout.addRow(lang_manager.tr("api_name_label"), self.llm_name_input)
        
        self.llm_provider_combo = QComboBox()
        self.llm_provider_combo.addItems(["openai", "deepseek", "wenxin", "tongyi", "custom"])
        form_layout.addRow(lang_manager.tr("api_provider_label"), self.llm_provider_combo)
        
        self.llm_model_input = QLineEdit()
        self.llm_model_input.setPlaceholderText(lang_manager.tr("api_model_placeholder").format("gpt-4o / deepseek-chat"))
        form_layout.addRow(lang_manager.tr("api_model_label"), self.llm_model_input)
        
        self.llm_api_key_input = QLineEdit()
        self.llm_api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.llm_api_key_input.setPlaceholderText(lang_manager.tr("api_key_placeholder"))
        form_layout.addRow(lang_manager.tr("api_key_label"), self.llm_api_key_input)
        
        self.llm_base_url_input = QLineEdit()
        self.llm_base_url_input.setPlaceholderText(lang_manager.tr("api_url_placeholder").format("https://api.openai.com/v1/chat/completions"))
        form_layout.addRow(lang_manager.tr("api_url_label"), self.llm_base_url_input)
        
        self.llm_is_default_combo = QComboBox()
        self.llm_is_default_combo.addItems([lang_manager.tr("no"), lang_manager.tr("yes")])
        form_layout.addRow(lang_manager.tr("set_default_label"), self.llm_is_default_combo)
        
        group.setLayout(form_layout)
        right_layout.addWidget(group)
        
        save_api_btn = QPushButton(lang_manager.tr("save_this_api_btn"))
        save_api_btn.clicked.connect(self.save_llm_api)
        right_layout.addWidget(save_api_btn)
        
        # 说明
        info = QLabel(lang_manager.tr("llm_info"))
        info.setWordWrap(True)
        info.setStyleSheet("color: #666; padding: 10px; font-size: 12px;")
        right_layout.addWidget(info)
        
        right_layout.addStretch()
        layout.addLayout(right_layout, 2)
        
        return widget

    
    def create_image_settings_tab(self):
        """创建图片生成设置标签页"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        
        # 左侧：接口列表
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel(lang_manager.tr("configured_apis").format(lang_manager.tr("tab_image_api").replace("API", "").strip())))
        
        self.image_list = QListWidget()
        self.image_list.itemClicked.connect(self.load_image_api_config)
        left_layout.addWidget(self.image_list)
        
        list_btn_layout = QHBoxLayout()
        add_image_btn = QPushButton(lang_manager.tr("add_api_btn"))
        add_image_btn.clicked.connect(self.add_new_image_api)
        list_btn_layout.addWidget(add_image_btn)
        
        del_image_btn = QPushButton(lang_manager.tr("delete_api_btn"))
        del_image_btn.clicked.connect(self.delete_image_api)
        list_btn_layout.addWidget(del_image_btn)
        left_layout.addLayout(list_btn_layout)
        
        layout.addLayout(left_layout, 1)
        
        # 右侧：接口配置表单
        right_layout = QVBoxLayout()
        
        group = QGroupBox(lang_manager.tr("api_config_group"))
        form_layout = QFormLayout()
        
        self.image_name_input = QLineEdit()
        self.image_name_input.setPlaceholderText(lang_manager.tr("api_name_placeholder").format("Flux / DALL-E"))
        form_layout.addRow(lang_manager.tr("api_name_label"), self.image_name_input)
        
        self.image_provider_combo = QComboBox()
        self.image_provider_combo.addItems(["stability", "openai", "midjourney", "flux", "custom"])
        form_layout.addRow(lang_manager.tr("api_provider_label"), self.image_provider_combo)
        
        self.image_model_input = QLineEdit()
        self.image_model_input.setPlaceholderText(lang_manager.tr("api_model_placeholder").format("dall-e-3 / flux-pro"))
        form_layout.addRow(lang_manager.tr("api_model_label"), self.image_model_input)
        
        self.image_api_key_input = QLineEdit()
        self.image_api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.image_api_key_input.setPlaceholderText(lang_manager.tr("api_key_placeholder"))
        form_layout.addRow(lang_manager.tr("api_key_label"), self.image_api_key_input)
        
        self.image_base_url_input = QLineEdit()
        self.image_base_url_input.setPlaceholderText(lang_manager.tr("api_url_placeholder").format(""))
        form_layout.addRow(lang_manager.tr("api_url_label"), self.image_base_url_input)
        
        self.image_is_default_combo = QComboBox()
        self.image_is_default_combo.addItems([lang_manager.tr("no"), lang_manager.tr("yes")])
        form_layout.addRow(lang_manager.tr("set_default_label"), self.image_is_default_combo)
        
        group.setLayout(form_layout)
        right_layout.addWidget(group)
        
        save_api_btn = QPushButton(lang_manager.tr("save_this_api_btn"))
        save_api_btn.clicked.connect(self.save_image_api)
        right_layout.addWidget(save_api_btn)
        
        # 说明
        info = QLabel(lang_manager.tr("image_info"))
        info.setWordWrap(True)
        info.setStyleSheet("color: #666; padding: 10px; font-size: 12px;")
        right_layout.addWidget(info)
        
        right_layout.addStretch()
        layout.addLayout(right_layout, 2)
        
        return widget

    
    def create_video_settings_tab(self):
        """创建视频生成设置标签页"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        
        # 左侧：接口列表
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel(lang_manager.tr("configured_apis").format(lang_manager.tr("tab_video_api").replace("API", "").strip())))
        
        self.video_list = QListWidget()
        self.video_list.itemClicked.connect(self.load_video_api_config)
        left_layout.addWidget(self.video_list)
        
        list_btn_layout = QHBoxLayout()
        add_video_btn = QPushButton(lang_manager.tr("add_api_btn"))
        add_video_btn.clicked.connect(self.add_new_video_api)
        list_btn_layout.addWidget(add_video_btn)
        
        del_video_btn = QPushButton(lang_manager.tr("delete_api_btn"))
        del_video_btn.clicked.connect(self.delete_video_api)
        list_btn_layout.addWidget(del_video_btn)
        left_layout.addLayout(list_btn_layout)
        
        layout.addLayout(left_layout, 1)
        
        # 右侧：接口配置表单
        right_layout = QVBoxLayout()
        
        group = QGroupBox(lang_manager.tr("api_config_group"))
        form_layout = QFormLayout()
        
        self.video_name_input = QLineEdit()
        self.video_name_input.setPlaceholderText(lang_manager.tr("api_name_placeholder").format("Luma / Runway"))
        form_layout.addRow(lang_manager.tr("api_name_label"), self.video_name_input)
        
        self.video_provider_combo = QComboBox()
        self.video_provider_combo.addItems(["sora", "pika", "runway", "luma", "custom"])
        form_layout.addRow(lang_manager.tr("api_provider_label"), self.video_provider_combo)
        
        self.video_model_input = QLineEdit()
        self.video_model_input.setPlaceholderText(lang_manager.tr("api_model_placeholder").format("sora-1.0 / gen-3"))
        form_layout.addRow(lang_manager.tr("api_model_label"), self.video_model_input)
        
        self.video_api_key_input = QLineEdit()
        self.video_api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.video_api_key_input.setPlaceholderText(lang_manager.tr("api_key_placeholder"))
        form_layout.addRow(lang_manager.tr("api_key_label"), self.video_api_key_input)
        
        self.video_base_url_input = QLineEdit()
        self.video_base_url_input.setPlaceholderText(lang_manager.tr("api_url_placeholder").format(""))
        form_layout.addRow(lang_manager.tr("api_url_label"), self.video_base_url_input)
        
        self.video_is_default_combo = QComboBox()
        self.video_is_default_combo.addItems([lang_manager.tr("no"), lang_manager.tr("yes")])
        form_layout.addRow(lang_manager.tr("set_default_label"), self.video_is_default_combo)
        
        group.setLayout(form_layout)
        right_layout.addWidget(group)
        
        save_api_btn = QPushButton(lang_manager.tr("save_this_api_btn"))
        save_api_btn.clicked.connect(self.save_video_api)
        right_layout.addWidget(save_api_btn)
        
        # 说明
        info = QLabel(lang_manager.tr("video_info"))
        info.setWordWrap(True)
        info.setStyleSheet("color: #666; padding: 10px; font-size: 12px;")
        right_layout.addWidget(info)
        
        right_layout.addStretch()
        layout.addLayout(right_layout, 2)
        
        return widget
    
    def create_general_settings_tab(self):
        """创建通用设置标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 存储设置
        group = QGroupBox(lang_manager.tr("storage_settings_group"))
        form_layout = QFormLayout()
        
        self.projects_dir_input = QLineEdit()
        self.projects_dir_input.setText("./projects")
        form_layout.addRow(lang_manager.tr("projects_dir_label"), self.projects_dir_input)
        
        group.setLayout(form_layout)
        layout.addWidget(group)
        
        # 语言设置
        lang_group = QGroupBox(lang_manager.tr("language_settings_group"))
        lang_layout = QVBoxLayout()
        
        lang_form = QFormLayout()
        self.language_combo = QComboBox()
        self.language_combo.addItem("简体中文 (Chinese)", "zh")
        self.language_combo.addItem("English", "en")
        lang_form.addRow(lang_manager.tr("language_select_label"), self.language_combo)
        lang_layout.addLayout(lang_form)
        
        # 重启提示
        tip_label = QLabel(lang_manager.tr("language_restart_tip"))
        tip_label.setStyleSheet("color: #666; font-size: 12px; margin-top: 5px;")
        lang_layout.addWidget(tip_label)
        
        lang_group.setLayout(lang_layout)
        layout.addWidget(lang_group)
        
        layout.addStretch()
        return widget
    
    def load_settings(self):
        """加载设置"""
        # 加载LLM接口列表
        self.refresh_llm_list()
        
        # 加载图片接口列表
        self.refresh_image_list()
        
        # 加载视频接口列表
        self.refresh_video_list()
        
        # 通用设置
        general_config = self.config.get_general_config()
        self.projects_dir_input.setText(general_config.get("projects_dir", "./projects"))
        
        # 加载语言设置
        current_lang = lang_manager.current_lang
        index = self.language_combo.findData(current_lang)
        if index >= 0:
            self.language_combo.setCurrentIndex(index)
    
    def refresh_llm_list(self):
        """刷新LLM接口列表"""
        self.llm_list.clear()
        apis = self.config.get_llm_apis()
        default_api = self.config.get_default_llm_api()
        
        for api in apis:
            name = api["name"]
            if name == default_api:
                name += f" [{lang_manager.tr('default_tag')}]"
            self.llm_list.addItem(name)
    
    def refresh_image_list(self):
        """刷新图片接口列表"""
        self.image_list.clear()
        apis = self.config.get_image_apis()
        default_api = self.config.get_default_image_api()
        
        for api in apis:
            name = api["name"]
            if name == default_api:
                name += f" [{lang_manager.tr('default_tag')}]"
            self.image_list.addItem(name)
    
    def refresh_video_list(self):
        """刷新视频接口列表"""
        self.video_list.clear()
        apis = self.config.get_video_apis()
        default_api = self.config.get_default_video_api()
        
        for api in apis:
            name = api["name"]
            if name == default_api:
                name += f" [{lang_manager.tr('default_tag')}]"
            self.video_list.addItem(name)
    
    def add_new_llm_api(self):
        """新增LLM接口"""
        self.llm_name_input.clear()
        self.llm_provider_combo.setCurrentIndex(0)
        self.llm_model_input.clear()
        self.llm_api_key_input.clear()
        self.llm_base_url_input.clear()
        self.llm_is_default_combo.setCurrentIndex(0)
        self.llm_name_input.setFocus()
    
    def load_llm_api_config(self, item):
        """加载LLM接口配置"""
        name = item.text().replace(" [默认]", "")
        api = self.config.get_llm_api(name)
        
        if api:
            self.llm_name_input.setText(api["name"])
            self.llm_provider_combo.setCurrentText(api.get("provider", "openai"))
            self.llm_model_input.setText(api.get("model", ""))
            self.llm_api_key_input.setText(api.get("api_key", ""))
            self.llm_base_url_input.setText(api.get("base_url", ""))
            
            is_default = (name == self.config.get_default_llm_api())
            self.llm_is_default_combo.setCurrentIndex(1 if is_default else 0)
    
    def save_llm_api(self):
        """保存LLM接口配置"""
        name = self.llm_name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "警告", "请输入接口名称")
            return
        
        api_key = self.llm_api_key_input.text().strip()
        if not api_key:
            QMessageBox.warning(self, "警告", "请输入API密钥")
            return
        
        self.config.add_llm_api(
            name=name,
            provider=self.llm_provider_combo.currentText(),
            api_key=api_key,
            base_url=self.llm_base_url_input.text().strip(),
            model=self.llm_model_input.text().strip()
        )
        
        if self.llm_is_default_combo.currentIndex() == 1:
            self.config.set_default_llm_api(name)
        
        self.config.save()
        self.refresh_llm_list()
        QMessageBox.information(self, lang_manager.tr("success"), lang_manager.tr("msg_api_saved").format(name))
    
    def delete_llm_api(self):
        """删除LLM接口"""
        current_item = self.llm_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, lang_manager.tr("warning"), lang_manager.tr("msg_select_api_delete"))
            return
        
        name = current_item.text().replace(f" [{lang_manager.tr('default_tag')}]", "")
        reply = QMessageBox.question(
            self, lang_manager.tr("confirm"), lang_manager.tr("msg_confirm_delete_api").format(name),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.config.delete_llm_api(name)
            if name == self.config.get_default_llm_api():
                self.config.set_default_llm_api("")
            self.config.save()
            self.refresh_llm_list()
            self.add_new_llm_api()  # 清空表单
    
    def save_settings(self):
        """保存设置（向后兼容）"""
        try:
            # 获取新语言
            new_lang = self.language_combo.currentData()
            if not new_lang:
                print("Warning: Language selection is None, defaulting to 'zh'")
                new_lang = "zh"
            
            # 重新加载配置以确保拥有最新状态（如其他地方修改了API配置）
            self.config.load()
            
            # 通用设置 - 显式包含 language 以防止被覆盖
            self.config.set_general_config(
                projects_dir=self.projects_dir_input.text(),
                language=new_lang
            )
            
            # 应用语言设置
            if new_lang != lang_manager.current_lang:
                lang_manager.set_language(new_lang, save=False)
                QMessageBox.information(
                    self, 
                    lang_manager.tr("info"), 
                    lang_manager.tr("menu_restart_required")
                )
            
            self.config.save()
            
            # 验证保存结果
            verify_config = Config()
            saved_lang = verify_config.get_general_config().get("language")
            print(f"Settings saved. Language in file: {saved_lang}")
            
            QMessageBox.information(self, "成功", lang_manager.tr("msg_settings_saved"))
        
        except Exception as e:
            print(f"Error saving settings: {e}")
            QMessageBox.critical(self, lang_manager.tr("error"), lang_manager.tr("msg_settings_save_failed").format(str(e)))

    
    # ==================== Image API 管理方法 ====================
    
    def add_new_image_api(self):
        """新增图片接口"""
        self.image_name_input.clear()
        self.image_provider_combo.setCurrentIndex(0)
        self.image_model_input.clear()
        self.image_api_key_input.clear()
        self.image_base_url_input.clear()
        self.image_is_default_combo.setCurrentIndex(0)
        self.image_name_input.setFocus()
    
    def load_image_api_config(self, item):
        """加载图片接口配置"""
        name = item.text().replace(" [默认]", "")
        api = self.config.get_image_api(name)
        
        if api:
            self.image_name_input.setText(api["name"])
            self.image_provider_combo.setCurrentText(api.get("provider", "stability"))
            self.image_model_input.setText(api.get("model", ""))
            self.image_api_key_input.setText(api.get("api_key", ""))
            self.image_base_url_input.setText(api.get("base_url", ""))
            
            is_default = (name == self.config.get_default_image_api())
            self.image_is_default_combo.setCurrentIndex(1 if is_default else 0)
    
    def save_image_api(self):
        """保存图片接口配置"""
        name = self.image_name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "警告", "请输入接口名称")
            return
        
        api_key = self.image_api_key_input.text().strip()
        if not api_key:
            QMessageBox.warning(self, "警告", "请输入API密钥")
            return
        
        self.config.add_image_api(
            name=name,
            provider=self.image_provider_combo.currentText(),
            api_key=api_key,
            base_url=self.image_base_url_input.text().strip(),
            model=self.image_model_input.text().strip()
        )
        
        if self.image_is_default_combo.currentIndex() == 1:
            self.config.set_default_image_api(name)
        
        self.config.save()
        self.refresh_image_list()
        QMessageBox.information(self, lang_manager.tr("success"), lang_manager.tr("msg_api_saved").format(name))
    
    def delete_image_api(self):
        """删除图片接口"""
        current_item = self.image_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, lang_manager.tr("warning"), lang_manager.tr("msg_select_api_delete"))
            return
        
        name = current_item.text().replace(f" [{lang_manager.tr('default_tag')}]", "")
        reply = QMessageBox.question(
            self, lang_manager.tr("confirm"), lang_manager.tr("msg_confirm_delete_api").format(name),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.config.delete_image_api(name)
            if name == self.config.get_default_image_api():
                self.config.set_default_image_api("")
            self.config.save()
            self.refresh_image_list()
            self.add_new_image_api()
    
    # ==================== Video API 管理方法 ====================
    
    def add_new_video_api(self):
        """新增视频接口"""
        self.video_name_input.clear()
        self.video_provider_combo.setCurrentIndex(0)
        self.video_model_input.clear()
        self.video_api_key_input.clear()
        self.video_base_url_input.clear()
        self.video_is_default_combo.setCurrentIndex(0)
        self.video_name_input.setFocus()
    
    def load_video_api_config(self, item):
        """加载视频接口配置"""
        name = item.text()
        default_suffix = f" [{lang_manager.tr('default_tag')}]"
        if name.endswith(default_suffix):
            name = name[:-len(default_suffix)]
        api = self.config.get_video_api(name)
        
        if api:
            self.video_name_input.setText(api["name"])
            self.video_provider_combo.setCurrentText(api.get("provider", "sora"))
            self.video_model_input.setText(api.get("model", ""))
            self.video_api_key_input.setText(api.get("api_key", ""))
            self.video_base_url_input.setText(api.get("base_url", ""))
            
            is_default = (name == self.config.get_default_video_api())
            self.video_is_default_combo.setCurrentIndex(1 if is_default else 0)
    
    def save_video_api(self):
        """保存视频接口配置"""
        name = self.video_name_input.text().strip()
        if not name:
            QMessageBox.warning(self, lang_manager.tr("warning"), lang_manager.tr("msg_enter_api_name"))
            return
        
        api_key = self.video_api_key_input.text().strip()
        if not api_key:
            QMessageBox.warning(self, lang_manager.tr("warning"), lang_manager.tr("msg_enter_api_key"))
            return
        
        self.config.add_video_api(
            name=name,
            provider=self.video_provider_combo.currentText(),
            api_key=api_key,
            base_url=self.video_base_url_input.text().strip(),
            model=self.video_model_input.text().strip()
        )
        
        if self.video_is_default_combo.currentIndex() == 1:
            self.config.set_default_video_api(name)
        
        self.config.save()
        self.refresh_video_list()
        QMessageBox.information(self, lang_manager.tr("success"), lang_manager.tr("msg_api_saved").format(name))
    
    def delete_video_api(self):
        """删除视频接口"""
        current_item = self.video_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, lang_manager.tr("warning"), lang_manager.tr("msg_select_api_delete"))
            return
        
        name = current_item.text()
        default_suffix = f" [{lang_manager.tr('default_tag')}]"
        if name.endswith(default_suffix):
            name = name[:-len(default_suffix)]
            
        reply = QMessageBox.question(
            self, lang_manager.tr("confirm"), lang_manager.tr("msg_confirm_delete_api").format(name),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.config.delete_video_api(name)
            if name == self.config.get_default_video_api():
                self.config.set_default_video_api("")
            self.config.save()
            self.refresh_video_list()
            self.add_new_video_api()
