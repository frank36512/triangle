"""
Language Manager
Handles language detection, switching, and string retrieval.
"""
import locale
import sys
from src.utils.config import Config
from src.utils.translations import TRANSLATIONS

class LanguageManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LanguageManager, cls).__new__(cls)
            cls._instance.config = Config()
            cls._instance.current_lang = cls._instance._load_initial_language()
        return cls._instance
    
    def _load_initial_language(self) -> str:
        """
        Determine initial language.
        Priority: Config > System Locale > Default (zh)
        """
        # 1. Check config
        saved_lang = self.config.config_data.get("general", {}).get("language")
        if saved_lang and saved_lang in TRANSLATIONS:
            return saved_lang
            
        # 2. Check system locale
        try:
            sys_lang = locale.getdefaultlocale()[0]
            if sys_lang and sys_lang.lower().startswith("en"):
                return "en"
            # Default to zh for zh_CN, zh_TW or other
        except:
            pass
            
        return "zh"

    def get_current_language(self) -> str:
        return self.current_lang

    def set_language(self, lang_code: str, save: bool = True):
        """Set language and save to config"""
        if lang_code in TRANSLATIONS:
            self.current_lang = lang_code
            
            if save:
                # Update config
                # Reload config to ensure we don't overwrite other changes
                self.config.load()
                
                if "general" not in self.config.config_data:
                    self.config.config_data["general"] = {}
                self.config.config_data["general"]["language"] = lang_code
                self.config.save()

    def tr(self, key: str) -> str:
        """Translate a key"""
        return TRANSLATIONS.get(self.current_lang, TRANSLATIONS["zh"]).get(key, key)

# Global instance
lang_manager = LanguageManager()

def tr(key: str) -> str:
    """Helper function for translation"""
    return lang_manager.tr(key)
