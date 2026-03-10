import pytest
import tkinter as tk
from unittest.mock import Mock
from src.main_window import MainWindow

def test_main_window_creation():
    root = tk.Tk()
    root.withdraw()  # 隐藏窗口
    
    config = Mock()
    config.get = Mock(return_value="1000x700")
    alibaba_client = Mock()
    llm_agent = Mock()
    
    window = MainWindow(root, config, alibaba_client, llm_agent)
    
    assert window.root == root
    assert window.config == config
    assert window.alibaba_client == alibaba_client
    assert window.llm_agent == llm_agent
    
    root.destroy()