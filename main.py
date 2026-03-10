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