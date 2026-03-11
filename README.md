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
