# tests/test_config_window.py
import pytest
import tkinter as tk
from unittest.mock import Mock, patch
from src.config_window import ConfigWindow

def test_config_window_creation():
    root = tk.Tk()
    root.withdraw()
    
    config = Mock()
    config.load_config = Mock(return_value={
        "1688_api": {"app_key": "", "app_secret": ""},
        "llm": {"api_key": "", "base_url": ""}
    })
    config.save_config = Mock()
    
    window = ConfigWindow(root, config)
    
    assert window.parent == root
    assert window.config == config
    
    window.destroy()
    root.destroy()

def test_load_config():
    root = tk.Tk()
    root.withdraw()
    
    config = Mock()
    config.load_config = Mock(return_value={
        "1688_api": {
            "app_key": "test_key",
            "app_secret": "test_secret",
            "access_token": "test_token",
            "refresh_token": "test_refresh"
        },
        "llm": {
            "provider": "deepseek",
            "api_key": "llm_key",
            "base_url": "https://api.deepseek.com/v1",
            "model": "deepseek-chat"
        }
    })
    config.save_config = Mock()
    
    window = ConfigWindow(root, config)
    
    # 验证配置已加载到UI
    assert window.app_key_entry.get() == "test_key"
    assert window.app_secret_entry.get() == "test_secret"
    assert window.access_token_entry.get() == "test_token"
    assert window.refresh_token_entry.get() == "test_refresh"
    assert window.provider_var.get() == "deepseek"
    assert window.llm_api_key_entry.get() == "llm_key"
    assert window.base_url_entry.get() == "https://api.deepseek.com/v1"
    assert window.model_entry.get() == "deepseek-chat"
    
    window.destroy()
    root.destroy()

def test_apply_preset():
    root = tk.Tk()
    root.withdraw()
    
    config = Mock()
    config.load_config = Mock(return_value={
        "1688_api": {},
        "llm": {}
    })
    config.save_config = Mock()
    
    window = ConfigWindow(root, config)
    
    # 测试DeepSeek预设
    window._apply_preset("deepseek")
    assert window.provider_var.get() == "deepseek"
    assert window.base_url_entry.get() == "https://api.deepseek.com/v1"
    assert window.model_entry.get() == "deepseek-chat"
    
    # 测试千问预设
    window._apply_preset("qwen")
    assert window.provider_var.get() == "qwen"
    assert window.base_url_entry.get() == "https://dashscope.aliyuncs.com/compatible-mode/v1"
    assert window.model_entry.get() == "qwen-turbo"
    
    # 测试Ollama预设
    window._apply_preset("ollama")
    assert window.provider_var.get() == "ollama"
    assert window.base_url_entry.get() == "http://localhost:11434/v1"
    assert window.model_entry.get() == "llama2"
    
    window.destroy()
    root.destroy()

@patch('src.config_window.messagebox')
def test_save_config(mock_messagebox):
    root = tk.Tk()
    root.withdraw()
    
    config = Mock()
    config.load_config = Mock(return_value={
        "1688_api": {},
        "llm": {}
    })
    config.save_config = Mock()
    
    window = ConfigWindow(root, config)
    
    # 设置一些测试值
    window.app_key_entry.insert(0, "new_key")
    window.app_secret_entry.insert(0, "new_secret")
    window.provider_var.set("openai")
    window.llm_api_key_entry.insert(0, "new_llm_key")
    
    # 调用保存
    window._save_config()
    
    # 验证save_config被调用
    config.save_config.assert_called_once()
    
    # 验证保存的数据
    saved_config = config.save_config.call_args[0][0]
    assert saved_config["1688_api"]["app_key"] == "new_key"
    assert saved_config["1688_api"]["app_secret"] == "new_secret"
    assert saved_config["llm"]["provider"] == "openai"
    assert saved_config["llm"]["api_key"] == "new_llm_key"
    
    window.destroy()
    root.destroy()

@patch('src.config_window.messagebox')
@patch('src.llm_agent.LLMAgent')
def test_test_connection(mock_llm_agent, mock_messagebox):
    root = tk.Tk()
    root.withdraw()
    
    config = Mock()
    config.load_config = Mock(return_value={
        "1688_api": {},
        "llm": {}
    })
    config.save_config = Mock()
    
    window = ConfigWindow(root, config)
    
    # 设置LLM配置
    window.provider_var.set("openai")
    window.llm_api_key_entry.insert(0, "test_key")
    window.base_url_entry.insert(0, "https://api.openai.com/v1")
    window.model_entry.insert(0, "gpt-3.5-turbo")
    
    # 模拟LLMAgent
    mock_agent = Mock()
    mock_agent.test_connection.return_value = True
    mock_llm_agent.return_value = mock_agent
    
    # 调用测试连接
    window._test_connection()
    
    # 验证LLMAgent被创建
    mock_llm_agent.assert_called_once()
    
    # 验证消息框被调用（1688 API警告和LLM成功）
    assert mock_messagebox.showwarning.called or mock_messagebox.showinfo.called
    
    window.destroy()
    root.destroy()