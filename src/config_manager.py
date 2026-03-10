# src/config_manager.py
import os
import json
from pathlib import Path

class ConfigManager:
    def __init__(self, config_path="config/settings.json"):
        self.config_path = config_path
        self._ensure_config_dir()
        self._ensure_default_config()
    
    def _ensure_config_dir(self):
        config_dir = os.path.dirname(self.config_path)
        if config_dir and not os.path.exists(config_dir):
            os.makedirs(config_dir)
    
    def _ensure_default_config(self):
        if not os.path.exists(self.config_path):
            self.save_config(self._get_default_config())
    
    def _get_default_config(self):
        import os
        import json
        from pathlib import Path
        
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
                "1688_api": {
                    "app_key": "",
                    "app_secret": "",
                    "access_token": "",
                    "refresh_token": "",
                    "api_endpoint": "https://gw.open.1688.com/openapi"
                },
                "llm": {
                    "provider": "openai",
                    "api_key": "",
                    "base_url": "https://api.openai.com/v1",
                    "model": "gpt-3.5-turbo"
                },
                "agents": {
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
        
        for section in ["1688_api", "llm"]:
            if section in default_config:
                for key in default_config[section]:
                    if default_config[section][key] is None:
                        default_config[section][key] = ""
        
        if "ui" not in default_config:
            default_config["ui"] = {
                "window_size": "1000x700",
                "theme": "light"
            }
        
        if "llm" in default_config:
            if "temperature" not in default_config["llm"]:
                default_config["llm"]["temperature"] = 0.7
            if "max_tokens" not in default_config["llm"]:
                default_config["llm"]["max_tokens"] = 500
        
        if "1688_api" in default_config:
            if "api_endpoint" not in default_config["1688_api"]:
                default_config["1688_api"]["api_endpoint"] = "https://gw.open.1688.com/openapi"
        
        return default_config
    
    def load_config(self):
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return self._get_default_config()
    
    def save_config(self, config_data):
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
    
    def update_section(self, section, data):
        config = self.load_config()
        if section not in config:
            config[section] = {}
        config[section].update(data)
        self.save_config(config)
    
    def get(self, section, key, default=None):
        config = self.load_config()
        return config.get(section, {}).get(key, default)