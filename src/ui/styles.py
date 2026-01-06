"""
UI样式定义
现代化、简洁、美观的界面样式
"""

# 主题色彩方案
COLORS = {
    # 主色调 - 蓝色系
    'primary': '#2563eb',        # 主色
    'primary_dark': '#1e40af',   # 主色深色
    'primary_light': '#3b82f6',  # 主色浅色
    
    # 辅助色
    'success': '#10b981',        # 成功绿
    'success_dark': '#059669',   # 成功绿深色
    'warning': '#f59e0b',        # 警告橙
    'warning_dark': '#d97706',   # 警告橙深色
    'danger': '#ef4444',         # 危险红
    'danger_dark': '#dc2626',    # 危险红深色
    'info': '#06b6d4',           # 信息青
    'info_dark': '#0891b2',      # 信息青深色
    
    # 中性色
    'bg_primary': '#ffffff',     # 主背景
    'bg_secondary': '#f8fafc',   # 次背景
    'bg_tertiary': '#f1f5f9',    # 三级背景
    'bg_hover': '#e2e8f0',       # 悬停背景
    'bg_active': '#cbd5e1',      # 激活背景
    
    # 文字颜色
    'text_primary': '#0f172a',   # 主文字
    'text_secondary': '#475569', # 次文字
    'text_tertiary': '#94a3b8',  # 三级文字
    'text_inverse': '#ffffff',   # 反色文字
    
    # 边框颜色
    'border': '#e2e8f0',         # 边框
    'border_dark': '#cbd5e1',    # 深色边框
}

# 全局样式
GLOBAL_STYLE = f"""
QWidget {{
    font-family: 'Microsoft YaHei UI', 'Segoe UI', system-ui, sans-serif;
    font-size: 14px;
    color: {COLORS['text_primary']};
}}

/* 主窗口 */
QMainWindow {{
    background-color: {COLORS['bg_secondary']};
}}

/* 菜单栏 */
QMenuBar {{
    background-color: #ffffff;
    border-bottom: 1px solid #e5e7eb;
    padding: 4px;
}}

QMenuBar::item {{
    background-color: transparent;
    padding: 6px 12px;
    color: #374151;
}}

QMenuBar::item:selected {{
    background-color: #f3f4f6;
    border-radius: 4px;
}}

QMenuBar::item:pressed {{
    background-color: #e5e7eb;
}}

QMenu {{
    background-color: white;
    border: 1px solid #e5e7eb;
    border-radius: 6px;
    padding: 4px;
}}

QMenu::item {{
    padding: 8px 24px;
    color: #374151;
}}

QMenu::item:selected {{
    background-color: #f0f9ff;
    color: #2563eb;
    border-radius: 4px;
}}

/* 标题标签 */
QLabel[class="title"] {{
    font-size: 18px;
    font-weight: bold;
    color: {COLORS['text_primary']};
    padding: 12px 16px;
}}

QLabel[class="subtitle"] {{
    font-size: 16px;
    font-weight: 600;
    color: {COLORS['text_primary']};
    padding: 8px 12px;
}}

/* 分组框 */
QGroupBox {{
    font-weight: 600;
    font-size: 14px;
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 12px;
    background-color: {COLORS['bg_primary']};
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    padding: 0 8px;
    background-color: {COLORS['bg_primary']};
}}

/* 按钮样式 */
QPushButton {{
    background-color: {COLORS['primary']};
    color: {COLORS['text_inverse']};
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-size: 14px;
    font-weight: 500;
    min-height: 36px;
}}

QPushButton:hover {{
    background-color: {COLORS['primary_dark']};
}}

QPushButton:pressed {{
    background-color: {COLORS['primary_dark']};
    padding-top: 9px;
}}

QPushButton:disabled {{
    background-color: {COLORS['bg_tertiary']};
    color: {COLORS['text_tertiary']};
}}

/* 次要按钮 */
QPushButton[class="secondary"] {{
    background-color: {COLORS['bg_tertiary']};
    color: #1f2937;
    border: 1px solid {COLORS['border']};
    font-weight: 500;
}}

QPushButton[class="secondary"]:hover {{
    background-color: {COLORS['bg_hover']};
    border-color: {COLORS['border_dark']};
    color: #111827;
}}

QPushButton[class="secondary"]:disabled {{
    background-color: #f3f4f6;
    color: #9ca3af;
    border: 1px solid #e5e7eb;
}}

/* 危险按钮 */
QPushButton[class="danger"] {{
    background-color: {COLORS['danger']};
    color: white;
}}

QPushButton[class="danger"]:hover {{
    background-color: #dc2626;
}}

QPushButton[class="danger"]:disabled {{
    background-color: #fca5a5;
    color: #fecaca;
}}

/* 成功按钮 */
QPushButton[class="success"] {{
    background-color: {COLORS['success']};
    color: white;
}}

QPushButton[class="success"]:hover {{
    background-color: {COLORS['success_dark']};
}}

/* 警告按钮 */
QPushButton[class="warning"] {{
    background-color: {COLORS['warning']};
    color: white;
}}

QPushButton[class="warning"]:hover {{
    background-color: {COLORS['warning_dark']};
}}

/* 信息按钮 */
QPushButton[class="info"] {{
    background-color: {COLORS['info']};
    color: {COLORS['text_primary']};
    font-weight: 500;
}}

QPushButton[class="info"]:hover {{
    background-color: {COLORS['info_dark']};
    color: {COLORS['text_primary']};
}}

QPushButton[class="info"]:disabled {{
    background-color: #cbd5e1;
    color: #94a3b8;
}}

/* 标签页按钮 */
QPushButton[class="tab"] {{
    background-color: transparent;
    color: {COLORS['text_secondary']};
    border: none;
    border-bottom: 3px solid transparent;
    border-radius: 0;
    padding: 12px 20px;
    font-size: 14px;
    font-weight: 500;
}}

QPushButton[class="tab"]:hover {{
    color: {COLORS['primary']};
    background-color: {COLORS['bg_hover']};
}}

QPushButton[class="tab"][active="true"] {{
    color: {COLORS['primary']};
    border-bottom-color: {COLORS['primary']};
    font-weight: 600;
}}

/* 输入框 */
QLineEdit, QTextEdit, QPlainTextEdit {{
    background-color: {COLORS['bg_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 8px 12px;
    color: {COLORS['text_primary']};
    selection-background-color: {COLORS['primary_light']};
}}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
    border-color: {COLORS['primary']};
    outline: none;
}}

QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled {{
    background-color: {COLORS['bg_tertiary']};
    color: {COLORS['text_tertiary']};
}}

/* 下拉框 */
QComboBox {{
    background-color: {COLORS['bg_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 8px 12px;
    min-height: 36px;
}}

QComboBox:hover {{
    border-color: {COLORS['border_dark']};
}}

QComboBox:focus {{
    border-color: {COLORS['primary']};
}}

QComboBox::drop-down {{
    border: none;
    width: 30px;
}}

QComboBox::down-arrow {{
    image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOCIgdmlld0JveD0iMCAwIDEyIDgiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHBhdGggZD0iTTEgMUw2IDZMMTEgMSIgc3Ryb2tlPSIjNjQ3NDhiIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPjwvc3ZnPg==);
}}

QComboBox QAbstractItemView {{
    background-color: {COLORS['bg_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 4px;
    selection-background-color: {COLORS['primary_light']};
    selection-color: {COLORS['text_inverse']};
}}

/* 列表 */
QListWidget {{
    background-color: {COLORS['bg_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    padding: 4px;
    outline: none;
}}

QListWidget::item {{
    padding: 10px 12px;
    border-radius: 6px;
    margin: 2px 0;
}}

QListWidget::item:hover {{
    background-color: {COLORS['bg_hover']};
}}

QListWidget::item:selected {{
    background-color: {COLORS['primary_light']};
    color: {COLORS['text_inverse']};
}}

/* 图标模式列表项 - 显示缩略图和文本 */
QListWidget[viewMode="IconMode"]::item {{
    padding: 8px;
    text-align: center;
    border: 1px solid {COLORS['border']};
    background-color: {COLORS['bg_primary']};
}}

QListWidget[viewMode="IconMode"]::item:hover {{
    border-color: {COLORS['primary_light']};
    background-color: {COLORS['bg_hover']};
}}

QListWidget[viewMode="IconMode"]::item:selected {{
    border-color: {COLORS['primary']};
    background-color: {COLORS['bg_hover']};
}}

/* 滚动条 */
QScrollBar:vertical {{
    background-color: {COLORS['bg_secondary']};
    width: 12px;
    border-radius: 6px;
}}

QScrollBar::handle:vertical {{
    background-color: {COLORS['border_dark']};
    border-radius: 6px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {COLORS['text_tertiary']};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar:horizontal {{
    background-color: {COLORS['bg_secondary']};
    height: 12px;
    border-radius: 6px;
}}

QScrollBar::handle:horizontal {{
    background-color: {COLORS['border_dark']};
    border-radius: 6px;
    min-width: 30px;
}}

QScrollBar::handle:horizontal:hover {{
    background-color: {COLORS['text_tertiary']};
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0px;
}}

/* 进度条 */
QProgressBar {{
    background-color: {COLORS['bg_tertiary']};
    border: none;
    border-radius: 6px;
    text-align: center;
    height: 8px;
}}

QProgressBar::chunk {{
    background-color: {COLORS['primary']};
    border-radius: 6px;
}}

/* 分割器 */
QSplitter::handle {{
    background-color: {COLORS['border']};
}}

QSplitter::handle:horizontal {{
    width: 1px;
}}

QSplitter::handle:vertical {{
    height: 1px;
}}

/* 标签页容器 */
QTabWidget::pane {{
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    background-color: {COLORS['bg_primary']};
}}

QTabBar::tab {{
    background-color: transparent;
    color: {COLORS['text_secondary']};
    padding: 10px 20px;
    border-bottom: 3px solid transparent;
}}

QTabBar::tab:hover {{
    color: {COLORS['primary']};
    background-color: {COLORS['bg_hover']};
}}

QTabBar::tab:selected {{
    color: {COLORS['primary']};
    border-bottom-color: {COLORS['primary']};
    font-weight: 600;
}}

/* 工具提示 */
QToolTip {{
    background-color: {COLORS['text_primary']};
    color: {COLORS['text_inverse']};
    border: none;
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 13px;
}}

/* 状态栏 */
QStatusBar {{
    background-color: {COLORS['bg_primary']};
    border-top: 1px solid {COLORS['border']};
    color: {COLORS['text_secondary']};
}}
"""

# 项目列表面板样式
PROJECT_LIST_STYLE = f"""
QWidget {{
    background-color: {COLORS['bg_primary']};
    border-right: 1px solid {COLORS['border']};
}}
"""

# 功能面板区域样式
FUNCTION_PANEL_STYLE = f"""
QWidget {{
    background-color: {COLORS['bg_secondary']};
}}
"""

# 标签页容器样式
TAB_CONTAINER_STYLE = f"""
QWidget {{
    background-color: {COLORS['bg_primary']};
    border-bottom: 1px solid {COLORS['border']};
}}
"""


def apply_button_property(button, class_name):
    """应用按钮属性"""
    button.setProperty("class", class_name)
    button.style().unpolish(button)
    button.style().polish(button)


def set_tab_active(button, active=True):
    """设置标签页按钮激活状态"""
    button.setProperty("active", "true" if active else "false")
    button.style().unpolish(button)
    button.style().polish(button)
