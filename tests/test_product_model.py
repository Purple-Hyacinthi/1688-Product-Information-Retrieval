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