# src/config_window.py
import tkinter as tk
from tkinter import ttk, messagebox

class ConfigWindow:
    def __init__(self, parent, config_manager):
        self.parent = parent
        self.config = config_manager
        
        self.window = tk.Toplevel(parent)
        self.window.title("配置")
        self.window.geometry("600x500")
        self.window.transient(parent)
        self.window.grab_set()
        
        self._setup_ui()
        self._load_config()
    
    def _setup_ui(self):
        notebook = ttk.Notebook(self.window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 1688 API配置页
        api_frame = ttk.Frame(notebook, padding="10")
        notebook.add(api_frame, text="1688 API")
        
        ttk.Label(api_frame, text="App Key:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.app_key_entry = ttk.Entry(api_frame, width=50, show="*")
        self.app_key_entry.grid(row=0, column=1, pady=5, padx=(5, 0))
        
        ttk.Label(api_frame, text="App Secret:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.app_secret_entry = ttk.Entry(api_frame, width=50, show="*")
        self.app_secret_entry.grid(row=1, column=1, pady=5, padx=(5, 0))
        
        ttk.Label(api_frame, text="Access Token:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.access_token_entry = ttk.Entry(api_frame, width=50, show="*")
        self.access_token_entry.grid(row=2, column=1, pady=5, padx=(5, 0))
        
        ttk.Label(api_frame, text="Refresh Token:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.refresh_token_entry = ttk.Entry(api_frame, width=50, show="*")
        self.refresh_token_entry.grid(row=3, column=1, pady=5, padx=(5, 0))
        
        ttk.Label(api_frame, text="如何获取API密钥?").grid(row=4, column=0, columnspan=2, pady=(20, 5), sticky=tk.W)
        
        help_text = """1. 访问 https://open.1688.com
2. 注册成为开放平台开发者
3. 创建应用获取App Key和App Secret
4. 根据文档获取Access Token"""
        
        help_label = ttk.Label(api_frame, text=help_text, justify=tk.LEFT)
        help_label.grid(row=5, column=0, columnspan=2, sticky=tk.W)
        
        # LLM配置页
        llm_frame = ttk.Frame(notebook, padding="10")
        notebook.add(llm_frame, text="LLM配置")
        
        ttk.Label(llm_frame, text="提供商:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.provider_var = tk.StringVar(value="openai")
        provider_combo = ttk.Combobox(llm_frame, textvariable=self.provider_var, width=20)
        provider_combo['values'] = ('openai', 'deepseek', 'qwen', 'ollama')
        provider_combo.grid(row=0, column=1, pady=5, padx=(5, 0), sticky=tk.W)
        
        ttk.Label(llm_frame, text="API Key:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.llm_api_key_entry = ttk.Entry(llm_frame, width=50, show="*")
        self.llm_api_key_entry.grid(row=1, column=1, pady=5, padx=(5, 0))
        
        ttk.Label(llm_frame, text="Base URL:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.base_url_entry = ttk.Entry(llm_frame, width=50)
        self.base_url_entry.grid(row=2, column=1, pady=5, padx=(5, 0))
        
        ttk.Label(llm_frame, text="模型:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.model_entry = ttk.Entry(llm_frame, width=50)
        self.model_entry.grid(row=3, column=1, pady=5, padx=(5, 0))
        
        ttk.Label(llm_frame, text="预设配置:").grid(row=4, column=0, sticky=tk.W, pady=(20, 5))
        
        preset_frame = ttk.Frame(llm_frame)
        preset_frame.grid(row=5, column=0, columnspan=2, sticky=tk.W)
        
        ttk.Button(preset_frame, text="DeepSeek", 
                  command=lambda: self._apply_preset("deepseek")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(preset_frame, text="千问", 
                  command=lambda: self._apply_preset("qwen")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(preset_frame, text="Ollama", 
                  command=lambda: self._apply_preset("ollama")).pack(side=tk.LEFT)
        
        # 按钮区域
        button_frame = ttk.Frame(self.window)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Button(button_frame, text="测试连接", command=self._test_connection).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="保存", command=self._save_config).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="取消", command=self.window.destroy).pack(side=tk.RIGHT)
    
    def _load_config(self):
        try:
            config = self.config.load_config()
            
            # 1688 API
            api_config = config.get("1688_api", {})
            self._safe_entry_insert(self.app_key_entry, api_config.get("app_key", ""))
            self._safe_entry_insert(self.app_secret_entry, api_config.get("app_secret", ""))
            self._safe_entry_insert(self.access_token_entry, api_config.get("access_token", ""))
            self._safe_entry_insert(self.refresh_token_entry, api_config.get("refresh_token", ""))
            
            # LLM
            llm_config = config.get("llm", {})
            if hasattr(self, 'provider_var'):
                self.provider_var.set(llm_config.get("provider", "openai"))
            self._safe_entry_insert(self.llm_api_key_entry, llm_config.get("api_key", ""))
            self._safe_entry_insert(self.base_url_entry, llm_config.get("base_url", ""))
            self._safe_entry_insert(self.model_entry, llm_config.get("model", ""))
        except Exception as e:
            import traceback
            print(f"加载配置时出错: {e}")
            print(traceback.format_exc())
    
    def _safe_entry_insert(self, entry_widget, text):
        """安全地向Entry组件插入文本"""
        if entry_widget and hasattr(entry_widget, 'insert'):
            try:
                entry_widget.delete(0, tk.END)
                entry_widget.insert("0", str(text) if text is not None else "")
            except Exception:
                # 如果插入失败，静默处理
                pass
    
    def _safe_entry_get(self, entry_widget, default=""):
        """安全地从Entry组件获取文本"""
        if entry_widget and hasattr(entry_widget, 'get'):
            try:
                return entry_widget.get()
            except Exception:
                return default
        return default
    
    def _apply_preset(self, preset):
        presets = {
            "deepseek": {
                "provider": "deepseek",
                "base_url": "https://api.deepseek.com/v1",
                "model": "deepseek-chat"
            },
            "qwen": {
                "provider": "qwen",
                "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
                "model": "qwen-turbo"
            },
            "ollama": {
                "provider": "ollama",
                "base_url": "http://localhost:11434/v1",
                "model": "llama2"
            }
        }
        
        if preset in presets:
            preset_config = presets[preset]
            if hasattr(self, 'provider_var'):
                self.provider_var.set(preset_config["provider"])
            self._safe_entry_insert(self.base_url_entry, preset_config["base_url"])
            self._safe_entry_insert(self.model_entry, preset_config["model"])
    
    def _test_connection(self):
        # 测试1688 API连接（检查凭证是否填写）
        app_key = self._safe_entry_get(self.app_key_entry)
        app_secret = self._safe_entry_get(self.app_secret_entry)
        
        if app_key and app_secret:
            messagebox.showinfo("1688 API配置", "1688 API凭证已填写（未进行实际连接测试）")
        else:
            messagebox.showwarning("1688 API配置", "1688 API凭证未填写，请填写App Key和App Secret")
        
        # 测试LLM连接
        from src.llm_agent import LLMAgent
        
        provider = self.provider_var.get() if hasattr(self, 'provider_var') else "openai"
        api_key = self._safe_entry_get(self.llm_api_key_entry)
        base_url = self._safe_entry_get(self.base_url_entry)
        model = self._safe_entry_get(self.model_entry)
        
        test_config = {
            "llm": {
                "provider": provider,
                "api_key": api_key,
                "base_url": base_url,
                "model": model
            }
        }
        
        class MockConfig:
            def get(self, section, key, default=None):
                return test_config.get(section, {}).get(key, default)
        
        try:
            agent = LLMAgent(MockConfig())
            if agent.test_connection():
                messagebox.showinfo("测试成功", "LLM连接测试成功！")
            else:
                messagebox.showerror("测试失败", "LLM连接测试失败，请检查配置")
        except Exception as e:
            messagebox.showerror("测试错误", f"LLM连接测试失败: {str(e)}")
    
    def _save_config(self):
        config = self.config.load_config()
        
        # 确保配置部分存在
        if "1688_api" not in config:
            config["1688_api"] = {}
        if "llm" not in config:
            config["llm"] = {}
        
        # 更新1688 API配置
        config["1688_api"].update({
            "app_key": self._safe_entry_get(self.app_key_entry),
            "app_secret": self._safe_entry_get(self.app_secret_entry),
            "access_token": self._safe_entry_get(self.access_token_entry),
            "refresh_token": self._safe_entry_get(self.refresh_token_entry)
        })
        
        # 更新LLM配置
        provider = self.provider_var.get() if hasattr(self, 'provider_var') else "openai"
        config["llm"].update({
            "provider": provider,
            "api_key": self._safe_entry_get(self.llm_api_key_entry),
            "base_url": self._safe_entry_get(self.base_url_entry),
            "model": self._safe_entry_get(self.model_entry)
        })
        
        self.config.save_config(config)
        messagebox.showinfo("保存成功", "配置已保存")
        self.window.destroy()
    
    def destroy(self):
        self.window.destroy()