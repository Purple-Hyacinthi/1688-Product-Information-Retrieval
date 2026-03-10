# src/config_manager.py
import os
import json
from pathlib import Path

class ConfigManager:
    CONFIG_DIR_PERMISSIONS = 0o700
    SECTION_1688_API = "1688_api"
    SECTION_LLM = "llm"
    SECTION_UI = "ui"
    SECTION_AGENTS = "agents"
    
    def __init__(self, config_path="config/settings.json"):
        self.config_path = config_path
        self._config_cache = None
        self._ensure_config_dir()
        self._ensure_default_config()
    
    def _ensure_config_dir(self):
        config_dir = os.path.dirname(self.config_path)
        if config_dir:
            os.makedirs(config_dir, mode=self.CONFIG_DIR_PERMISSIONS, exist_ok=True)
    
    def _ensure_default_config(self):
        if not os.path.exists(self.config_path):
            self.save_config(self._get_default_config())
    
    def _get_default_config(self):
        template_path = Path(__file__).parent.parent / "config" / "config_template.json"
        default_config = {}
        
        if template_path.exists():
            try:
                with open(template_path, 'r', encoding='utf-8') as f:
                    default_config = json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        
        if not default_config:
            default_config = {
                self.SECTION_1688_API: {
                    "app_key": "",
                    "app_secret": "",
                    "access_token": "",
                    "refresh_token": "",
                    "api_endpoint": "https://gw.open.1688.com/openapi"
                },
                self.SECTION_LLM: {
                    "provider": "openai",
                    "api_key": "",
                    "base_url": "https://api.openai.com/v1",
                    "model": "gpt-3.5-turbo"
                },
                self.SECTION_AGENTS: {
                    "deepseek": {
                        "base_url": "https://api.deepseek.com/v1",
                        "model": "deepseek-chat"
                    },
                    "qwen": {
                        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
                        "model": "qwen-turbo"
                    },
                    "ollama": {
                        "base_url": "http://localhost:11434/v1",
                        "model": "llama2"
                    }
                }
            }
        
        for section in [self.SECTION_1688_API, self.SECTION_LLM]:
            if section in default_config:
                for key in default_config[section]:
                    if default_config[section][key] is None:
                        default_config[section][key] = ""
        
        def ensure_section_with_defaults(config, section, defaults):
            if section not in config:
                config[section] = defaults
            else:
                for key, value in defaults.items():
                    if key not in config[section]:
                        config[section][key] = value
        
        def ensure_key_exists(section_dict, key, default_value):
            if key not in section_dict:
                section_dict[key] = default_value
        
        ensure_section_with_defaults(default_config, self.SECTION_UI, {
            "window_size": "1000x700",
            "theme": "light"
        })
        
        if self.SECTION_LLM in default_config:
            ensure_key_exists(default_config[self.SECTION_LLM], "temperature", 0.7)
            ensure_key_exists(default_config[self.SECTION_LLM], "max_tokens", 500)
        
        if self.SECTION_1688_API in default_config:
            ensure_key_exists(default_config[self.SECTION_1688_API], "api_endpoint", "https://gw.open.1688.com/openapi")
        
        return default_config
    
    def load_config(self):
        if self._config_cache is None:
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self._config_cache = json.load(f)
            except (OSError, json.JSONDecodeError):
                self._config_cache = self._get_default_config()
        return self._config_cache
    
    def reload(self):
        self._config_cache = None
        return self.load_config()
    
    def save_config(self, config_data):
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            self._config_cache = config_data
        except (OSError, TypeError, ValueError) as e:
            raise IOError(f"无法保存配置文件到 {self.config_path}: {e}")
    
    def update_section(self, section, data):
        config = self.load_config()
        if section not in config:
            config[section] = {}
        config[section].update(data)
        self.save_config(config)
    
    def get(self, section, key, default=None):
        config = self.load_config()
        section_data = config.get(section)
        if not isinstance(section_data, dict):
            return default
        return section_data.get(key, default)