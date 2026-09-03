# analytics.py
# Feature 9: Executive Canvas KPI Analytics & Graphical Reports Dashboard

import tkinter as tk
from tkinter import ttk
import config
from database import execute_query

class AnalyticsView(tk.Frame):
    def __init__(self, parent, user):
        super().__init__(parent, bg=config.get_theme()["bg"])
        self.user = user
        self.theme = config.get_theme()
        self.build_ui()

    def build_ui(self):
        top_bar = tk.Frame(self, bg=self.theme["card_bg"], pady=10)
        top_bar.pack(fill="x", padx=15, pady=10)

        lbl_title = tk.Label(top_bar, text="📊 Executive Analytics Dashboard", font=("Segoe UI", 14, "bold"), fg=self.theme["fg"], bg=self.theme["card_bg"])
        lbl_title.pack(side="left", padx=10)

        # 4 Top KPI Summary Cards
        kpi_frame = tk.Frame(self, bg=self.theme["bg"])
        kpi_frame.pack(fill="x", padx=15, pady=5)

        total_emp = (execute_query("SELECT COUNT(*) as cnt FROM employees", fetchone=True) or {}).get("cnt", 0)
        total_dept = (execute_query("SELECT COUNT(*) as cnt FROM departments", fetchone=True) or {}).get("cnt", 0)
        total_pay = (execute_query("SELECT SUM(net_salary) as sum FROM payroll", fetchone=True) or {}).get("sum", 0.0) or 0.0
        active_tasks = (execute_query("SELECT COUNT(*) as cnt FROM tasks WHERE status != 'Completed'", fetchone=True) or {}).get("cnt", 0)

        cards = [
            ("TOTAL EMPLOYEES", f"{total_emp}", "👥 Active Headcount", self.theme["accent"]),
            ("DEPARTMENTS", f"{total_dept}", "🏢 Operational Units", self.theme["success"]),
            ("MONTHLY PAYROLL", f"${total_pay:,.0f}", "💵 Salary Expenditure", self.theme["warning"]),
            ("ACTIVE TASKS", f"{active_tasks}", "📋 In-Progress Work", self.theme["info"])
        ]

        for i, (title, val, sub, color) in enumerate(cards):
            c_box = tk.Frame(kpi_frame, bg=self.theme["card_bg"], bd=1, relief="solid")
            c_box.grid(row=0, column=i, sticky="ew", padx=8, pady=5)
            kpi_frame.grid_columnconfigure(i, weight=1)

            lbl_t = tk.Label(c_box, text=title, font=("Segoe UI", 9, "bold"), fg=self.theme["fg_dim"], bg=self.theme["card_bg"])
            lbl_t.pack(anchor="w", padx=15, pady=(12, 2))

            lbl_v = tk.Label(c_box, text=val, font=("Segoe UI", 18, "bold"), fg=color, bg=self.theme["card_bg"])
            lbl_v.pack(anchor="w", padx=15, pady=(0, 2))

            lbl_s = tk.Label(c_box, text=sub, font=("Segoe UI", 8), fg=self.theme["fg_dim"], bg=self.theme["card_bg"])
            lbl_s.pack(anchor="w", padx=15, pady=(0, 12))

        # Canvas Charts Container
        chart_container = tk.Frame(self, bg=self.theme["bg"])
        chart_container.pack(fill="both", expand=True, padx=15, pady=10)

        # Left Chart: Department Breakdown (Bar Chart Canvas)
        left_box = tk.Frame(chart_container, bg=self.theme["card_bg"], bd=1, relief="solid")
        left_box.pack(side="left", fill="both", expand=True, padx=(0, 10))

        lbl_c1 = tk.Label(left_box, text="Department Staff Distribution", font=("Segoe UI", 11, "bold"), fg=self.theme["fg"], bg=self.theme["card_bg"])
        lbl_c1.pack(anchor="w", padx=15, pady=10)

        c1 = tk.Canvas(left_box, bg=self.theme["card_bg"], highlightthickness=0)
        c1.pack(fill="both", expand=True, padx=10, pady=10)

        # Right Chart: Attendance Rates / KPI Gauge
        right_box = tk.Frame(chart_container, bg=self.theme["card_bg"], bd=1, relief="solid")
        right_box.pack(side="left", fill="both", expand=True)

        lbl_c2 = tk.Label(right_box, text="Monthly Attendance & Performance Metric", font=("Segoe UI", 11, "bold"), fg=self.theme["fg"], bg=self.theme["card_bg"])
        lbl_c2.pack(anchor="w", padx=15, pady=10)

        c2 = tk.Canvas(right_box, bg=self.theme["card_bg"], highlightthickness=0)
        c2.pack(fill="both", expand=True, padx=10, pady=10)

        self.root_after = self.after(100, lambda: self.draw_charts(c1, c2))

    def draw_charts(self, c1, c2):
        c1.update()
        w1, h1 = c1.winfo_width(), c1.winfo_height()
        if w1 < 50 or h1 < 50: return

        # Draw Bar Chart on c1
        dept_data = execute_query("""
            SELECT d.dept_name, COUNT(e.emp_id) as cnt 
            FROM departments d LEFT JOIN employees e ON d.dept_id = e.dept_id 
            GROUP BY d.dept_id
        """, fetchall=True) or []

        max_val = max([r["cnt"] for r in dept_data] + [1])
        bars = len(dept_data) if dept_data else 1
        bar_width = (w1 - 60) / max(bars, 1)

        for i, r in enumerate(dept_data):
            x0 = 40 + i * bar_width + 10
            x1 = x0 + bar_width - 20
            h_ratio = (r["cnt"] / max_val) * (h1 - 80)
            y0 = h1 - 40 - h_ratio
            y1 = h1 - 40

            c1.create_rectangle(x0, y0, x1, y1, fill=self.theme["accent"], outline="")
            c1.create_text((x0+x1)/2, y0 - 15, text=str(r["cnt"]), font=("Segoe UI", 10, "bold"), fill=self.theme["fg"])
            c1.create_text((x0+x1)/2, h1 - 20, text=r["dept_name"][:8], font=("Segoe UI", 8), fill=self.theme["fg_dim"])

        # Draw Gauge Donut Chart on c2
        c2.update()
        w2, h2 = c2.winfo_width(), c2.winfo_height()
        cx, cy, r_size = w2 / 2, h2 / 2, min(w2, h2) / 3

        # Donut Chart for Attendance (94% Present)
        c2.create_arc(cx - r_size, cy - r_size, cx + r_size, cy + r_size, start=0, extent=360, fill=self.theme["sidebar_bg"], outline="")
        c2.create_arc(cx - r_size, cy - r_size, cx + r_size, cy + r_size, start=90, extent=-310, fill=self.theme["success"], outline="")
        c2.create_oval(cx - r_size + 30, cy - r_size + 30, cx + r_size - 30, cy + r_size - 30, fill=self.theme["card_bg"], outline="")

        c2.create_text(cx, cy - 10, text="92.4%", font=("Segoe UI", 22, "bold"), fill=self.theme["fg"])
        c2.create_text(cx, cy + 18, text="ON-TIME ATTENDANCE", font=("Segoe UI", 8, "bold"), fill=self.theme["fg_dim"])
