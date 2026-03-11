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
    API_FORMAT = "json"
    API_VERSION = "2.0"
    SIGN_METHOD = "hmac-sha1"
    
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
            "format": self.API_FORMAT,
            "v": self.API_VERSION,
            "sign_method": self.SIGN_METHOD,
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
        except requests.exceptions.Timeout as e:
            logging.error(f"API调用超时: {e}")
            raise AlibabaAPIError(f"API调用超时（{self.DEFAULT_TIMEOUT}秒），请检查网络连接", original_error=e)
        except requests.exceptions.SSLError as e:
            logging.error(f"SSL证书错误: {e}")
            raise AlibabaAPIError("SSL证书验证失败，请检查系统时间或代理设置", original_error=e)
        except requests.exceptions.ConnectionError as e:
            logging.error(f"网络连接错误: {e}")
            raise AlibabaAPIError("网络连接失败，请检查网络设置", original_error=e)
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if e.response else "未知"
            logging.error(f"HTTP错误 {status_code}: {e}")
            error_msg = f"HTTP错误 {status_code}"
            if isinstance(status_code, int):
                if status_code == 401:
                    error_msg += "：认证失败，请检查API密钥和访问令牌"
                elif status_code == 403:
                    error_msg += "：权限不足，请检查API访问权限"
                elif status_code == 404:
                    error_msg += "：API端点不存在"
                elif status_code == 429:
                    error_msg += "：请求过于频繁，请稍后再试"
                elif status_code >= 500:
                    error_msg += "：服务器内部错误"
            raise AlibabaAPIError(error_msg, original_error=e)
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
        # 输入验证
        if not keyword or not keyword.strip():
            logging.warning("搜索关键词为空")
            return []
        
        if limit <= 0:
            limit = 10
        elif limit > 50:
            logging.warning(f"请求数量{limit}超过限制，调整为50")
            limit = 50
        
        params = {
            "keywords": keyword.strip(),
            "pageSize": str(limit)
        }
        
        try:
            result = self._call_api(self.API_SEARCH_PRODUCTS, params)
        except AlibabaAPIError as e:
            logging.error(f"搜索商品失败: {e}")
            raise
        
        products = []
        
        # 处理多种API响应格式
        response_data = result
        if isinstance(result, dict):
            if "result" in result:
                response_data = result["result"]
            elif "error" in result:
                error_msg = result.get("error", {}).get("message", "未知错误")
                logging.error(f"API返回错误: {error_msg}")
                return products
        
        if isinstance(response_data, dict):
            if response_data.get("success", False):
                data = response_data.get("data", [])
                if not isinstance(data, list):
                    logging.warning(f"API返回的data字段不是列表: {type(data)}")
                    data = []
                
                for item in data[:limit]:
                    if not isinstance(item, dict):
                        continue
                    try:
                        product = Product(
                            title=item.get("title", ""),
                            description=item.get("description", ""),
                            url=item.get("url", ""),
                            price=item.get("price", ""),
                            seller=item.get("seller", ""),
                            image_url=item.get("imageUrl", "")
                        )
                        products.append(product)
                    except Exception as e:
                        logging.warning(f"创建商品对象失败: {e}, 原始数据: {item}")
            else:
                error_code = response_data.get("errorCode", "未知")
                error_msg = response_data.get("errorMessage", "请求失败")
                logging.error(f"API请求失败: {error_code} - {error_msg}")
        else:
            logging.warning(f"API响应格式异常: {type(response_data)}")
        
        return products
    
    def get_auth_url(self):
        return self.auth_url