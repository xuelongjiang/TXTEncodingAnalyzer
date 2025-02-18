import tkinter as tk
from tkinter import filedialog, ttk, messagebox  # 添加 messagebox
import os
import chardet
from collections import Counter

class EncodingAnalyzer(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("文本文件编码分析器")
        self.geometry("800x600")  # 调整窗口大小
        
        self.selected_directory = None
        self.encoding_files = {}  # 存储每种编码对应的文件列表
        
        # 创建界面元素
        self.create_widgets()
    
    def create_widgets(self):
        # 顶部按钮框架
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)
        
        # 选择目录按钮
        self.select_btn = tk.Button(btn_frame, text="选择目录", command=self.select_directory)
        self.select_btn.pack(side=tk.LEFT, padx=5)
        
        # 分析按钮
        self.analyze_btn = tk.Button(btn_frame, text="开始分析", command=self.start_analyze)
        self.analyze_btn.pack(side=tk.LEFT, padx=5)
        
        # 显示选中的目录
        self.path_label = tk.Label(self, text="未选择目录", wraplength=500)
        self.path_label.pack(pady=5)
        
        # 创建左右分栏框架
        paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=5)
        
        # 创建左侧框架
        left_frame = ttk.LabelFrame(paned, text="编码统计 (点击查看文件列表)")
        paned.add(left_frame, weight=1)
        
        # 创建左侧编码统计表格
        columns = ("编码", "文件数量", "百分比")
        self.tree = ttk.Treeview(left_frame, columns=columns, show="headings", style="Custom.Treeview")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        # 添加滚动条
        tree_scroll = ttk.Scrollbar(left_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 创建右侧框架
        right_frame = ttk.LabelFrame(paned, text="文件列表 (双击打开文件)")
        paned.add(right_frame, weight=1)
        
        # 创建右侧文件列表
        self.file_list = ttk.Treeview(right_frame, columns=("文件路径",), show="headings", style="Custom.Treeview")
        self.file_list.heading("文件路径", text="文件路径")
        self.file_list.column("文件路径", width=300)
        
        # 添加滚动条
        file_scroll = ttk.Scrollbar(right_frame, orient="vertical", command=self.file_list.yview)
        self.file_list.configure(yscrollcommand=file_scroll.set)
        
        self.file_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        file_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 设置树形控件的样式
        style = ttk.Style()
        style.configure("Custom.Treeview", rowheight=25)  # 增加行高
        style.configure("Custom.Treeview.Heading", font=('TkDefaultFont', 9, 'bold'))  # 加粗表头
        
        # 绑定事件
        self.tree.bind('<<TreeviewSelect>>', self.on_encoding_select)
        self.file_list.bind('<Double-1>', self.open_file)
        
        # 添加鼠标悬停效果
        self.tree.bind('<Motion>', lambda e: self.tree.configure(cursor='hand2'))
        self.file_list.bind('<Motion>', lambda e: self.file_list.configure(cursor='hand2'))
    def select_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.selected_directory = directory
            self.path_label.config(text=directory)
            
    def start_analyze(self):
        if not self.selected_directory:
            tk.messagebox.showwarning("警告", "请先选择目录！")
            return
        self.analyze_directory(self.selected_directory)
    
    def analyze_directory(self, directory):
        encoding_counter = Counter()
        total_files = 0
        self.encoding_files.clear()  # 清空文件列表
        
        # 遍历目录
        for root, _, files in os.walk(directory):
            for file in files:
                if self.is_text_file(file):
                    file_path = os.path.join(root, file)
                    encoding = self.detect_encoding(file_path)
                    if encoding:
                        encoding_counter[encoding] += 1
                        total_files += 1
                        # 存储文件路径
                        if encoding not in self.encoding_files:
                            self.encoding_files[encoding] = []
                        self.encoding_files[encoding].append(file_path)
        
        # 显示结果
        if total_files > 0:
            sorted_results = encoding_counter.most_common()
            for encoding, count in sorted_results:
                percentage = f"{(count/total_files)*100:.2f}%"
                self.tree.insert("", tk.END, values=(encoding, count, percentage))
    
    def is_text_file(self, filename):
        text_extensions = {'.txt', '.csv', '.md', '.py', '.java', '.cpp', '.h', 
                          '.c', '.js', '.html', '.css', '.xml', '.json'}
        return os.path.splitext(filename)[1].lower() in text_extensions
    
    def detect_encoding(self, file_path):
        try:
            with open(file_path, 'rb') as file:
                raw_data = file.read()
                result = chardet.detect(raw_data)
                return result['encoding']
        except Exception:
            return None
    def on_encoding_select(self, event):
        selected_items = self.tree.selection()
        if not selected_items:
            return
            
        # 清空文件列表
        for item in self.file_list.get_children():
            self.file_list.delete(item)
            
        # 获取选中的编码
        encoding = self.tree.item(selected_items[0])['values'][0]
        
        # 显示该编码的文件列表
        if encoding in self.encoding_files:
            for file_path in self.encoding_files[encoding]:
                self.file_list.insert("", tk.END, values=(file_path,))
    def open_file(self, event):
        selected_items = self.file_list.selection()
        if not selected_items:
            return
            
        file_path = self.file_list.item(selected_items[0])['values'][0]
        os.startfile(file_path)  # Windows系统打开文件
# 在文件底部添加主程序入口
if __name__ == "__main__":
    app = EncodingAnalyzer()
    app.mainloop()