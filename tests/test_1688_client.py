# tests/test_1688_client.py
import pytest
import requests
from unittest.mock import Mock, patch
from src.product_model import Product
from src.config_manager import ConfigManager
from src.alibaba_client import AlibabaAPIError

def create_mock_config(access_token="test_token", auth_url=None):
    mock_config = Mock()
    def get_side_effect(section, key, default=None):
        mapping = {
            ("1688_api", "app_key"): "test_key",
            ("1688_api", "app_secret"): "test_secret",
            ("1688_api", "access_token"): access_token,
            ("1688_api", "api_endpoint"): "https://gw.open.1688.com/openapi",
        }
        if auth_url is not None:
            mapping[("1688_api", "auth_url")] = auth_url
        return mapping.get((section, key), default)
    mock_config.get = Mock(side_effect=get_side_effect)
    return mock_config

def test_alibaba_client_initialization():
    from src.alibaba_client import AlibabaClient
    config = create_mock_config()
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
    
    config = create_mock_config()
    
    client = AlibabaClient(config)
    products = client.search_products("测试商品", "测试用途", limit=10)
    
    assert len(products) == 1
    assert products[0].title == "测试商品"
    assert products[0].url == "https://detail.1688.com/test"


@patch('requests.post')
def test_call_api_request_exception(mock_post):
    from src.alibaba_client import AlibabaClient
    
    mock_post.side_effect = requests.exceptions.RequestException("网络错误")
    
    config = create_mock_config()
    
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
    
    config = create_mock_config()
    
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
    
    config = create_mock_config()
    
    client = AlibabaClient(config)
    with pytest.raises(AlibabaAPIError) as exc_info:
        client.search_products("测试")
    
    assert "API响应JSON解析失败" in str(exc_info.value)


def test_search_products_empty_response():
    from src.alibaba_client import AlibabaClient
    
    config = create_mock_config()
    
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
    
    config = create_mock_config(auth_url="https://custom.auth.url")
    
    client = AlibabaClient(config)
    assert client.get_auth_url() == "https://custom.auth.url"
    
    config2 = create_mock_config()
    
    client2 = AlibabaClient(config2)
    assert client2.get_auth_url() == "https://auth.1688.com/oauth/authorize"


def test_generate_signature():
    from src.alibaba_client import AlibabaClient
    
    config = create_mock_config()
    client = AlibabaClient(config)
    
    # 测试签名生成
    params = {
        "app_key": "test_key",
        "timestamp": "1234567890000",
        "format": AlibabaClient.API_FORMAT,
        "v": AlibabaClient.API_VERSION,
        "sign_method": AlibabaClient.SIGN_METHOD,
        "method": "test.method"
    }
    
    # 计算签名
    signature = client._generate_signature(params)
    
    # 验证签名长度和格式（base64）
    assert isinstance(signature, str)
    assert len(signature) > 0
    # 可以添加更精确的验证，例如与已知值比较
    # 但为了不暴露算法细节，我们至少确保它是base64编码
    try:
        import base64
        base64.b64decode(signature)
        assert True
    except Exception:
        assert False, "签名不是有效的base64编码"
    
    # 测试参数顺序不影响签名结果（排序后应该一致）
    params_shuffled = {
        "method": "test.method",
        "v": AlibabaClient.API_VERSION,
        "format": AlibabaClient.API_FORMAT,
        "timestamp": "1234567890000",
        "app_key": "test_key",
        "sign_method": AlibabaClient.SIGN_METHOD
    }
    signature2 = client._generate_signature(params_shuffled)
    assert signature == signature2, "参数排序应不影响签名"