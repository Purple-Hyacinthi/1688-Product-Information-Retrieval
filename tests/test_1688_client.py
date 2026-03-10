# tests/test_1688_client.py
import pytest
from unittest.mock import Mock, patch
from src.product_model import Product
from src.config_manager import ConfigManager

def test_alibaba_client_initialization():
    from src.alibaba_client import AlibabaClient
    config = Mock()
    config.get = Mock(return_value="test_key")
    client = AlibabaClient(config)
    assert client.config == config

@patch('requests.post')
def test_search_products_mock(mock_post):
    from src.alibaba_client import AlibabaClient
    
    mock_response = Mock()
    mock_response.json.return_value = {
        "result": {
            "success": True,
            "data": [
                {
                    "title": "测试商品",
                    "description": "商品描述",
                    "url": "https://detail.1688.com/test",
                    "price": "100元",
                    "seller": "测试卖家"
                }
            ]
        }
    }
    mock_response.raise_for_status = Mock()
    mock_post.return_value = mock_response
    
    config = Mock()
    config.get = Mock(side_effect=lambda section, key, default=None: {
        ("1688_api", "app_key"): "test_key",
        ("1688_api", "app_secret"): "test_secret",
        ("1688_api", "access_token"): "test_token"
    }.get((section, key), default))
    
    client = AlibabaClient(config)
    products = client.search_products("测试商品", "测试用途", limit=10)
    
    assert len(products) == 1
    assert products[0].title == "测试商品"
    assert products[0].url == "https://detail.1688.com/test"