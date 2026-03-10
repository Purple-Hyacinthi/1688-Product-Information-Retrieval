import pytest
from unittest.mock import Mock, patch
from src.product_model import Product
from src.llm_agent import LLMAgent

@patch('src.llm_agent.OpenAI')
def test_llm_agent_initialization(mock_openai):
    config = Mock()
    config.get = Mock(side_effect=lambda section, key, default=None: {
        ("llm", "provider"): "openai",
        ("llm", "api_key"): "test_key",
        ("llm", "base_url"): "https://api.openai.com/v1",
        ("llm", "model"): "gpt-3.5-turbo"
    }.get((section, key), default))
    
    mock_client = Mock()
    mock_openai.return_value = mock_client
    
    agent = LLMAgent(config)
    assert agent.provider == "openai"
    assert agent.api_key == "test_key"

@patch('src.llm_agent.OpenAI')
def test_analyze_products_mock(mock_openai):
    config = Mock()
    config.get = Mock(side_effect=lambda section, key, default=None: {
        ("llm", "provider"): "openai",
        ("llm", "api_key"): "test_key",
        ("llm", "base_url"): "https://api.openai.com/v1",
        ("llm", "model"): "gpt-3.5-turbo",
        ("llm", "temperature"): 0.7,
        ("llm", "max_tokens"): 500
    }.get((section, key), default))
    
    mock_client = Mock()
    mock_completion = Mock()
    mock_completion.choices = [Mock(message=Mock(content='{"recommended_index": 0, "reason": "测试推荐理由"}'))]
    mock_client.chat.completions.create.return_value = mock_completion
    mock_openai.return_value = mock_client
    
    agent = LLMAgent(config)
    
    products = [
        Product("商品1", "描述1", "https://example.com/1", "100元"),
        Product("商品2", "描述2", "https://example.com/2", "200元")
    ]
    
    result = agent.analyze_products(products, "测试用途")
    
    assert "recommended_index" in result
    assert "reason" in result
    assert result["recommended_index"] == 0