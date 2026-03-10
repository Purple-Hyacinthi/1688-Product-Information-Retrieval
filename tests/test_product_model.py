import pytest
from src.product_model import Product

def test_product_creation():
    product = Product(
        title="测试商品",
        description="这是一个测试商品",
        url="https://example.com",
        price="100元",
        seller="测试卖家"
    )
    assert product.title == "测试商品"
    assert product.description == "这是一个测试商品"
    assert product.url == "https://example.com"

def test_product_to_dict():
    product = Product(
        title="测试商品",
        description="描述",
        url="https://example.com",
        price="100元",
        seller="卖家"
    )
    data = product.to_dict()
    assert data["title"] == "测试商品"
    assert data["url"] == "https://example.com"

def test_from_dict():
    data = {
        "title": "商品标题",
        "description": "商品描述",
        "url": "https://example.com/product",
        "price": "200元",
        "seller": "卖家A",
        "image_url": "https://example.com/image.jpg"
    }
    product = Product.from_dict(data)
    assert product.title == "商品标题"
    assert product.description == "商品描述"
    assert product.url == "https://example.com/product"
    assert product.price == "200元"
    assert product.seller == "卖家A"
    assert product.image_url == "https://example.com/image.jpg"

def test_from_dict_missing_fields():
    data = {
        "title": "仅标题",
        "description": "",
        "url": ""
    }
    product = Product.from_dict(data)
    assert product.title == "仅标题"
    assert product.description == ""
    assert product.url == ""
    assert product.price is None
    assert product.seller is None
    assert product.image_url is None

def test_from_dict_invalid_data():
    with pytest.raises(TypeError, match="data必须是字典"):
        Product.from_dict(None)  # type: ignore
    with pytest.raises(TypeError, match="data必须是字典"):
        Product.from_dict("not a dict")  # type: ignore
    with pytest.raises(TypeError, match="data必须是字典"):
        Product.from_dict(123)  # type: ignore

def test_str_representation():
    product = Product(title="商品", description="描述", url="https://example.com", price="100元")
    assert str(product) == "商品 - 100元"
    
    product_no_price = Product(title="商品", description="描述", url="https://example.com")
    assert str(product_no_price) == "商品 - 价格未知"
    
    product_empty_title = Product(title="", description="描述", url="https://example.com", price="50元")
    assert str(product_empty_title) == " - 50元"
    
    product_no_title = Product(title="", description="描述", url="https://example.com")
    assert str(product_no_title) == " - 价格未知"

def test_input_validation():
    with pytest.raises(TypeError, match="title必须是字符串"):
        Product(title=123, description="描述", url="https://example.com")  # type: ignore
    with pytest.raises(TypeError, match="description必须是字符串"):
        Product(title="标题", description=456, url="https://example.com")  # type: ignore
    with pytest.raises(TypeError, match="url必须是字符串"):
        Product(title="标题", description="描述", url=None)  # type: ignore
    # 可选参数可以接受None
    product = Product(title="标题", description="描述", url="https://example.com", price=None)
    assert product.price is None