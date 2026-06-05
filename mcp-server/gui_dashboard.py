import threading
import customtkinter as ctk
import json
import re
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# Directly import the execution logic from your Phase 5 MCP server
from mcp_nmap_server import cancel_scan, scan_local_machine

# Configure global GUI aesthetics
ctk.set_appearance_mode("System")  # Matches OS theme (Light/Dark)
ctk.set_default_color_theme("blue")

class NmapAnalyticsGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Settings
        self.title("MCP Nmap Analytics & Metrics Dashboard")
        self.geometry("1100x700")

        # Configure Grid Layout (2 Columns: Sidebar and Main Content)
        self.grid_columnconfigure(0, weight=1, minsize=260)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(0, weight=1)

        # ------------------ SIDEBAR CONTROLS ------------------
        self.sidebar = ctk.CTkFrame(self, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        self.sidebar.grid_columnconfigure(0, weight=1)
        self.sidebar.grid_rowconfigure(4, weight=1)

        self.title_label = ctk.CTkLabel(
            self.sidebar, 
            text="Scan Configurations", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.title_label.grid(row=0, column=0, sticky="ew", padx=10, pady=(20, 10))

        # Profile Selector Dropdown
        self.scan_type_var = ctk.StringVar(value="quick")
        self.scan_dropdown = ctk.CTkOptionMenu(
            self.sidebar, 
            values=["quick", "intense", "ping"], 
            variable=self.scan_type_var
        )
        self.scan_dropdown.grid(row=1, column=0, sticky="ew", padx=20, pady=10)

        # Trigger Button
        self.run_btn = ctk.CTkButton(
            self.sidebar, 
            text="Execute MCP Tool Scan", 
            command=self.trigger_scan, 
            fg_color="#2b719e"
        )
        self.run_btn.grid(row=2, column=0, sticky="ew", padx=20, pady=(10, 8))

        self.cancel_btn = ctk.CTkButton(
            self.sidebar,
            text="Stop Scan",
            command=self.request_cancel_scan,
            fg_color="#c0392b",
            state="disabled"
        )
        self.cancel_btn.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 20))

        # Nested Frame for Analytics Cards / Metrics
        self.metrics_frame = ctk.CTkScrollableFrame(self.sidebar, label_text="Scan Quality Metrics")
        self.metrics_frame.grid(row=4, column=0, sticky="nsew", padx=20, pady=10)
        
        self.metric_latency = ctk.CTkLabel(self.metrics_frame, text="Host Latency: --", anchor="w")
        self.metric_latency.pack(fill="x", padx=10, pady=5)
        
        self.metric_ports_open = ctk.CTkLabel(self.metrics_frame, text="Open Ports: --", anchor="w")
        self.metric_ports_open.pack(fill="x", padx=10, pady=5)

        self.metric_score = ctk.CTkLabel(
            self.metrics_frame, 
            text="Exposure Index: --", 
            font=ctk.CTkFont(weight="bold"),
            anchor="w"
        )
        self.metric_score.pack(fill="x", padx=10, pady=10)

        # ------------------ MAIN CONTENT AREA ------------------
        self.main_content = ctk.CTkFrame(self, fg_color="transparent")
        self.main_content.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.main_content.grid_columnconfigure(0, weight=1)
        self.main_content.grid_rowconfigure(1, weight=1)

        # Application Status Bar
        self.status_bar = ctk.CTkLabel(
            self.main_content, 
            text="System Engine Ready. Awaiting user interaction...", 
            anchor="w", 
            font=ctk.CTkFont(size=13)
        )
        self.status_bar.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        # Tabbed Layout for Visual Graphing vs Raw Output Log
        self.tab_view = ctk.CTkTabview(self.main_content)
        self.tab_view.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.tab_view.add("Analytics Chart")
        self.tab_view.add("Raw Terminal Output")

        # Tab 1: Terminal text wrapper
        self.raw_output_text = ctk.CTkTextbox(self.tab_view.tab("Raw Terminal Output"), wrap="word")
        self.raw_output_text.pack(fill="both", expand=True)

        # Tab 2: Matplotlib rendering engine container
        self.chart_frame = ctk.CTkFrame(self.tab_view.tab("Analytics Chart"), fg_color="transparent")
        self.chart_frame.pack(fill="both", expand=True)

        self.chart_fig = Figure(figsize=(5, 4), dpi=100)
        self.chart_ax = self.chart_fig.add_subplot(111)
        self.chart_canvas = FigureCanvasTkAgg(self.chart_fig, master=self.chart_frame)
        self.chart_canvas.draw()
        self.chart_canvas.get_tk_widget().pack(fill="both", expand=True)

    def trigger_scan(self):
        """Dispatches execution payload safely to the FastMCP underlying function block."""
        self.status_bar.configure(text="⚡ Requesting live scan via Python FastMCP engine... Please wait...", text_color="#e67e22")
        self.run_btn.configure(state="disabled")
        self.cancel_btn.configure(state="normal")
        self.update_idletasks()

        profile = self.scan_type_var.get()
        thread = threading.Thread(target=self._run_scan_thread, args=(profile,), daemon=True)
        thread.start()

    def request_cancel_scan(self):
        self.cancel_btn.configure(state="disabled")
        self.status_bar.configure(text="🛑 Cancel requested. Attempting to stop active scan...", text_color="#e67e22")
        canceled = cancel_scan()

        if not canceled:
            self.status_bar.configure(text="⚠️ No active scan process was found to cancel.", text_color="#f39c12")

    def _run_scan_thread(self, profile):
        try:
            response_str = scan_local_machine(scan_type=profile)
            response = response_str
            if isinstance(response_str, str):
                try:
                    response = json.loads(response_str)
                except json.JSONDecodeError as err:
                    raise ValueError(f"Invalid JSON response from scan tool: {err}") from err

            self.after(0, self._handle_scan_response, response)
        except Exception as err:
            self.after(0, self._handle_scan_error, err)

    def _handle_scan_response(self, response):
        try:
            if response.get("status") == "success":
                raw_text = response.get("raw_output", "")
                self.status_bar.configure(text="✓ Nmap tool chain executed successfully.", text_color="#2ecc71")
                self.raw_output_text.delete("1.0", "end")
                self.raw_output_text.insert("end", raw_text)
                self.parse_and_render_metrics(raw_text)
            else:
                error_msg = response.get("message", "Unknown script error.")
                self.status_bar.configure(text=f"❌ Scan Failed: {error_msg}", text_color="#e74c3c")
        finally:
            self.run_btn.configure(state="normal")
            self.cancel_btn.configure(state="disabled")

    def _handle_scan_error(self, error):
        self.status_bar.configure(text=f"❌ Fatal System Error: {str(error)}", text_color="#e74c3c")
        self.run_btn.configure(state="normal")
        self.cancel_btn.configure(state="disabled")

    def parse_and_render_metrics(self, raw_text):
        """Extracts text structures using RegEx patterns to populate widgets and charts."""
        # 1. Parse Latency Metrics
        latency_match = re.search(r"Host is up \((.*?)\s+latency\)", raw_text)
        latency = latency_match.group(1) if latency_match else "N/A (Localhost)"
        self.metric_latency.configure(text=f"Host Latency: {latency}")

        # 2. Count Port States via state matchers
        open_ports = re.findall(r"(\d+)/tcp\s+open", raw_text)
        filtered_ports = re.findall(r"(\d+)/tcp\s+filtered", raw_text)
        closed_ports = re.findall(r"(\d+)/tcp\s+closed", raw_text)
        num_open = len(open_ports)
        num_filtered = len(filtered_ports)
        num_closed = len(closed_ports)
        
        self.metric_ports_open.configure(text=f"Open Ports Found: {num_open}")

        # 3. Calculate Risk/Exposure Profile Rule
        if num_open == 0:
            exposure_index = "SECURE"
            lbl_color = "#2ecc71"
        elif num_open <= 2:
            exposure_index = "LOW RISK"
            lbl_color = "#2ecc71"
        elif num_open <= 5:
            exposure_index = "MEDIUM RISK"
            lbl_color = "#f1c40f"
        else:
            exposure_index = "CRITICAL METRIC"
            lbl_color = "#e74c3c"
            
        self.metric_score.configure(text=f"Exposure Index: {exposure_index}", text_color=lbl_color)

        # 4. Update Matplotlib Canvas in place for faster refreshes
        self.chart_ax.clear()
        categories = ['Open TCP', 'Filtered TCP', 'Closed TCP']
        values = [num_open, num_filtered, num_closed]
        colors = ['#e74c3c', '#f1c40f', '#95a5a6']

        bars = self.chart_ax.bar(categories, values, color=colors, width=0.5)
        self.chart_ax.set_title("Network Attack Surface Analysis", pad=15, weight="bold")
        self.chart_ax.set_ylabel("Detected Instance Count")
        self.chart_ax.grid(axis='y', linestyle='--', alpha=0.7)

        for bar in bars:
            yval = bar.get_height()
            self.chart_ax.text(bar.get_x() + bar.get_width() / 2.0, yval + 0.1, int(yval), ha='center', va='bottom', weight='bold')

        self.chart_fig.tight_layout()
        self.chart_canvas.draw()

if __name__ == "__main__":
    app = NmapAnalyticsGUI()
    app.mainloop()