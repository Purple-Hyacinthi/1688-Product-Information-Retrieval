# tests/test_integration.py
import pytest
import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_import_modules():
    from config_manager import ConfigManager
    from product_model import Product
    from alibaba_client import AlibabaClient
    from llm_agent import LLMAgent
    
    assert ConfigManager is not None
    assert Product is not None
    assert AlibabaClient is not None
    assert LLMAgent is not None

def test_product_flow():
    from product_model import Product
    
    product = Product("测试", "描述", "https://example.com")
    assert product.title == "测试"
    assert product.url == "https://example.com"
    
    data = product.to_dict()
    assert data["title"] == "测试"
    
    product2 = Product.from_dict(data)
    assert product2.title == "测试"