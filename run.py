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