import sys
import re
import threading
import queue
import time
import os
import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog, ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.colors import ListedColormap
import seaborn as sns
import pandas as pd
import numpy as np

# --- MODERN BUTTON COMPONENT (RE-USED) ---
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

class MotionVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Nexus Playable Analytics | Real-Time Replay")
        self.root.geometry("1100x1000")
        self.root.configure(bg="#f1f3f4")
        
        self.all_events = []
        self.line_queue = queue.Queue()
        self.log_file = "live_data.txt"
        self.is_live = True  # The 'Global' Follow Variable
        self.is_playing = False

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

        ModernButton(self.top_frame, text="🗑️ CLEAR", color="#ffa3a3", command=self.clear_data).pack(side=tk.RIGHT, padx=5)
        ModernButton(self.top_frame, text="📁 EXPORT CSV", color="#f4ff91", command=self.export_csv).pack(side=tk.RIGHT, padx=5)
        ModernButton(self.top_frame, text="📷 SAVE PNG", color="#91faff", command=self.save_plot).pack(side=tk.RIGHT, padx=5)

        # 2. PANED WINDOW
        self.paned_window = tk.PanedWindow(root, orient=tk.VERTICAL, bg="#f1f3f4", sashwidth=6, sashrelief=tk.FLAT)
        self.paned_window.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

        self.card_frame = tk.Frame(self.paned_window, bg="#f1f3f4")
        self.fig, self.ax = plt.subplots(figsize=(8, 5))
        self.canvas_widget = FigureCanvasTkAgg(self.fig, master=self.card_frame)
        self.canvas_widget.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.paned_window.add(self.card_frame, minsize=400)

        # 3. MODERN PLAYBACK CONTROLS
        self.playback_frame = tk.Frame(root, bg="#ffffff", padx=20, pady=15, highlightthickness=1, highlightbackground="#e0e0e0")
        self.playback_frame.pack(fill=tk.X, padx=20, pady=10)

        self.play_btn = tk.Button(self.playback_frame, text="▶ PLAY", font=("Segoe UI", 10, "bold"), 
                                 command=self.toggle_play, width=12, bg="#1a73e8", fg="white", 
                                 activebackground="#1557b0", relief=tk.FLAT)
        self.play_btn.pack(side=tk.LEFT, padx=5)

        self.slider_var = tk.DoubleVar(value=0)

        # Custom styled scale
        self.slider = ttk.Scale(self.playback_frame, from_=0, to=100, orient=tk.HORIZONTAL, 
                               variable=self.slider_var, command=self.on_slider_move)
        self.slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=15)
        
        self.counter_label = tk.Label(self.playback_frame, text="0 / 0", font=("Consolas", 11, "bold"), bg="#ffffff", fg="#1a73e8")
        self.counter_label.pack(side=tk.RIGHT, padx=10)

        # 4. TERMINAL PANE
        self.term_container = tk.Frame(self.paned_window, bg="#f1f3f4")
        tk.Label(self.term_container, text="LIVE LOG STREAM", font=("Segoe UI", 10, "bold"), bg="#f1f3f4", fg="#5f6368").pack(anchor=tk.W, padx=20)
        self.terminal = scrolledtext.ScrolledText(self.term_container, bg="white", font=("Consolas", 10), height=8)
        self.terminal.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))
        self.paned_window.add(self.term_container, minsize=150)

        # Define terminal colors
        self.terminal.tag_config("x0", foreground="#A020F0", font=("Consolas", 10, "bold")) # Bright Purple
        self.terminal.tag_config("x1", foreground="#55d368", font=("Consolas", 10, "bold")) # Neon Green
        self.terminal.tag_config("action", foreground="#0000FF", font=("Consolas", 10, "bold")) # Deep Blue

        # THREADING
        threading.Thread(target=self.read_data, daemon=True).start()
        self.process_queue()

    def toggle_play(self):
        self.is_playing = not self.is_playing
        self.play_btn.config(text="⏸ PAUSE" if self.is_playing else "▶ PLAY", 
                            bg="#ea4335" if self.is_playing else "#1a73e8")
        if self.is_playing:
            if self.slider_var.get() >= len(self.all_events) - 1:
                self.slider_var.set(0)
            self.run_realtime_autoplay()

    def run_realtime_autoplay(self):
        """Calculates the time difference between events to play back at true speed."""
        if not self.is_playing:
            return

        curr_idx = int(self.slider_var.get())
        if curr_idx < len(self.all_events) - 1:
            # Determine how long to wait before the next point
            t1 = self.all_events[curr_idx]['pc_time']
            t2 = self.all_events[curr_idx + 1]['pc_time']
            # Convert to ms, capped at 1.5s to avoid boring long pauses
            wait_ms = int(min((t2 - t1) * 1000, 1500))
            
            self.slider_var.set(curr_idx + 1)
            self.update_plot()
            self.root.after(wait_ms, self.run_realtime_autoplay)
        else:
            self.is_playing = False
            self.play_btn.config(text="▶ PLAY", bg="#1a73e8")

    def on_slider_move(self, event):
        total = len(self.all_events)
        current_selection = int(float(event)) # Scale widget sends a string/float
        
        # If the user drags the slider away from the end, stop following live
        if current_selection < total - 5:
            self.is_live = False
            self.action_label.config(text="● INSPECTING HISTORY", fg="#f4b400")
        else:
            self.is_live = True
            self.action_label.config(text="● LIVE", fg="#4caf50")
            
        self.update_plot()
    
    def read_data(self):
        # Support for both file redirection and standard piping
        if not sys.stdin.isatty():
            while True:
                line = sys.stdin.readline()
                if line: self.line_queue.put(line)
        else:
            if not os.path.exists(self.log_file): open(self.log_file, "w").close()
            with open(self.log_file, "r") as f:
                f.seek(0, 2)
                while True:
                    line = f.readline()
                    if line: self.line_queue.put(line)
                    else: time.sleep(0.01)

    def process_queue(self):
        new_points = False
        while not self.line_queue.empty():
            try:
                line = self.line_queue.get_nowait()
                
                # 'end-1c' is the standard way to get the exact start of the new insertion
                start_ptr = self.terminal.index("end-1c")
                self.terminal.insert(tk.END, line)
                
                # --- BRIGHT SYNTAX HIGHLIGHTING ---
                
                # 1. Action (Blue) - matches action=ACTION_MOVE
                act = re.search(r'action=[^, ]+', line)
                if act:
                    self.terminal.tag_add("action", f"{start_ptr} + {act.start()}c", f"{start_ptr} + {act.end()}c")
                
                # 2. Pointer 0 (Purple) - matches x[0]=... and y[0]=...
                for m in re.finditer(r'[xy]\[0\]=[^, ]+', line):
                    self.terminal.tag_add("x0", f"{start_ptr} + {m.start()}c", f"{start_ptr} + {m.end()}c")

                # 3. Pointer 1 (Green) - matches x[1]=... and y[1]=...
                for m in re.finditer(r'[xy]\[1\]=[^, ]+', line):
                    self.terminal.tag_add("x1", f"{start_ptr} + {m.start()}c", f"{start_ptr} + {m.end()}c")
                # 4. Parse for graph
                data = self.parse_line(line)
                if data:
                    self.all_events.append(data)
                    new_points = True
                    
            except queue.Empty:
                break

        if new_points:
            total = len(self.all_events)
            self.slider.config(to=max(0, total - 1))
            if self.is_live and not self.is_playing:
                self.slider_var.set(total - 1)
                self.update_plot()
            self.counter_label.config(text=f"{int(self.slider_var.get())} / {total-1}")
            self.terminal.see(tk.END)

        self.root.after(20, self.process_queue)

    def parse_line(self, line):
        match = re.search(r'MotionEvent \{ (.*) \}', line)
        if not match: return None
        kv = re.findall(r'(\w+)(?:\[(\d+)\])?=([^, ]+)', match.group(1))
        row = { (f"{k}_{i}" if i else k): (float(v) if '.' in v else int(v) if v.isdigit() else v) for k, i, v in kv }
        row['timestamp_order'] = len(self.all_events)
        row['pc_time'] = time.time() # Capture PC arrival time for playback deltas
        return row

    def update_plot(self):
        self.ax.clear()
        
        # 1. IMMEDIATE RESTORATION OF AXES (Prevents disappearing)
        self.ax.set_xlabel("X-Axis (Sensor Range)", fontweight='bold', color='#5f6368')
        self.ax.set_ylabel("Y-Axis (Sensor Range)", fontweight='bold', color='#5f6368')
        self.ax.set_title("Live Replay: Multi-Touch Analytics", fontweight='bold', pad=10)
        
        if self.all_events:
            # Get the current point from the slider
            limit = int(self.slider_var.get())
            
            # Create the DataFrame
            df = pd.DataFrame(self.all_events)
            
            # SLICING FIX: Ensure we are looking at the data up to the limit
            # We use .iloc to ensure we get the correct integer index range
            df_slice = df.iloc[:limit + 1] 

            # Create colormaps
            p_map = ListedColormap(sns.color_palette("Purples", as_cmap=True)(np.linspace(0.3, 0.9, 256)))
            g_map = ListedColormap(sns.color_palette("Greens", as_cmap=True)(np.linspace(0.3, 0.9, 256)))
            
            if 'x_0' in df_slice.columns:
                d0 = df_slice.dropna(subset=['x_0', 'y_0'])
                # Only plot if we have data
                if not d0.empty:
                    self.ax.scatter(d0['x_0'], d0['y_0'], c=d0['timestamp_order'], 
                                    cmap=p_map, s=120, edgecolors='white', alpha=0.7)
            
            if 'x_1' in df_slice.columns:
                d1 = df_slice.dropna(subset=['x_1', 'y_1'])
                if not d1.empty:
                    self.ax.scatter(d1['x_1'], d1['y_1'], c=d1['timestamp_order'], 
                                    cmap=g_map, s=100, marker="D", edgecolors='white', alpha=0.7)

        # Apply User-Defined Limits
        try:
            self.ax.set_xlim(0, float(self.x_limit_var.get()))
            self.ax.set_ylim(0, float(self.y_limit_var.get()))
        except:
            pass

        # Use draw_idle() for smoother real-time performance
        self.canvas_widget.draw_idle()


    def clear_data(self):
        self.all_events = []; self.terminal.delete('1.0', tk.END); self.slider_var.set(0); self.update_plot()
        if os.path.exists(self.log_file): open(self.log_file, "w").close()

    def get_timestamp_filename(self, extension):
        """Generates a filename based on the first data point's timestamp."""
        if not self.all_events:
            # Fallback to current time if no data exists
            ts = time.strftime("%Y%m%d-%H%M%S")
        else:
            # Use the 'pc_time' from the very first event (index 0)
            first_ts = self.all_events[0]['pc_time']
            ts = time.strftime("%Y%m%d-%H%M%S", time.localtime(first_ts))
        
        return f"TouchLog_{ts}.{extension}"

    def save_plot(self):
        default_name = self.get_timestamp_filename("png")
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            initialfile=default_name,
            title="Save PNG Plot"
        )
        if path: 
            self.fig.savefig(path, dpi=300)
            messagebox.showinfo("Success", f"Saved to {os.path.basename(path)}")

    def export_csv(self):
        if not self.all_events:
            return
        default_name = self.get_timestamp_filename("csv")
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            initialfile=default_name,
            title="Export CSV Data"
        )
        if path: 
            pd.DataFrame(self.all_events).to_csv(path, index=False)
            messagebox.showinfo("Success", f"Exported to {os.path.basename(path)}")

if __name__ == "__main__":
    root = tk.Tk(); MotionVisualizer(root); root.mainloop()