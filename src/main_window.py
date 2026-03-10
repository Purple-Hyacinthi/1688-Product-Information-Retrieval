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