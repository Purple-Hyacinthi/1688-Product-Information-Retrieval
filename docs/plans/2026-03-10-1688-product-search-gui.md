# 1688商品搜索GUI实现计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 创建一个Python Tkinter图形化脚本，允许用户输入商品名和用途，通过1688 API搜索商品，显示结果（限10条），并支持配置LLM智能体模式自动推荐最佳商品。

**Architecture:** 模块化设计，包括配置管理、1688 API客户端、LLM代理管理器、商品数据模型和Tkinter GUI主界面。支持多种LLM API（OpenAI格式、DeepSeek、本地Ollama、千问）。

**Tech Stack:** Python 3.8+, Tkinter (内置), requests (HTTP客户端), openai (LLM客户端), json (配置存储)

---

### Task 1: 项目初始化与依赖

**Files:**
- Create: `requirements.txt`
- Create: `README.md`
- Create: `config/config_template.json`

**Step 1: 创建项目依赖文件**

```python
# requirements.txt
requests>=2.31.0
openai>=1.0.0
pytest>=7.4.0
```

**Step 2: 创建项目说明文档**

```markdown
# 1688商品搜索GUI工具

一个图形化工具，通过1688 API搜索商品并智能推荐。

## 功能
1. 输入商品名称和用途
2. 调用1688 API搜索商品（最多10条）
3. 显示商品简介和链接
4. 智能体模式：LLM分析商品并推荐最佳选项

## 配置
1. 1688 API密钥（需自行申请）
2. LLM API配置（支持OpenAI格式、DeepSeek、本地Ollama、千问）
```

**Step 3: 创建配置模板**

```json
{
  "1688_api": {
    "app_key": "",
    "app_secret": "",
    "access_token": "",
    "refresh_token": ""
  },
  "llm": {
    "provider": "openai",
    "api_key": "",
    "base_url": "https://api.openai.com/v1",
    "model": "gpt-3.5-turbo"
  },
  "agents": {
    "deepseek": {
      "base_url": "https://api.deepseek.com/v1",
      "model": "deepseek-chat"
    },
    "qwen": {
      "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
      "model": "qwen-turbo"
    },
    "ollama": {
      "base_url": "http://localhost:11434/v1",
      "model": "llama2"
    }
  }
}
```

**Step 4: 提交初始化文件**

```bash
git add requirements.txt README.md config/config_template.json
git commit -m "chore: 初始化项目结构和依赖"
```

---

### Task 2: 商品数据模型

**Files:**
- Create: `src/product_model.py`
- Create: `tests/test_product_model.py`

**Step 1: 编写商品模型测试**

```python
# tests/test_product_model.py
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
```

**Step 2: 运行测试验证失败**

```bash
pytest tests/test_product_model.py -v
```
预期：FAIL，因为product_model.py不存在

**Step 3: 实现商品数据模型**

```python
# src/product_model.py
class Product:
    def __init__(self, title, description, url, price=None, seller=None, image_url=None):
        self.title = title
        self.description = description
        self.url = url
        self.price = price
        self.seller = seller
        self.image_url = image_url
    
    def to_dict(self):
        return {
            "title": self.title,
            "description": self.description,
            "url": self.url,
            "price": self.price,
            "seller": self.seller,
            "image_url": self.image_url
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            title=data.get("title", ""),
            description=data.get("description", ""),
            url=data.get("url", ""),
            price=data.get("price"),
            seller=data.get("seller"),
            image_url=data.get("image_url")
        )
    
    def __str__(self):
        return f"{self.title} - {self.price or '价格未知'}"
```

**Step 4: 运行测试验证通过**

```bash
pytest tests/test_product_model.py -v
```
预期：PASS

**Step 5: 提交商品模型**

```bash
git add src/product_model.py tests/test_product_model.py
git commit -m "feat: 添加商品数据模型"
```

---

### Task 3: 配置管理器

**Files:**
- Create: `src/config_manager.py`
- Create: `tests/test_config_manager.py`
- Create: `config/settings.json`

**Step 1: 编写配置管理器测试**

```python
# tests/test_config_manager.py
import os
import json
import tempfile
import pytest
from src.config_manager import ConfigManager

def test_config_manager_creation():
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = os.path.join(tmpdir, "config.json")
        config = ConfigManager(config_path)
        assert config.config_path == config_path

def test_load_default_config():
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = os.path.join(tmpdir, "config.json")
        config = ConfigManager(config_path)
        default_config = config.load_config()
        assert "1688_api" in default_config
        assert "llm" in default_config

def test_save_and_load_config():
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = os.path.join(tmpdir, "config.json")
        config = ConfigManager(config_path)
        
        test_data = {"test": "value"}
        config.save_config(test_data)
        
        loaded = config.load_config()
        assert loaded["test"] == "value"
```

**Step 2: 运行测试验证失败**

```bash
pytest tests/test_config_manager.py -v
```
预期：FAIL，因为config_manager.py不存在

**Step 3: 实现配置管理器**

```python
# src/config_manager.py
import os
import json
from pathlib import Path

class ConfigManager:
    def __init__(self, config_path="config/settings.json"):
        self.config_path = config_path
        self._ensure_config_dir()
        self._ensure_default_config()
    
    def _ensure_config_dir(self):
        config_dir = os.path.dirname(self.config_path)
        if config_dir and not os.path.exists(config_dir):
            os.makedirs(config_dir)
    
    def _ensure_default_config(self):
        if not os.path.exists(self.config_path):
            self.save_config(self._get_default_config())
    
    def _get_default_config(self):
        return {
            "1688_api": {
                "app_key": "",
                "app_secret": "",
                "access_token": "",
                "refresh_token": "",
                "api_endpoint": "https://gw.open.1688.com/openapi"
            },
            "llm": {
                "provider": "openai",
                "api_key": "",
                "base_url": "https://api.openai.com/v1",
                "model": "gpt-3.5-turbo",
                "temperature": 0.7,
                "max_tokens": 500
            },
            "ui": {
                "window_size": "1000x700",
                "theme": "light"
            }
        }
    
    def load_config(self):
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return self._get_default_config()
    
    def save_config(self, config_data):
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
    
    def update_section(self, section, data):
        config = self.load_config()
        if section not in config:
            config[section] = {}
        config[section].update(data)
        self.save_config(config)
    
    def get(self, section, key, default=None):
        config = self.load_config()
        return config.get(section, {}).get(key, default)
```

**Step 4: 创建默认配置文件**

```bash
mkdir -p config
cp config/config_template.json config/settings.json
```

**Step 5: 运行测试验证通过**

```bash
pytest tests/test_config_manager.py -v
```
预期：PASS

**Step 6: 提交配置管理器**

```bash
git add src/config_manager.py tests/test_config_manager.py config/settings.json
git commit -m "feat: 添加配置管理器"
```

---

### Task 4: 1688 API客户端

**Files:**
- Create: `src/1688_client.py`
- Create: `tests/test_1688_client.py`

**Step 1: 编写1688 API客户端测试**

```python
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
```

**Step 2: 运行测试验证失败**

```bash
pytest tests/test_1688_client.py -v
```
预期：FAIL，因为alibaba_client.py不存在

**Step 3: 实现1688 API客户端**

```python
# src/alibaba_client.py
import time
import hashlib
import hmac
import base64
import json
import requests
from urllib.parse import quote
from typing import List, Optional
from src.product_model import Product

class AlibabaClient:
    def __init__(self, config_manager):
        self.config = config_manager
        self.api_endpoint = self.config.get("1688_api", "api_endpoint", "https://gw.open.1688.com/openapi")
        self.app_key = self.config.get("1688_api", "app_key")
        self.app_secret = self.config.get("1688_api", "app_secret")
        self.access_token = self.config.get("1688_api", "access_token")
    
    def _generate_signature(self, params):
        sorted_params = sorted(params.items())
        canonicalized_query = ""
        for key, value in sorted_params:
            canonicalized_query += f"{key}{value}"
        
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
            response = requests.post(self.api_endpoint, data=all_params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API调用失败: {e}")
            return {"error": str(e)}
    
    def search_products(self, keyword: str, purpose: str = "", limit: int = 10) -> List[Product]:
        params = {
            "keywords": keyword,
            "pageSize": str(limit)
        }
        
        result = self._call_api("com.alibaba.product:alibaba.category.searchSPUInfo-1", params)
        
        products = []
        if result.get("success", False):
            data = result.get("data", [])
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
        return "https://auth.1688.com/oauth/authorize"
```

**Step 4: 运行测试验证通过**

```bash
pytest tests/test_1688_client.py -v
```
预期：PASS（模拟测试）

**Step 5: 提交API客户端**

```bash
git add src/alibaba_client.py tests/test_1688_client.py
git commit -m "feat: 添加1688 API客户端"
```

---

### Task 5: LLM代理管理器

**Files:**
- Create: `src/llm_agent.py`
- Create: `tests/test_llm_agent.py`

**Step 1: 编写LLM代理测试**

```python
# tests/test_llm_agent.py
import pytest
from unittest.mock import Mock, patch
from src.product_model import Product
from src.llm_agent import LLMAgent

def test_llm_agent_initialization():
    config = Mock()
    config.get = Mock(side_effect=lambda section, key, default=None: {
        ("llm", "provider"): "openai",
        ("llm", "api_key"): "test_key",
        ("llm", "base_url"): "https://api.openai.com/v1",
        ("llm", "model"): "gpt-3.5-turbo"
    }.get((section, key), default))
    
    agent = LLMAgent(config)
    assert agent.provider == "openai"
    assert agent.api_key == "test_key"

@patch('openai.OpenAI')
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
```

**Step 2: 运行测试验证失败**

```bash
pytest tests/test_llm_agent.py -v
```
预期：FAIL，因为llm_agent.py不存在

**Step 3: 实现LLM代理管理器**

```python
# src/llm_agent.py
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
            base_url = self.config.get("agents", "ollama", {}).get("base_url", "http://localhost:11434/v1")
            model = self.config.get("agents", "ollama", {}).get("model", "llama2")
            self.client = OpenAI(base_url=base_url, api_key="not-needed")
            self.model = model
        elif self.provider == "deepseek":
            base_url = self.config.get("agents", "deepseek", {}).get("base_url", "https://api.deepseek.com/v1")
            model = self.config.get("agents", "deepseek", {}).get("model", "deepseek-chat")
            self.client = OpenAI(base_url=base_url, api_key=self.api_key)
            self.model = model
        elif self.provider == "qwen":
            base_url = self.config.get("agents", "qwen", {}).get("base_url", "https://dashscope.aliyuncs.com/compatible-mode/v1")
            model = self.config.get("agents", "qwen", {}).get("model", "qwen-turbo")
            self.client = OpenAI(base_url=base_url, api_key=self.api_key)
            self.model = model
        else:  # openai兼容
            self.client = OpenAI(base_url=self.base_url, api_key=self.api_key)
    
    def analyze_products(self, products: List[Product], purpose: str) -> Dict[str, Any]:
        if not products:
            return {"error": "没有可分析的商品"}
        
        if not self.client or not self.api_key:
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
                "recommended_product": products[recommended_idx],
                "reason": result.get("reason", "无推荐理由"),
                "summary": result.get("summary", ""),
                "raw_response": result_text
            }
            
        except Exception as e:
            return {"error": f"LLM分析失败: {str(e)}"}
    
    def test_connection(self) -> bool:
        try:
            if not self.client or not self.api_key:
                return False
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "测试连接"}],
                max_tokens=10
            )
            return response.choices[0].message.content is not None
        except Exception:
            return False
```

**Step 4: 运行测试验证通过**

```bash
pytest tests/test_llm_agent.py -v
```
预期：PASS（模拟测试）

**Step 5: 提交LLM代理管理器**

```bash
git add src/llm_agent.py tests/test_llm_agent.py
git commit -m "feat: 添加LLM代理管理器"
```

---

### Task 6: Tkinter主窗口

**Files:**
- Create: `src/main_window.py`
- Create: `main.py`

**Step 1: 创建主窗口测试**

```python
# tests/test_main_window.py
import pytest
import tkinter as tk
from unittest.mock import Mock
from src.main_window import MainWindow

def test_main_window_creation():
    root = tk.Tk()
    root.withdraw()  # 隐藏窗口
    
    config = Mock()
    alibaba_client = Mock()
    llm_agent = Mock()
    
    window = MainWindow(root, config, alibaba_client, llm_agent)
    
    assert window.root == root
    assert window.config == config
    assert window.alibaba_client == alibaba_client
    assert window.llm_agent == llm_agent
    
    root.destroy()
```

**Step 2: 运行测试验证失败**

```bash
pytest tests/test_main_window.py -v
```
预期：FAIL，因为main_window.py不存在

**Step 3: 实现Tkinter主窗口**

```python
# src/main_window.py
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
from typing import List, Optional
from src.product_model import Product

class MainWindow:
    def __init__(self, root, config_manager, alibaba_client, llm_agent):
        self.root = root
        self.config = config_manager
        self.alibaba_client = alibaba_client
        self.llm_agent = llm_agent
        
        self.root.title("1688商品搜索工具")
        self.root.geometry(self.config.get("ui", "window_size", "1000x700"))
        
        self.products: List[Product] = []
        self.current_purpose: str = ""
        
        self._setup_ui()
        self._load_config_to_ui()
    
    def _setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # 搜索区域
        ttk.Label(main_frame, text="商品名称:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.product_entry = ttk.Entry(main_frame, width=50)
        self.product_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        
        ttk.Label(main_frame, text="商品用途:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.purpose_entry = ttk.Entry(main_frame, width=50)
        self.purpose_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        
        self.search_button = ttk.Button(main_frame, text="搜索商品", command=self._search_products)
        self.search_button.grid(row=0, column=2, rowspan=2, padx=(10, 0), pady=5, sticky=tk.N)
        
        # 结果区域
        result_frame = ttk.LabelFrame(main_frame, text="搜索结果（最多10条）", padding="10")
        result_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
        
        # 创建Treeview显示结果
        columns = ("#", "商品名称", "价格", "卖家", "描述")
        self.tree = ttk.Treeview(result_frame, columns=columns, show="headings", height=8)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        self.tree.column("#", width=50)
        self.tree.column("商品名称", width=200)
        self.tree.column("价格", width=100)
        self.tree.column("卖家", width=150)
        self.tree.column("描述", width=300)
        
        tree_scroll = ttk.Scrollbar(result_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 智能体区域
        agent_frame = ttk.LabelFrame(main_frame, text="智能体推荐", padding="10")
        agent_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        agent_frame.columnconfigure(0, weight=1)
        
        self.agent_enabled = tk.BooleanVar(value=False)
        agent_check = ttk.Checkbutton(
            agent_frame, 
            text="启用智能体模式", 
            variable=self.agent_enabled,
            command=self._toggle_agent_mode
        )
        agent_check.grid(row=0, column=0, sticky=tk.W)
        
        self.agent_button = ttk.Button(
            agent_frame, 
            text="开始智能推荐", 
            command=self._analyze_with_agent,
            state=tk.DISABLED
        )
        self.agent_button.grid(row=0, column=1, padx=(10, 0))
        
        self.recommendation_text = scrolledtext.ScrolledText(
            agent_frame, 
            width=80, 
            height=8,
            wrap=tk.WORD
        )
        self.recommendation_text.grid(row=1, column=0, columnspan=2, pady=(10, 0), sticky=(tk.W, tk.E))
        
        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # 配置按钮
        config_button = ttk.Button(main_frame, text="配置", command=self._open_config_window)
        config_button.grid(row=5, column=2, pady=(10, 0), sticky=tk.E)
    
    def _load_config_to_ui(self):
        pass
    
    def _search_products(self):
        keyword = self.product_entry.get().strip()
        purpose = self.purpose_entry.get().strip()
        
        if not keyword:
            messagebox.showwarning("输入错误", "请输入商品名称")
            return
        
        self.current_purpose = purpose
        self.status_var.set("正在搜索商品...")
        self.search_button.config(state=tk.DISABLED)
        
        thread = threading.Thread(target=self._perform_search, args=(keyword, purpose))
        thread.daemon = True
        thread.start()
    
    def _perform_search(self, keyword, purpose):
        try:
            self.products = self.alibaba_client.search_products(keyword, purpose, limit=10)
            
            self.root.after(0, self._update_results)
            self.root.after(0, lambda: self.status_var.set(f"找到 {len(self.products)} 个商品"))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("搜索错误", f"搜索失败: {str(e)}"))
            self.root.after(0, lambda: self.status_var.set("搜索失败"))
        
        finally:
            self.root.after(0, lambda: self.search_button.config(state=tk.NORMAL))
    
    def _update_results(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for i, product in enumerate(self.products):
            self.tree.insert("", "end", values=(
                i+1,
                product.title[:50] + "..." if len(product.title) > 50 else product.title,
                product.price or "未知",
                product.seller or "未知",
                product.description[:80] + "..." if product.description and len(product.description) > 80 else product.description or ""
            ))
    
    def _toggle_agent_mode(self):
        if self.agent_enabled.get():
            self.agent_button.config(state=tk.NORMAL)
        else:
            self.agent_button.config(state=tk.DISABLED)
            self.recommendation_text.delete(1.0, tk.END)
    
    def _analyze_with_agent(self):
        if not self.products:
            messagebox.showwarning("无数据", "请先搜索商品")
            return
        
        if not self.llm_agent.test_connection():
            messagebox.showwarning("连接失败", "LLM连接失败，请检查配置")
            return
        
        self.status_var.set("智能体分析中...")
        self.agent_button.config(state=tk.DISABLED)
        
        thread = threading.Thread(target=self._perform_analysis)
        thread.daemon = True
        thread.start()
    
    def _perform_analysis(self):
        try:
            result = self.llm_agent.analyze_products(self.products, self.current_purpose)
            
            if "error" in result:
                self.root.after(0, lambda: messagebox.showerror("分析错误", result["error"]))
            else:
                self.root.after(0, lambda: self._display_recommendation(result))
            
            self.root.after(0, lambda: self.status_var.set("分析完成"))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("分析错误", f"分析失败: {str(e)}"))
            self.root.after(0, lambda: self.status_var.set("分析失败"))
        
        finally:
            self.root.after(0, lambda: self.agent_button.config(state=tk.NORMAL))
    
    def _display_recommendation(self, result):
        product = result["recommended_product"]
        reason = result["reason"]
        summary = result["summary"]
        
        text = f"推荐商品: {product.title}\n"
        text += f"价格: {product.price or '未知'}\n"
        text += f"卖家: {product.seller or '未知'}\n"
        text += f"链接: {product.url}\n\n"
        text += f"推荐理由:\n{reason}\n\n"
        
        if summary:
            text += f"商品特点:\n{summary}\n\n"
        
        text += f"点击链接查看详情: {product.url}"
        
        self.recommendation_text.delete(1.0, tk.END)
        self.recommendation_text.insert(1.0, text)
    
    def _open_config_window(self):
        from src.config_window import ConfigWindow
        config_window = ConfigWindow(self.root, self.config)
```

**Step 4: 创建主程序入口**

```python
# main.py
import tkinter as tk
from src.config_manager import ConfigManager
from src.alibaba_client import AlibabaClient
from src.llm_agent import LLMAgent
from src.main_window import MainWindow

def main():
    root = tk.Tk()
    
    config = ConfigManager()
    alibaba_client = AlibabaClient(config)
    llm_agent = LLMAgent(config)
    
    app = MainWindow(root, config, alibaba_client, llm_agent)
    
    root.mainloop()

if __name__ == "__main__":
    main()
```

**Step 5: 运行简单测试**

```bash
python -c "import tkinter; print('Tkinter可用')"
```
预期：显示"Tkinter可用"

**Step 6: 提交主窗口**

```bash
git add src/main_window.py main.py tests/test_main_window.py
git commit -m "feat: 添加Tkinter主窗口和主程序"
```

---

### Task 7: 配置窗口

**Files:**
- Create: `src/config_window.py`
- Create: `tests/test_config_window.py`

**Step 1: 编写配置窗口测试**

```python
# tests/test_config_window.py
import pytest
import tkinter as tk
from unittest.mock import Mock
from src.config_window import ConfigWindow

def test_config_window_creation():
    root = tk.Tk()
    root.withdraw()
    
    config = Mock()
    config.load_config = Mock(return_value={
        "1688_api": {"app_key": "", "app_secret": ""},
        "llm": {"api_key": "", "base_url": ""}
    })
    config.save_config = Mock()
    
    window = ConfigWindow(root, config)
    
    assert window.parent == root
    assert window.config == config
    
    window.destroy()
    root.destroy()
```

**Step 2: 运行测试验证失败**

```bash
pytest tests/test_config_window.py -v
```
预期：FAIL，因为config_window.py不存在

**Step 3: 实现配置窗口**

```python
# src/config_window.py
import tkinter as tk
from tkinter import ttk, messagebox

class ConfigWindow:
    def __init__(self, parent, config_manager):
        self.parent = parent
        self.config = config_manager
        
        self.window = tk.Toplevel(parent)
        self.window.title("配置")
        self.window.geometry("600x500")
        self.window.transient(parent)
        self.window.grab_set()
        
        self._setup_ui()
        self._load_config()
    
    def _setup_ui(self):
        notebook = ttk.Notebook(self.window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 1688 API配置页
        api_frame = ttk.Frame(notebook, padding="10")
        notebook.add(api_frame, text="1688 API")
        
        ttk.Label(api_frame, text="App Key:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.app_key_entry = ttk.Entry(api_frame, width=50, show="*")
        self.app_key_entry.grid(row=0, column=1, pady=5, padx=(5, 0))
        
        ttk.Label(api_frame, text="App Secret:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.app_secret_entry = ttk.Entry(api_frame, width=50, show="*")
        self.app_secret_entry.grid(row=1, column=1, pady=5, padx=(5, 0))
        
        ttk.Label(api_frame, text="Access Token:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.access_token_entry = ttk.Entry(api_frame, width=50, show="*")
        self.access_token_entry.grid(row=2, column=1, pady=5, padx=(5, 0))
        
        ttk.Label(api_frame, text="Refresh Token:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.refresh_token_entry = ttk.Entry(api_frame, width=50, show="*")
        self.refresh_token_entry.grid(row=3, column=1, pady=5, padx=(5, 0))
        
        ttk.Label(api_frame, text="如何获取API密钥?").grid(row=4, column=0, columnspan=2, pady=(20, 5), sticky=tk.W)
        
        help_text = """1. 访问 https://open.1688.com
2. 注册成为开放平台开发者
3. 创建应用获取App Key和App Secret
4. 根据文档获取Access Token"""
        
        help_label = ttk.Label(api_frame, text=help_text, justify=tk.LEFT)
        help_label.grid(row=5, column=0, columnspan=2, sticky=tk.W)
        
        # LLM配置页
        llm_frame = ttk.Frame(notebook, padding="10")
        notebook.add(llm_frame, text="LLM配置")
        
        ttk.Label(llm_frame, text="提供商:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.provider_var = tk.StringVar(value="openai")
        provider_combo = ttk.Combobox(llm_frame, textvariable=self.provider_var, width=20)
        provider_combo['values'] = ('openai', 'deepseek', 'qwen', 'ollama')
        provider_combo.grid(row=0, column=1, pady=5, padx=(5, 0), sticky=tk.W)
        
        ttk.Label(llm_frame, text="API Key:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.llm_api_key_entry = ttk.Entry(llm_frame, width=50, show="*")
        self.llm_api_key_entry.grid(row=1, column=1, pady=5, padx=(5, 0))
        
        ttk.Label(llm_frame, text="Base URL:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.base_url_entry = ttk.Entry(llm_frame, width=50)
        self.base_url_entry.grid(row=2, column=1, pady=5, padx=(5, 0))
        
        ttk.Label(llm_frame, text="模型:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.model_entry = ttk.Entry(llm_frame, width=50)
        self.model_entry.grid(row=3, column=1, pady=5, padx=(5, 0))
        
        ttk.Label(llm_frame, text="预设配置:").grid(row=4, column=0, sticky=tk.W, pady=(20, 5))
        
        preset_frame = ttk.Frame(llm_frame)
        preset_frame.grid(row=5, column=0, columnspan=2, sticky=tk.W)
        
        ttk.Button(preset_frame, text="DeepSeek", 
                  command=lambda: self._apply_preset("deepseek")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(preset_frame, text="千问", 
                  command=lambda: self._apply_preset("qwen")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(preset_frame, text="Ollama", 
                  command=lambda: self._apply_preset("ollama")).pack(side=tk.LEFT)
        
        # 按钮区域
        button_frame = ttk.Frame(self.window)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Button(button_frame, text="测试连接", command=self._test_connection).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="保存", command=self._save_config).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="取消", command=self.window.destroy).pack(side=tk.RIGHT)
    
    def _load_config(self):
        config = self.config.load_config()
        
        # 1688 API
        api_config = config.get("1688_api", {})
        self.app_key_entry.insert(0, api_config.get("app_key", ""))
        self.app_secret_entry.insert(0, api_config.get("app_secret", ""))
        self.access_token_entry.insert(0, api_config.get("access_token", ""))
        self.refresh_token_entry.insert(0, api_config.get("refresh_token", ""))
        
        # LLM
        llm_config = config.get("llm", {})
        self.provider_var.set(llm_config.get("provider", "openai"))
        self.llm_api_key_entry.insert(0, llm_config.get("api_key", ""))
        self.base_url_entry.insert(0, llm_config.get("base_url", ""))
        self.model_entry.insert(0, llm_config.get("model", ""))
    
    def _apply_preset(self, preset):
        presets = {
            "deepseek": {
                "provider": "deepseek",
                "base_url": "https://api.deepseek.com/v1",
                "model": "deepseek-chat"
            },
            "qwen": {
                "provider": "qwen",
                "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
                "model": "qwen-turbo"
            },
            "ollama": {
                "provider": "ollama",
                "base_url": "http://localhost:11434/v1",
                "model": "llama2"
            }
        }
        
        if preset in presets:
            preset_config = presets[preset]
            self.provider_var.set(preset_config["provider"])
            self.base_url_entry.delete(0, tk.END)
            self.base_url_entry.insert(0, preset_config["base_url"])
            self.model_entry.delete(0, tk.END)
            self.model_entry.insert(0, preset_config["model"])
    
    def _test_connection(self):
        from src.llm_agent import LLMAgent
        
        provider = self.provider_var.get()
        api_key = self.llm_api_key_entry.get()
        base_url = self.base_url_entry.get()
        model = self.model_entry.get()
        
        test_config = {
            "llm": {
                "provider": provider,
                "api_key": api_key,
                "base_url": base_url,
                "model": model
            }
        }
        
        class MockConfig:
            def get(self, section, key, default=None):
                return test_config.get(section, {}).get(key, default)
        
        try:
            agent = LLMAgent(MockConfig())
            if agent.test_connection():
                messagebox.showinfo("测试成功", "LLM连接测试成功！")
            else:
                messagebox.showerror("测试失败", "LLM连接测试失败，请检查配置")
        except Exception as e:
            messagebox.showerror("测试错误", f"连接测试失败: {str(e)}")
    
    def _save_config(self):
        config = self.config.load_config()
        
        # 更新1688 API配置
        config["1688_api"].update({
            "app_key": self.app_key_entry.get(),
            "app_secret": self.app_secret_entry.get(),
            "access_token": self.access_token_entry.get(),
            "refresh_token": self.refresh_token_entry.get()
        })
        
        # 更新LLM配置
        config["llm"].update({
            "provider": self.provider_var.get(),
            "api_key": self.llm_api_key_entry.get(),
            "base_url": self.base_url_entry.get(),
            "model": self.model_entry.get()
        })
        
        self.config.save_config(config)
        messagebox.showinfo("保存成功", "配置已保存")
        self.window.destroy()
```

**Step 4: 运行测试验证通过**

```bash
pytest tests/test_config_window.py -v
```
预期：PASS（模拟测试）

**Step 5: 提交配置窗口**

```bash
git add src/config_window.py tests/test_config_window.py
git commit -m "feat: 添加配置窗口"
```

---

### Task 8: 集成测试与完善

**Files:**
- Modify: `README.md`
- Create: `run.py`
- Create: `tests/test_integration.py`

**Step 1: 更新README文档**

```markdown
# 1688商品搜索GUI工具

一个图形化工具，通过1688 API搜索商品并智能推荐。

## 功能
1. 输入商品名称和用途
2. 调用1688 API搜索商品（最多10条）
3. 显示商品简介和链接
4. 智能体模式：LLM分析商品并推荐最佳选项

## 安装
```bash
pip install -r requirements.txt
```

## 配置
1. 运行程序后点击"配置"按钮
2. 1688 API配置：
   - 访问 https://open.1688.com 注册开发者账号
   - 创建应用获取App Key和App Secret
3. LLM配置：
   - 支持OpenAI格式API（如DeepSeek、千问、Ollama等）
   - 可使用预设配置快速设置

## 使用
1. 输入商品名称（如"手机"）
2. 输入商品用途（如"拍照"）
3. 点击"搜索商品"
4. 查看搜索结果
5. 启用"智能体模式"并点击"开始智能推荐"

## 支持的LLM
- OpenAI格式API（GPT系列）
- DeepSeek API
- 阿里云千问API
- Ollama本地模型

## 项目结构
```
src/
├── config_manager.py    # 配置管理
├── product_model.py     # 商品数据模型
├── alibaba_client.py    # 1688 API客户端
├── llm_agent.py        # LLM代理管理器
├── main_window.py      # 主窗口
└── config_window.py    # 配置窗口
```

## 注意事项
1. 需要有效的1688开放平台API密钥
2. LLM API需要有效的API密钥或本地服务
3. 商品搜索受1688 API限制
```

**Step 2: 创建便捷运行脚本**

```python
# run.py
#!/usr/bin/env python3
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    import tkinter as tk
    from config_manager import ConfigManager
    from alibaba_client import AlibabaClient
    from llm_agent import LLMAgent
    from main_window import MainWindow
    
    def main():
        root = tk.Tk()
        
        config = ConfigManager()
        alibaba_client = AlibabaClient(config)
        llm_agent = LLMAgent(config)
        
        app = MainWindow(root, config, alibaba_client, llm_agent)
        
        root.mainloop()
    
    if __name__ == "__main__":
        main()
        
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保已安装依赖: pip install -r requirements.txt")
    sys.exit(1)
```

**Step 3: 编写集成测试**

```python
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
```

**Step 4: 运行集成测试**

```bash
pytest tests/test_integration.py -v
```
预期：PASS

**Step 5: 运行完整测试套件**

```bash
pytest tests/ -v
```
预期：所有测试通过（模拟测试）

**Step 6: 提交最终版本**

```bash
git add README.md run.py tests/test_integration.py
git commit -m "feat: 完成集成测试和文档"
```

---

### Task 9: 最终验证

**Step 1: 安装依赖**

```bash
pip install -r requirements.txt
```
预期：成功安装依赖

**Step 2: 运行程序测试**

```bash
python run.py
```
预期：Tkinter窗口正常打开（可能需要配置API密钥）

**Step 3: 创建完成报告**

```markdown
# 完成报告

## 实现的功能
1. ✅ 商品数据模型 (Product类)
2. ✅ 配置管理器 (ConfigManager)
3. ✅ 1688 API客户端 (AlibabaClient)
4. ✅ LLM代理管理器 (LLMAgent)
5. ✅ Tkinter主窗口 (MainWindow)
6. ✅ 配置窗口 (ConfigWindow)
7. ✅ 集成测试和文档

## 技术特性
1. 模块化设计，易于维护和扩展
2. 支持多种LLM API（OpenAI格式、DeepSeek、千问、Ollama）
3. 线程安全，避免GUI冻结
4. 完整的错误处理
5. 详细的配置管理

## 使用说明
1. 安装依赖: `pip install -r requirements.txt`
2. 运行程序: `python run.py`
3. 配置1688 API和LLM API
4. 搜索商品并使用智能推荐功能
```

---

计划完成并保存到 `docs/plans/2026-03-10-1688-product-search-gui.md`。

**执行选项：**

1. **Subagent-Driven (本会话)** - 我分发新的子代理执行每个任务，任务间进行代码审查，快速迭代

2. **并行会话 (分离)** - 在新会话中使用executing-plans，批量执行并设置检查点

**您希望使用哪种方式？**