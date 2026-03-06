import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import importlib.util
import re

class SyntaxHighlighter:
    """Regex based highlighting engine."""
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.categories = {
            "keyword": (r'\b(def|class|return|if|else|elif|import|from|while|for|in|try|except|with|as|pass)\b', "#ff7b72"),
            "string": (r'(\".*?\"|\'.*?\')', "#a5d6ff"),
            "comment": (r'#.*', "#8b949e"),
            "builtin": (r'\b(print|len|range|int|str|list|dict|set|open|self)\b', "#d2a8ff")
        }
        for tag, (pattern, color) in self.categories.items():
            self.text_widget.tag_configure(tag, foreground=color)

    def highlight(self, event=None):
        content = self.text_widget.get("1.0", tk.END)
        for tag, (pattern, color) in self.categories.items():
            self.text_widget.tag_remove(tag, "1.0", tk.END)
            for match in re.finditer(pattern, content):
                start = f"1.0 + {match.start()} chars"
                end = f"1.0 + {match.end()} chars"
                self.text_widget.tag_add(tag, start, end)

class SlickLeafUltra:
    def __init__(self, root):
        self.root = root
        self.root.title("Slick-Leaf Ultra")
        self.root.geometry("1100x750")
        self.root.configure(bg="#0d1117")

        # --- UI Styling ---
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("TNotebook", background="#161b22", borderwidth=0)
        self.style.configure("TNotebook.Tab", background="#21262d", foreground="#c9d1d9", padding=[15, 5])
        self.style.map("TNotebook.Tab", background=[("selected", "#0d1117")], foreground=[("selected", "#ffffff")])

        self.setup_ui()
        self.create_menus()
        self.load_plugins()

    def setup_ui(self):
        # 1. TOOLBAR (Includes New File Button)
        self.toolbar = tk.Frame(self.root, bg="#161b22", height=40)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)
        
        self.btn_new = tk.Button(self.toolbar, text="📄 New File", command=self.add_new_tab, 
                                 bg="#238636", fg="white", activebackground="#2ea043", 
                                 activeforeground="white", relief="flat", padx=10, cursor="hand2")
        self.btn_new.pack(side=tk.LEFT, padx=10, pady=5)

        self.btn_open = tk.Button(self.toolbar, text="📂 Open", command=self.open_file, 
                                 bg="#21262d", fg="#c9d1d9", activebackground="#30363d", 
                                 activeforeground="white", relief="flat", padx=10, cursor="hand2")
        self.btn_open.pack(side=tk.LEFT, padx=5, pady=5)

        # 2. PANED WORKSPACE (Sidebar + Tabs)
        self.main_pane = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, bg="#0d1117", sashwidth=3)
        self.main_pane.pack(fill=tk.BOTH, expand=True)

        self.sidebar = tk.Listbox(self.main_pane, bg="#0d1117", fg="#8b949e", border=0, font=("Arial", 10))
        self.main_pane.add(self.sidebar, width=180)

        self.notebook = ttk.Notebook(self.main_pane)
        self.main_pane.add(self.notebook)

        # 3. STATUS BAR
        self.status = tk.Label(self.root, text="Ready", bg="#161b22", fg="#8b949e", anchor=tk.W, padx=10)
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

        self.add_new_tab()

    def get_active_text(self):
        """API for Plugins: Returns the Text widget of the currently active tab."""
        try:
            current_tab = self.notebook.nametowidget(self.notebook.select())
            return current_tab.winfo_children()[0] 
        except:
            return None

    def add_new_tab(self, name="Untitled", content=""):
        tab_frame = tk.Frame(self.notebook, bg="#0d1117")
        txt = tk.Text(tab_frame, undo=True, bg="#0d1117", fg="#c9d1d9", insertbackground="white", 
                      font=("Monospace", 12), border=0, padx=15, pady=15, wrap="none")
        
        highlighter = SyntaxHighlighter(txt)
        txt.bind("<KeyRelease>", lambda e: [highlighter.highlight(), self.update_status(), self.update_symbols()])
        txt.bind("<Button-1>", lambda e: self.root.after(10, self.update_status))
        
        txt.insert("1.0", content)
        txt.pack(fill=tk.BOTH, expand=True)
        
        self.notebook.add(tab_frame, text=name)
        self.notebook.select(tab_frame)
        highlighter.highlight()

    def update_status(self):
        txt = self.get_active_text()
        if txt:
            row, col = txt.index(tk.INSERT).split('.')
            self.status.config(text=f"Line: {row} | Col: {int(col)+1}")

    def update_symbols(self):
        txt = self.get_active_text()
        if not txt: return
        self.sidebar.delete(0, tk.END)
        lines = txt.get("1.0", tk.END).split('\n')
        for line in lines:
            if line.strip().startswith(('def ', 'class ')):
                self.sidebar.insert(tk.END, f"  {line.strip().split('(')[0]}")

    def create_menus(self):
        self.menu_bar = tk.Menu(self.root)
        
        # File Menu
        file_m = tk.Menu(self.menu_bar, tearoff=0)
        file_m.add_command(label="New Tab", command=self.add_new_tab)
        file_m.add_command(label="Open File", command=self.open_file)
        file_m.add_separator()
        file_m.add_command(label="Exit", command=self.root.quit)
        self.menu_bar.add_cascade(label="File", menu=file_m)

        # Plugin Menu (crucial for loading external scripts)
        self.plugin_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Plugins", menu=self.plugin_menu)
        
        self.root.config(menu=self.menu_bar)

    def load_plugins(self):
        plugin_dir = os.path.join(os.getcwd(), "plugins")
        if not os.path.exists(plugin_dir): 
            os.makedirs(plugin_dir)
            return

        for filename in os.listdir(plugin_dir):
            if filename.endswith(".py"):
                path = os.path.join(plugin_dir, filename)
                spec = importlib.util.spec_from_file_location(filename[:-3], path)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                # Pass the main editor instance to the plugin
                if hasattr(mod, "register"): 
                    mod.register(self)

    def open_file(self):
        path = filedialog.askopenfilename()
        if path:
            with open(path, 'r') as f:
                self.add_new_tab(os.path.basename(path), f.read())

if __name__ == "__main__":
    root = tk.Tk()
    app = SlickLeafUltra(root)
    root.mainloop()