import json
from typing import List, Dict, Any
from openai import OpenAI
from src.product_model import Product

class LLMAgent:
    def __init__(self, config_manager):
        self.config = config_manager
        self.provider = self.config.get("llm", "provider", "openai")
        self.api_key = self.config.get("llm", "api_key", "")
        self.base_url = self.config.get("llm", "base_url", "https://api.openai.com/v1")
        self.model = self.config.get("llm", "model", "gpt-3.5-turbo")
        self.temperature = float(self.config.get("llm", "temperature", 0.7))
        self.max_tokens = int(self.config.get("llm", "max_tokens", 500))
        
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        if self.provider == "ollama":
            ollama_config = self.config.get("agents", "ollama", {})
            if not isinstance(ollama_config, dict):
                ollama_config = {}
            base_url = ollama_config.get("base_url", "http://localhost:11434/v1")
            model = ollama_config.get("model", "llama2")
            self.client = OpenAI(base_url=base_url, api_key="not-needed")
            self.model = model
        elif self.provider == "deepseek":
            deepseek_config = self.config.get("agents", "deepseek", {})
            if not isinstance(deepseek_config, dict):
                deepseek_config = {}
            base_url = deepseek_config.get("base_url", "https://api.deepseek.com/v1")
            model = deepseek_config.get("model", "deepseek-chat")
            self.client = OpenAI(base_url=base_url, api_key=self.api_key)
            self.model = model
        elif self.provider == "qwen":
            qwen_config = self.config.get("agents", "qwen", {})
            if not isinstance(qwen_config, dict):
                qwen_config = {}
            base_url = qwen_config.get("base_url", "https://dashscope.aliyuncs.com/compatible-mode/v1")
            model = qwen_config.get("model", "qwen-turbo")
            self.client = OpenAI(base_url=base_url, api_key=self.api_key)
            self.model = model
        else:  # openai兼容
            self.client = OpenAI(base_url=self.base_url, api_key=self.api_key)
    
    def analyze_products(self, products: List[Product], purpose: str) -> Dict[str, Any]:
        if not products:
            return {"error": "没有可分析的商品"}
        
        if not self.client or (self.provider != "ollama" and not self.api_key):
            return {"error": "LLM未配置"}
        
        products_info = []
        for i, product in enumerate(products):
            products_info.append(
                f"{i+1}. {product.title}\n"
                f"   价格: {product.price or '未知'}\n"
                f"   描述: {product.description}\n"
                f"   卖家: {product.seller or '未知'}\n"
                f"   链接: {product.url}"
            )
        
        system_prompt = """你是一个专业的商品推荐助手。请分析以下商品，根据用户的使用目的推荐最合适的一个商品。

请以JSON格式返回结果，包含以下字段：
- "recommended_index": 推荐商品的索引（从0开始）
- "reason": 推荐理由（中文，100-200字）
- "summary": 商品特点总结（中文，50-100字）"""
        
        user_prompt = f"""用户使用目的：{purpose}

待分析的商品列表：
{chr(10).join(products_info)}

请根据用户的使用目的，从以上商品中选择最合适的一个。考虑因素包括：价格合理性、商品描述匹配度、卖家信誉等。"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"}
            )
            
            result_text = response.choices[0].message.content
            result = json.loads(result_text)
            
            recommended_idx = result.get("recommended_index", 0)
            if recommended_idx < 0 or recommended_idx >= len(products):
                recommended_idx = 0
            
            return {
                "recommended_index": recommended_idx,
                "recommended_product": products[recommended_idx].to_dict(),
                "reason": result.get("reason", "无推荐理由"),
                "summary": result.get("summary", ""),
                "raw_response": result_text
            }
            
        except Exception as e:
            return {"error": f"LLM分析失败: {str(e)}"}
    
    def test_connection(self) -> bool:
        try:
            if not self.client or (self.provider != "ollama" and not self.api_key):
                return False
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "测试连接"}],
                max_tokens=10
            )
            return response.choices[0].message.content is not None
        except Exception:
            return False