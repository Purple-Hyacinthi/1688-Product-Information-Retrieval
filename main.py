import tkinter as tk
import logging
from src.config_manager import ConfigManager
from src.alibaba_client import AlibabaClient
from src.llm_agent import LLMAgent
from src.main_window import MainWindow

def main():
    # 设置基本日志
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    
    root = tk.Tk()
    
    config = ConfigManager()
    
    # 检查关键配置
    logger.info("检查配置完整性...")
    
    # 检查1688 API配置
    api_key = config.get("1688_api", "app_key", "")
    api_secret = config.get("1688_api", "app_secret", "")
    access_token = config.get("1688_api", "access_token", "")
    
    if api_key and api_secret:
        logger.info("1688 API密钥已配置")
        if access_token:
            logger.info("1688访问令牌已配置")
        else:
            logger.warning("1688访问令牌未配置，可能需要授权")
    else:
        logger.warning("1688 API密钥未配置，搜索功能将不可用")
    
    # 检查LLM配置
    llm_provider = config.get("llm", "provider", "openai")
    llm_api_key = config.get("llm", "api_key", "")
    
    if llm_provider == "ollama":
        logger.info(f"LLM提供商: {llm_provider} (本地模式，无需API密钥)")
    elif llm_api_key:
        logger.info(f"LLM提供商: {llm_provider}，API密钥已配置")
    else:
        logger.warning(f"LLM提供商: {llm_provider}，API密钥未配置，代理模式将不可用")
    
    try:
        alibaba_client = AlibabaClient(config)
        logger.info("1688 API客户端初始化成功")
    except Exception as e:
        logger.error(f"1688 API客户端初始化失败: {e}")
        alibaba_client = None
    
    try:
        llm_agent = LLMAgent(config)
        logger.info("LLM代理初始化成功")
    except Exception as e:
        logger.error(f"LLM代理初始化失败: {e}")
        llm_agent = None
    
    app = MainWindow(root, config, alibaba_client, llm_agent)
    
    logger.info("应用程序启动完成")
    root.mainloop()

if __name__ == "__main__":
    main()