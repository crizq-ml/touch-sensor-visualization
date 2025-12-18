import sys
import re
import threading
import queue
import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog, ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
import pandas as pd
import numpy as np

# --- SMOOTH ROUNDED BUTTON COMPONENT ---
class ModernButton(tk.Canvas):
    def __init__(self, parent, text, color="#1a73e8", command=None, width=150, height=50):
        super().__init__(parent, width=width+10, height=height+10, bg=parent['bg'], highlightthickness=0)
        self.command = command
        self.color = color
        self.hover_color = self._adjust_brightness(color, 1.1)
        
        self._draw_round_rect(5, 5, width+3, height+3, 20, fill="#d1d1d1", tag="shadow")
        self.btn_shape = self._draw_round_rect(2, 2, width, height, 20, fill=self.color, tag="button")
        self.create_text(width/2 + 2, height/2 + 2, text=text, fill="#5f6368", font=("Segoe UI", 10, "bold"), tag="text")

        self.tag_bind("button", "<Enter>", lambda e: self.itemconfig("button", fill=self.hover_color))
        self.tag_bind("button", "<Leave>", lambda e: self.itemconfig("button", fill=self.color))
        self.tag_bind("button", "<Button-1>", self._execute)
        self.tag_bind("text", "<Button-1>", self._execute)

    def _execute(self, event):
        if self.command: self.command()

    def _draw_round_rect(self, x1, y1, x2, y2, r, **kwargs):
        points = [x1+r, y1, x1+r, y1, x2-r, y1, x2-r, y1, x2, y1, x2, y1+r, x2, y1+r, x2, y2-r, x2, y2-r, x2, y2, x2-r, y2, x2-r, y2, x1+r, y2, x1+r, y2, x1, y2, x1, y2-r, x1, y2-r, x1, y1+r, x1, y1+r, x1, y1]
        return self.create_polygon(points, **kwargs, smooth=True)

    def _adjust_brightness(self, hex_color, factor):
        rgb = [int(hex_color[i:i+2], 16) for i in (1, 3, 5)]
        new_rgb = [min(255, int(c * factor)) for c in rgb]
        return "#%02x%02x%02x" % tuple(new_rgb)

# --- MAIN APPLICATION ---
class MotionVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Nexus Touch Analytics")
        self.root.geometry("1100x950")
        self.root.configure(bg="#f1f3f4")
        
        self.all_events = []
        self.line_queue = queue.Queue()

        # 1. TOP BAR
        self.top_frame = tk.Frame(root, bg="#f1f3f4", padx=20, pady=20)
        self.top_frame.pack(fill=tk.X)

        self.x_limit_var = tk.StringVar(value="1600")
        self.y_limit_var = tk.StringVar(value="306")
        self.x_limit_var.trace_add("write", lambda *a: self.update_plot())
        self.y_limit_var.trace_add("write", lambda *a: self.update_plot())

        input_box = tk.Frame(self.top_frame, bg="#f1f3f4")
        input_box.pack(side=tk.LEFT)
        
        tk.Label(input_box, text="X MAX", font=("Segoe UI", 12, "bold"), bg="#f1f3f4", fg="#5f6368").grid(row=0, column=0)
        ttk.Entry(input_box, textvariable=self.x_limit_var, width=8, font=("Segoe UI", 14)).grid(row=0, column=1, padx=10)
        
        tk.Label(input_box, text="Y MAX", font=("Segoe UI", 12, "bold"), bg="#f1f3f4", fg="#5f6368").grid(row=0, column=2, padx=(10, 0))
        ttk.Entry(input_box, textvariable=self.y_limit_var, width=8, font=("Segoe UI", 14)).grid(row=0, column=3, padx=10)
       
        self.action_label = tk.Label(self.top_frame, text="● READY", font=("Segoe UI", 14, "bold"), fg="#4285f4", bg="#f1f3f4")
        self.action_label.pack(side=tk.LEFT, padx=30)

        self.btn_clear = ModernButton(self.top_frame, text="🗑️ CLEAR", color="#ffa3a3", command=self.clear_data)
        self.btn_clear.pack(side=tk.RIGHT, padx=5)
        self.btn_csv = ModernButton(self.top_frame, text="📁 EXPORT CSV", color="#f4ff91", command=self.export_csv)
        self.btn_csv.pack(side=tk.RIGHT, padx=5)
        self.btn_save = ModernButton(self.top_frame, text="📷 SAVE PNG", color="#91faff", command=self.save_plot)
        self.btn_save.pack(side=tk.RIGHT, padx=5)

        self.paned_window = tk.PanedWindow(root, orient=tk.VERTICAL, bg="#f1f3f4", sashwidth=6, sashrelief=tk.FLAT)
        self.paned_window.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

        # 2. PLOT PANE
        self.card_frame = tk.Frame(self.paned_window, bg="#f1f3f4")
        self.card_canvas = tk.Canvas(self.card_frame, bg="#f1f3f4", highlightthickness=0)
        self.card_canvas.pack(fill=tk.BOTH, expand=True)

        sns.set_theme(style="whitegrid")
        self.fig, self.ax = plt.subplots(figsize=(8, 6))
        self.fig.patch.set_facecolor('white')
        self.canvas_widget = FigureCanvasTkAgg(self.fig, master=self.card_canvas)
        self.plot_item = self.card_canvas.create_window(0, 0, window=self.canvas_widget.get_tk_widget(), anchor="nw")
        self.paned_window.add(self.card_frame, minsize=300)

        # 3. TERMINAL PANE
        self.term_container = tk.Frame(self.paned_window, bg="#f1f3f4")
        self.terminal = scrolledtext.ScrolledText(self.term_container, bg="white", fg="#3c4043", font=("Consolas", 10), relief=tk.FLAT, borderwidth=1, highlightthickness=1, highlightbackground="#e0e0e0")
        self.terminal.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        # --- RAINBOW COLORS SETUP ---
        self.rainbow_colors = ["#e91e63", "#9c27b0", "#673ab7", "#3f51b5", "#2196f3", "#009688", "#4caf50", "#ff9800", "#795548"]
        for i, color in enumerate(self.rainbow_colors):
            self.terminal.tag_config(f"color_{i}", foreground=color)
        
        self.terminal.tag_config("timestamp", foreground="#757575")
        self.terminal.tag_config("action", foreground="#d32f2f", font=("Consolas", 10, "bold"))

        self.paned_window.add(self.term_container, minsize=100)
        self.card_canvas.bind("<Configure>", self.on_resize)

        threading.Thread(target=self.read_stdin, daemon=True).start()
        self.process_queue()

    def on_resize(self, event):
        w, h = event.width, event.height
        self.card_canvas.delete("card_bg")
        r = 40
        x1, y1, x2, y2 = 5, 5, w-5, h-5
        points = [x1+r, y1, x1+r, y1, x2-r, y1, x2-r, y1, x2, y1, x2, y1+r, x2, y1+r, x2, y2-r, x2, y2-r, x2, y2, x2-r, y2, x2-r, y2, x1+r, y2, x1+r, y2, x1, y2, x1, y2-r, x1, y2-r, x1, y1+r, x1, y1+r, x1, y1]
        self.card_canvas.create_polygon(points, fill="white", outline="#e0e0e0", smooth=True, tag="card_bg")
        self.card_canvas.tag_lower("card_bg")
        self.card_canvas.coords(self.plot_item, w/2, h/2)
        self.card_canvas.itemconfig(self.plot_item, width=w-60, height=h-60, anchor="center")

    def parse_line(self, line):
        match = re.search(r'MotionEvent \{ (.*) \}', line)
        if not match: return None
        kv = re.findall(r'(\w+)(?:\[(\d+)\])?=([^, ]+)', match.group(1))
        row = { (f"{k}_{i}" if i else k): (float(v) if '.' in v else int(v) if v.isdigit() else v) for k, i, v in kv }
        row['timestamp_order'] = len(self.all_events)
        return row

    def update_plot(self):
        if not self.all_events:
            self.ax.clear(); self.canvas_widget.draw(); return
        df = pd.DataFrame(self.all_events)
        self.ax.clear()
        if 'x_0' in df.columns and 'y_0' in df.columns:
            df0 = df.dropna(subset=['x_0', 'y_0'])
            self.ax.scatter(df0['x_0'], df0['y_0'], c=df0['timestamp_order'], cmap='Purples', s=120, edgecolors='white', alpha=0.7)
        if 'x_1' in df.columns and 'y_1' in df.columns:
            df1 = df.dropna(subset=['x_1', 'y_1'])
            if not df1.empty:
                self.ax.scatter(df1['x_1'], df1['y_1'], c=df1['timestamp_order'], cmap='viridis', s=100, edgecolors='white', marker="D", alpha=0.7)
        try:
            self.ax.set_xlim(0, float(self.x_limit_var.get()))
            self.ax.set_ylim(0, float(self.y_limit_var.get()))
        except: pass
        self.ax.set_xlabel("X"); self.ax.set_ylabel("Y")
        self.canvas_widget.draw()

    def clear_data(self):
        self.all_events = []; self.terminal.delete('1.0', tk.END); self.update_plot()

    def save_plot(self):
        path = filedialog.asksaveasfilename(defaultextension=".png"); 
        if path: self.fig.savefig(path, dpi=300); messagebox.showinfo("Success", "Saved")

    def export_csv(self):
        if not self.all_events: return
        path = filedialog.asksaveasfilename(defaultextension=".csv")
        if path: pd.DataFrame(self.all_events).to_csv(path, index=False)

    def read_stdin(self):
        for line in sys.stdin:
            if line: self.line_queue.put(line)

    def process_queue(self):
        try:
            while True:
                line = self.line_queue.get_nowait()
                start_ptr = self.terminal.index("end-1c")
                self.terminal.insert("end", line)
                
                # 1. Colorize Timestamp (First 18 chars)
                self.terminal.tag_add("timestamp", start_ptr, f"{start_ptr} + 18c")

                # 2. Colorize Action
                act = re.search(r'action=([^, ]*)', line)
                if act:
                    self.terminal.tag_add("action", f"{start_ptr} + {act.start()}c", f"{start_ptr} + {act.end()}c")

                # 3. Rainbow Colorize Key-Value Pairs inside { }
                # We find all matches for "key=value" and rotate through the rainbow palette
                kv_matches = list(re.finditer(r'(\w+(?:\[\d+\])?)=([^, \}]+)', line))
                for i, m in enumerate(kv_matches):
                    color_tag = f"color_{i % len(self.rainbow_colors)}"
                    self.terminal.tag_add(color_tag, f"{start_ptr} + {m.start()}c", f"{start_ptr} + {m.end()}c")

                self.terminal.see("end")
                data = self.parse_line(line)
                if data:
                    self.all_events.append(data)
                    self.action_label.config(text=f"● {data.get('action', 'N/A')}")
                    self.update_plot()
        except queue.Empty: pass
        self.root.after(50, self.process_queue)

if __name__ == "__main__":
    root = tk.Tk(); MotionVisualizer(root); root.mainloop()