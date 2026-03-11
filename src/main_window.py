import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
from typing import List, Optional
from src.product_model import Product

class MainWindow:
    # 常量定义
    SEARCH_RESULT_LIMIT = 10
    
    # 列宽度常量
    COLUMN_WIDTH_DEFAULT = 100
    COLUMN_WIDTH_ID = 50
    COLUMN_WIDTH_TITLE = 200
    COLUMN_WIDTH_PRICE = 100
    COLUMN_WIDTH_SELLER = 150
    COLUMN_WIDTH_DESCRIPTION = 300
    
    # 字符串常量
    INPUT_ERROR_MSG = "输入错误"
    NO_DATA_MSG = "无数据"
    CONNECTION_FAILED_MSG = "连接失败"
    SEARCH_ERROR_MSG = "搜索错误"
    ANALYSIS_ERROR_MSG = "分析错误"
    READY_STATUS_MSG = "就绪"
    
    @staticmethod
    def _clean_input(text: str, max_length: int = 200, allow_empty: bool = False) -> str:
        """
        清理用户输入文本
        
        Args:
            text: 原始输入文本
            max_length: 最大长度限制
            allow_empty: 是否允许空字符串
        
        Returns:
            清理后的文本，如果输入无效返回空字符串
        """
        if not isinstance(text, str):
            return ""
        
        cleaned = text.strip()
        
        # 限制长度
        if len(cleaned) > max_length:
            cleaned = cleaned[:max_length]
        
        # 去除多余空白字符（多个 空格、换行等）
        cleaned = ' '.join(cleaned.split())
        
        # 如果允许空字符串或清理后有内容，则返回
        if allow_empty or cleaned:
            return cleaned
        return ""
    
    def __init__(self, root, config_manager, alibaba_client, llm_agent):
        self.root = root
        self.config = config_manager
        self.alibaba_client = alibaba_client
        self.llm_agent = llm_agent
        
        self.root.title("1688商品搜索工具")
        self.root.geometry(self.config.get("ui", "window_size", "1000x700"))
        
        self.products: List[Product] = []
        self.current_purpose: str = ""
        
        # 检查依赖状态
        self.alibaba_client_available = alibaba_client is not None
        self.llm_agent_available = llm_agent is not None
        
        self._setup_ui()
        self._load_config_to_ui()
        
        # 显示配置状态
        self._show_config_status()
    
    def _setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # 使用子函数创建各个区域
        search_frame = self._create_search_area(main_frame)
        result_frame = self._create_result_area(main_frame)
        agent_frame = self._create_agent_area(main_frame)
        status_bar = self._create_status_bar(main_frame)
        
        # 布局各个区域
        search_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        result_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        agent_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        status_bar.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # 配置按钮
        config_button = ttk.Button(main_frame, text="配置", command=self._open_config_window)
        config_button.grid(row=4, column=2, pady=(10, 0), sticky=tk.E)
        
    def _create_search_area(self, parent):
        """创建搜索区域组件，返回包含组件的frame"""
        frame = ttk.Frame(parent)
        
        ttk.Label(frame, text="商品名称:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.product_entry = ttk.Entry(frame, width=50)
        self.product_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        
        ttk.Label(frame, text="商品用途:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.purpose_entry = ttk.Entry(frame, width=50)
        self.purpose_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        
        self.search_button = ttk.Button(frame, text="搜索商品", command=self._search_products)
        self.search_button.grid(row=0, column=2, rowspan=2, padx=(10, 0), pady=5, sticky=tk.N)
        
        frame.columnconfigure(1, weight=1)
        return frame
    
    def _create_result_area(self, parent):
        """创建结果区域组件，返回包含Treeview的LabelFrame"""
        result_frame = ttk.LabelFrame(parent, text=f"搜索结果（最多{self.SEARCH_RESULT_LIMIT}条）", padding="10")
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
        
        columns = ("#", "商品名称", "价格", "卖家", "描述")
        self.tree = ttk.Treeview(result_frame, columns=columns, show="headings", height=8)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=self.COLUMN_WIDTH_DEFAULT)
        
        self.tree.column("#", width=self.COLUMN_WIDTH_ID)
        self.tree.column("商品名称", width=self.COLUMN_WIDTH_TITLE)
        self.tree.column("价格", width=self.COLUMN_WIDTH_PRICE)
        self.tree.column("卖家", width=self.COLUMN_WIDTH_SELLER)
        self.tree.column("描述", width=self.COLUMN_WIDTH_DESCRIPTION)
        
        tree_scroll = ttk.Scrollbar(result_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        return result_frame
    
    def _create_agent_area(self, parent):
        """创建智能体区域组件，返回包含组件的LabelFrame"""
        agent_frame = ttk.LabelFrame(parent, text="智能体推荐", padding="10")
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
        
        return agent_frame
    
    def _create_status_bar(self, parent):
        """创建状态栏，返回状态栏Label"""
        self.status_var = tk.StringVar(value=self.READY_STATUS_MSG)
        status_bar = ttk.Label(parent, textvariable=self.status_var, relief=tk.SUNKEN)
        return status_bar
    
    def _handle_async_error(self, error_callback, status_message):
        self.root.after(0, error_callback)
        self.root.after(0, lambda: self.status_var.set(status_message))
    
    def _load_config_to_ui(self):
        window_size = self.config.get("ui", "window_size", "1000x700")
        self.root.geometry(window_size)
        
        theme = self.config.get("ui", "theme", "light")
        try:
            style = ttk.Style()
            available_themes = style.theme_names()
            if theme in available_themes:
                style.theme_use(theme)
            elif "clam" in available_themes:
                style.theme_use("clam")
        except Exception:
            pass
    
    def _show_config_status(self):
        """显示配置状态信息"""
        status_parts = []
        
        if not self.alibaba_client_available:
            status_parts.append("1688 API不可用")
        else:
            # 检查API密钥是否配置
            api_key = self.config.get("1688_api", "app_key", "")
            api_secret = self.config.get("1688_api", "app_secret", "")
            if api_key and api_secret:
                status_parts.append("1688 API已配置")
            else:
                status_parts.append("1688 API未配置")
        
        if not self.llm_agent_available:
            status_parts.append("LLM代理不可用")
        else:
            llm_provider = self.config.get("llm", "provider", "openai")
            llm_api_key = self.config.get("llm", "api_key", "")
            if llm_provider == "ollama" or llm_api_key:
                status_parts.append("LLM代理已配置")
            else:
                status_parts.append("LLM代理未配置")
        
        status_text = " | ".join(status_parts) if status_parts else "配置正常"
        self.status_var.set(f"就绪 - {status_text}")
    
    def _search_products(self):
        # 检查1688 API客户端是否可用
        if not self.alibaba_client_available or self.alibaba_client is None:
            messagebox.showerror("功能不可用", "1688 API客户端不可用，请检查配置")
            return
        
        raw_keyword = self.product_entry.get()
        raw_purpose = self.purpose_entry.get()
        
        keyword = self._clean_input(raw_keyword, max_length=100, allow_empty=False)
        purpose = self._clean_input(raw_purpose, max_length=200, allow_empty=True)
        
        if not keyword:
            messagebox.showwarning(self.INPUT_ERROR_MSG, "请输入有效的商品名称（1-100个字符）")
            return
        
        # 进一步验证关键词是否包含有效内容（不只是数字或符号）
        if not any(c.isalpha() for c in keyword):
            messagebox.showwarning(self.INPUT_ERROR_MSG, "商品名称应包含文字描述")
            return
        
        self.current_purpose = purpose
        self.status_var.set("正在搜索商品...")
        self.search_button.config(state=tk.DISABLED)
        
        thread = threading.Thread(target=self._perform_search, args=(keyword, purpose))
        thread.daemon = True
        thread.start()
    
    def _perform_search(self, keyword, purpose):
        try:
            self.products = self.alibaba_client.search_products(keyword, purpose, limit=self.SEARCH_RESULT_LIMIT)
            
            self.root.after(0, self._update_results)
            self.root.after(0, lambda: self.status_var.set(f"找到 {len(self.products)} 个商品"))
            
        except Exception as e:
            self._handle_async_error(
                lambda: messagebox.showerror(self.SEARCH_ERROR_MSG, f"搜索失败 ({type(e).__name__}): {str(e)}"),
                "搜索失败"
            )
        
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
        # 检查LLM代理是否可用
        if not self.llm_agent_available or self.llm_agent is None:
            messagebox.showerror("功能不可用", "LLM代理不可用，请检查配置")
            return
        
        if not self.products:
            messagebox.showwarning(self.NO_DATA_MSG, "请先搜索商品")
            return
        
        try:
            if not self.llm_agent.test_connection():
                messagebox.showwarning(self.CONNECTION_FAILED_MSG, "LLM连接失败，请检查配置")
                return
        except Exception as e:
            messagebox.showerror(self.CONNECTION_FAILED_MSG, f"LLM连接测试失败: {str(e)}")
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
                self.root.after(0, lambda: messagebox.showerror(self.ANALYSIS_ERROR_MSG, result["error"]))
            else:
                self.root.after(0, lambda: self._display_recommendation(result))
            
            self.root.after(0, lambda: self.status_var.set("分析完成"))
            
        except Exception as e:
            self._handle_async_error(
                lambda: messagebox.showerror(self.ANALYSIS_ERROR_MSG, f"分析失败 ({type(e).__name__}): {str(e)}"),
                "分析失败"
            )
        
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
        try:
            from src.config_window import ConfigWindow
            config_window = ConfigWindow(self.root, self.config)
        except ImportError:
            messagebox.showinfo("功能未实现", "配置窗口功能将在任务7中实现")