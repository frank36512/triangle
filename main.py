"""
三角铁--AI广告视频生成系统
主程序入口
"""
import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from src.ui.main_window import MainWindow
from src.utils.logger import logger
from src.utils.language import lang_manager


def main():
    """主函数"""
    try:
        # 修复 Windows 下 PyQt6 多媒体后端问题
        if os.name == 'nt':
            os.environ['QT_MEDIA_BACKEND'] = 'windows'
            
            # 显式设置插件路径，确保能找到 windowsmediaplugin.dll
            try:
                import PyQt6
                qt_path = os.path.dirname(PyQt6.__file__)
                plugin_path = os.path.join(qt_path, "Qt6", "plugins")
                if os.path.exists(plugin_path):
                    os.environ['QT_PLUGIN_PATH'] = plugin_path
            except ImportError:
                pass

        print("=" * 60)
        print(lang_manager.tr("startup_msg"))
        print("=" * 60)
        
        # 创建应用程序
        app = QApplication(sys.argv)
        app.setApplicationName("Triangle")
        app.setOrganizationName("Triangle")
        
        print(lang_manager.tr("app_created"))
        
        # 设置应用图标
        icon_path = "adplay.ico"
        if not os.path.exists(icon_path):
            # 尝试在resources中查找（兼容旧版本）
            icon_path = os.path.join("resources", "icon.ico")
            
        if os.path.exists(icon_path):
            app.setWindowIcon(QIcon(icon_path))
            print(lang_manager.tr("icon_loaded").format(icon_path))
        
        # 设置样式
        app.setStyle("Fusion")
        print(lang_manager.tr("style_set"))
        
        # 创建并显示主窗口
        logger.info(lang_manager.tr("startup_log"))
        print("\n" + lang_manager.tr("init_main_window"))
        main_window = MainWindow()
        print(lang_manager.tr("main_window_created"))
        
        main_window.show()
        print(lang_manager.tr("main_window_shown"))
        print("\n" + lang_manager.tr("startup_success"))
        print("=" * 60)
        
        # 运行应用程序
        sys.exit(app.exec())
    
    except Exception as e:
        print("\n" + "=" * 60)
        print(lang_manager.tr("startup_failed"))
        print("=" * 60)
        logger.error(f"程序启动失败: {str(e)}", exc_info=True)
        print("\n" + lang_manager.tr("error_msg").format(str(e)))
        import traceback
        traceback.print_exc()
        print("\n" + lang_manager.tr("check_error_msg"))
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()
