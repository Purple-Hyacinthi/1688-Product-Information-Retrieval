# tests/test_config_window.py
import pytest
import tkinter as tk
from unittest.mock import Mock
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