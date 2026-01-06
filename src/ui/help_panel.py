"""
帮助面板
"""
import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTextBrowser, QTabWidget)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QTextCursor
from src.utils.language import lang_manager
from src.utils.help_content import HELP_CONTENT


class HelpPanel(QWidget):
    """帮助面板"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)
        
        # 标题
        title = QLabel(lang_manager.tr("help_title"))
        title.setProperty("class", "title")
        layout.addWidget(title)
        
        # 标签页
        tab_widget = QTabWidget()
        
        # 使用指南标签页
        guide_tab = self.create_guide_tab()
        tab_widget.addTab(guide_tab, lang_manager.tr("help_tab_guide"))
        
        # 快捷键说明标签页
        shortcuts_tab = self.create_shortcuts_tab()
        tab_widget.addTab(shortcuts_tab, lang_manager.tr("help_tab_shortcuts"))
        
        # 运行日志标签页
        log_tab = self.create_log_tab()
        tab_widget.addTab(log_tab, lang_manager.tr("help_tab_logs"))
        
        # 关于标签页
        about_tab = self.create_about_tab()
        tab_widget.addTab(about_tab, lang_manager.tr("help_tab_about"))
        
        layout.addWidget(tab_widget)
        
    def create_guide_tab(self):
        """创建使用指南标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        content = HELP_CONTENT.get(lang_manager.current_lang, HELP_CONTENT["zh"]).get("guide", "")
        browser.setHtml(content)
        
        layout.addWidget(browser)
        return widget
        
    def create_shortcuts_tab(self):
        """创建快捷键说明标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        browser = QTextBrowser()
        content = HELP_CONTENT.get(lang_manager.current_lang, HELP_CONTENT["zh"]).get("shortcuts", "")
        browser.setHtml(content)
        
        layout.addWidget(browser)
        return widget

    def create_log_tab(self):
        """创建运行日志标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 顶部工具栏
        toolbar = QHBoxLayout()
        
        refresh_btn = QPushButton(lang_manager.tr("btn_refresh_log"))
        refresh_btn.clicked.connect(self.refresh_log)
        refresh_btn.setFixedSize(100, 32)
        from .styles import apply_button_property
        apply_button_property(refresh_btn, "secondary")
        
        self.log_path_label = QLabel()
        self.log_path_label.setStyleSheet("color: #6b7280; font-size: 12px;")
        
        toolbar.addWidget(refresh_btn)
        toolbar.addWidget(self.log_path_label)
        toolbar.addStretch()
        
        layout.addLayout(toolbar)
        
        # 日志显示区域
        self.log_browser = QTextBrowser()
        self.log_browser.setStyleSheet("""
            QTextBrowser {
                background-color: #1e1e1e;
                color: #d4d4d4;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
                border: 1px solid #374151;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        layout.addWidget(self.log_browser)
        
        # 初始加载
        self.refresh_log()
        
        return widget

    def refresh_log(self):
        """刷新日志内容"""
        log_path = os.path.abspath(os.path.join("logs", "app.log"))
        self.log_path_label.setText(lang_manager.tr("log_file_label").format(log_path))
        
        if os.path.exists(log_path):
            try:
                with open(log_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    self.log_browser.setPlainText(content)
                    # 滚动到底部
                    self.log_browser.moveCursor(QTextCursor.MoveOperation.End)
            except Exception as e:
                self.log_browser.setPlainText(lang_manager.tr("msg_read_log_failed").format(str(e)))
        else:
            self.log_browser.setPlainText(lang_manager.tr("log_file_not_found"))
        
    def create_about_tab(self):
        """创建关于标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        content = HELP_CONTENT.get(lang_manager.current_lang, HELP_CONTENT["zh"]).get("about", "")
        browser.setHtml(content)
        
        layout.addWidget(browser)
        return widget
