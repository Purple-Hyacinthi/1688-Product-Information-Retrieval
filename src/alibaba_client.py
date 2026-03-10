# src/alibaba_client.py
import time
import hashlib
import hmac
import base64
import json
import logging
import requests
from urllib.parse import quote
from typing import List, Optional
from src.product_model import Product


class AlibabaAPIError(Exception):
    def __init__(self, message, original_error=None):
        super().__init__(message)
        self.original_error = original_error

class AlibabaClient:
    DEFAULT_TIMEOUT = 30
    API_SEARCH_PRODUCTS = "com.alibaba.product:alibaba.category.searchSPUInfo-1"
    
    def __init__(self, config_manager):
        self.config = config_manager
        self.api_endpoint = self.config.get("1688_api", "api_endpoint", "https://gw.open.1688.com/openapi")
        self.app_key = self.config.get("1688_api", "app_key")
        self.app_secret = self.config.get("1688_api", "app_secret")
        self.access_token = self.config.get("1688_api", "access_token")
        self.auth_url = self.config.get("1688_api", "auth_url", "https://auth.1688.com/oauth/authorize")
    
    def _generate_signature(self, params):
        sorted_params = sorted(params.items())
        canonicalized_query = ""
        for key, value in sorted_params:
            canonicalized_query += f"{key}{str(value)}"
        
        signature = hmac.new(
            self.app_secret.encode('utf-8'),
            canonicalized_query.encode('utf-8'),
            hashlib.sha1
        ).digest()
        
        return base64.b64encode(signature).decode('utf-8')
    
    def _call_api(self, api_name, params=None):
        if params is None:
            params = {}
        
        timestamp = str(int(time.time() * 1000))
        
        base_params = {
            "app_key": self.app_key,
            "timestamp": timestamp,
            "format": "json",
            "v": "2.0",
            "sign_method": "hmac-sha1",
            "method": api_name
        }
        
        all_params = {**base_params, **params}
        signature = self._generate_signature(all_params)
        all_params["sign"] = signature
        
        if self.access_token:
            all_params["access_token"] = self.access_token
        
        try:
            response = requests.post(self.api_endpoint, data=all_params, timeout=self.DEFAULT_TIMEOUT)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"API调用失败: {e}")
            raise AlibabaAPIError(f"API调用失败: {e}", original_error=e)
        except (json.JSONDecodeError, ValueError) as e:
            logging.error(f"API响应JSON解析失败: {e}")
            raise AlibabaAPIError(f"API响应JSON解析失败: {e}", original_error=e)
    
    def search_products(self, keyword: str, purpose: str = "", limit: int = 10) -> List[Product]:
        """
        搜索1688商品
        
        Args:
            keyword: 搜索关键词
            purpose: 预留参数，供将来按用途筛选使用（当前未使用）
            limit: 返回商品数量限制
        
        Returns:
            商品对象列表
        """
        params = {
            "keywords": keyword,
            "pageSize": str(limit)
        }
        
        result = self._call_api(self.API_SEARCH_PRODUCTS, params)
        
        products = []
        if isinstance(result, dict) and "result" in result:
            response_data = result["result"]
        else:
            response_data = result
        if isinstance(response_data, dict) and response_data.get("success", False):
            data = response_data.get("data", [])
            for item in data[:limit]:
                product = Product(
                    title=item.get("title", ""),
                    description=item.get("description", ""),
                    url=item.get("url", ""),
                    price=item.get("price", ""),
                    seller=item.get("seller", ""),
                    image_url=item.get("imageUrl", "")
                )
                products.append(product)
        
        return products
    
    def get_auth_url(self):
        return self.auth_url