import pytest
import tkinter as tk
from unittest.mock import Mock, patch
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

@patch('tkinter.messagebox.showwarning')
def test_search_products_validation(mock_showwarning):
    root = tk.Tk()
    root.withdraw()
    
    config = Mock()
    config.get = Mock(return_value="1000x700")
    alibaba_client = Mock()
    llm_agent = Mock()
    
    window = MainWindow(root, config, alibaba_client, llm_agent)
    
    # 测试空关键词验证
    window.product_entry.insert(0, "")
    window._search_products()
    
    # 验证显示了警告
    mock_showwarning.assert_called_once()
    
    root.destroy()

def test_toggle_agent_mode():
    root = tk.Tk()
    root.withdraw()
    
    config = Mock()
    config.get = Mock(return_value="1000x700")
    alibaba_client = Mock()
    llm_agent = Mock()
    
    window = MainWindow(root, config, alibaba_client, llm_agent)
    
    # 初始状态应为禁用
    assert window.agent_button.instate(['disabled'])
    
    # 启用代理模式
    window.agent_enabled.set(True)
    window._toggle_agent_mode()
    assert window.agent_button.instate(['!disabled'])
    
    # 禁用代理模式
    window.agent_enabled.set(False)
    window._toggle_agent_mode()
    assert window.agent_button.instate(['disabled'])
    
    root.destroy()

def test_update_results():
    root = tk.Tk()
    root.withdraw()
    
    config = Mock()
    config.get = Mock(return_value="1000x700")
    alibaba_client = Mock()
    llm_agent = Mock()
    
    window = MainWindow(root, config, alibaba_client, llm_agent)
    
    # 创建模拟产品
    from src.product_model import Product
    mock_product = Product(
        title="测试商品" * 10,  # 长标题
        description="测试描述" * 20,  # 长描述
        url="https://example.com",
        price="100元",
        seller="测试卖家"
    )
    
    window.products = [mock_product]
    window._update_results()
    
    # 验证Treeview中是否有项目
    items = window.tree.get_children()
    assert len(items) == 1
    
    root.destroy()

@patch('threading.Thread')
def test_perform_search(mock_thread):
    root = tk.Tk()
    root.withdraw()
    
    config = Mock()
    config.get = Mock(return_value="1000x700")
    alibaba_client = Mock()
    alibaba_client.search_products = Mock(return_value=[])
    llm_agent = Mock()
    
    window = MainWindow(root, config, alibaba_client, llm_agent)
    
    # 调用_perform_search
    window._perform_search("测试商品", "测试用途")
    
    # 验证调用了search_products
    alibaba_client.search_products.assert_called_once_with("测试商品", "测试用途", limit=10)
    
    root.destroy()

def test_open_config_window():
    root = tk.Tk()
    root.withdraw()
    
    config = Mock()
    config.get = Mock(return_value="1000x700")
    alibaba_client = Mock()
    llm_agent = Mock()
    
    window = MainWindow(root, config, alibaba_client, llm_agent)
    
    # 调用_open_config_window，应该不抛出异常
    window._open_config_window()
    
    root.destroy()