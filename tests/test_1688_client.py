# tests/test_1688_client.py
import pytest
import requests
from unittest.mock import Mock, patch
from src.product_model import Product
from src.config_manager import ConfigManager
from src.alibaba_client import AlibabaAPIError

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


@patch('requests.post')
def test_call_api_request_exception(mock_post):
    from src.alibaba_client import AlibabaClient
    
    mock_post.side_effect = requests.exceptions.RequestException("网络错误")
    
    config = Mock()
    config.get = Mock(side_effect=lambda section, key, default=None: {
        ("1688_api", "app_key"): "test_key",
        ("1688_api", "app_secret"): "test_secret",
        ("1688_api", "access_token"): "test_token"
    }.get((section, key), default))
    
    client = AlibabaClient(config)
    with pytest.raises(AlibabaAPIError) as exc_info:
        client.search_products("测试")
    
    assert "API调用失败" in str(exc_info.value)
    assert exc_info.value.original_error is not None


@patch('requests.post')
def test_call_api_http_error(mock_post):
    from src.alibaba_client import AlibabaClient
    
    mock_response = Mock()
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
    mock_post.return_value = mock_response
    
    config = Mock()
    config.get = Mock(side_effect=lambda section, key, default=None: {
        ("1688_api", "app_key"): "test_key",
        ("1688_api", "app_secret"): "test_secret",
        ("1688_api", "access_token"): "test_token"
    }.get((section, key), default))
    
    client = AlibabaClient(config)
    with pytest.raises(AlibabaAPIError) as exc_info:
        client.search_products("测试")
    
    assert "API调用失败" in str(exc_info.value)


@patch('requests.post')
def test_call_api_json_decode_error(mock_post):
    from src.alibaba_client import AlibabaClient
    
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.side_effect = ValueError("Invalid JSON")
    mock_post.return_value = mock_response
    
    config = Mock()
    config.get = Mock(side_effect=lambda section, key, default=None: {
        ("1688_api", "app_key"): "test_key",
        ("1688_api", "app_secret"): "test_secret",
        ("1688_api", "access_token"): "test_token"
    }.get((section, key), default))
    
    client = AlibabaClient(config)
    with pytest.raises(AlibabaAPIError) as exc_info:
        client.search_products("测试")
    
    assert "API响应JSON解析失败" in str(exc_info.value)


def test_search_products_empty_response():
    from src.alibaba_client import AlibabaClient
    
    config = Mock()
    config.get = Mock(side_effect=lambda section, key, default=None: {
        ("1688_api", "app_key"): "test_key",
        ("1688_api", "app_secret"): "test_secret",
        ("1688_api", "access_token"): "test_token"
    }.get((section, key), default))
    
    client = AlibabaClient(config)
    
    with patch.object(client, '_call_api', return_value={"result": {"success": False}}):
        products = client.search_products("测试")
        assert len(products) == 0
    
    with patch.object(client, '_call_api', return_value={"result": {"success": True, "data": []}}):
        products = client.search_products("测试")
        assert len(products) == 0
    
    with patch.object(client, '_call_api', return_value={"result": {}}):
        products = client.search_products("测试")
        assert len(products) == 0


def test_get_auth_url():
    from src.alibaba_client import AlibabaClient
    
    config = Mock()
    config.get = Mock(side_effect=lambda section, key, default=None: {
        ("1688_api", "app_key"): "test_key",
        ("1688_api", "app_secret"): "test_secret",
        ("1688_api", "access_token"): "test_token",
        ("1688_api", "auth_url"): "https://custom.auth.url"
    }.get((section, key), default))
    
    client = AlibabaClient(config)
    assert client.get_auth_url() == "https://custom.auth.url"
    
    config2 = Mock()
    config2.get = Mock(side_effect=lambda section, key, default=None: {
        ("1688_api", "app_key"): "test_key",
        ("1688_api", "app_secret"): "test_secret",
        ("1688_api", "access_token"): "test_token"
    }.get((section, key), default or "https://auth.1688.com/oauth/authorize"))
    
    client2 = AlibabaClient(config2)
    assert client2.get_auth_url() == "https://auth.1688.com/oauth/authorize"