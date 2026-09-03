# dashboard.py
# Employee Management SaaS System - Main Dashboard Engine & Navigation

import tkinter as tk
from tkinter import ttk, messagebox
import config

from employees import EmployeesView
from departments import DepartmentsView
from payroll import PayrollView
from attendance_leave import AttendanceLeaveView
from performance import PerformanceView
from shifts import ShiftsView
from tasks import TasksView
from id_cards import IDCardsView
from analytics import AnalyticsView
from audit_security import AuditSecurityView
from kudos import KudosView
from ai_chat import AIChatView
from floor_plan import FloorPlanView

class DashboardWindow:
    def __init__(self, root, user, on_logout):
        self.root = root
        self.user = user
        self.on_logout = on_logout
        self.current_view = None
        self.nav_buttons = {}

        self.root.title(f"{config.APP_NAME} - Enterprise Portal [{self.user['role']}]")
        self.root.geometry("1280x760")
        self.root.minsize(1024, 600)
        self.root.resizable(True, True)

        config.apply_ttk_styles(self.root)
        self.apply_theme()
        self.build_ui()
        self.switch_tab("analytics")

    def apply_theme(self):
        theme = config.get_theme()
        self.root.configure(bg=theme["bg"])

    def build_ui(self):
        theme = config.get_theme()

        # 1. TOP HEADER BAR
        top_bar = tk.Frame(self.root, bg=theme["top_bar"], height=65)
        top_bar.pack(side="top", fill="x")
        top_bar.pack_propagate(False)

        # Custom Logo
        config.logo_canvas(top_bar, size=40, bg=theme["top_bar"]).pack(side="left", padx=(20, 10), pady=12)

        lbl_logo_text = tk.Label(top_bar, text="EmployeePulse SaaS", font=("Segoe UI", 16, "bold"), fg=theme["accent"], bg=theme["top_bar"])
        lbl_logo_text.pack(side="left")

        self.lbl_breadcrumb = tk.Label(top_bar, text=" / Analytics Dashboard", font=("Segoe UI", 11, "bold"), fg=theme["fg_dim"], bg=theme["top_bar"])
        self.lbl_breadcrumb.pack(side="left")

        # Right Action Pills
        btn_logout = tk.Button(top_bar, text="Logout", font=("Segoe UI", 9, "bold"), bg=theme["danger"], fg="white", bd=0, cursor="hand2", padx=15, pady=6, command=self.handle_logout)
        btn_logout.pack(side="right", padx=20)

        # Theme Toggle
        self.theme_toggle = config.ThemeToggle(top_bar, command=self.toggle_theme, bg=theme["top_bar"])
        self.theme_toggle.pack(side="right", padx=15, pady=17)

        # User Avatar Pill
        user_frame = tk.Frame(top_bar, bg=theme["sidebar_bg"], bd=1, relief="solid", padx=12, pady=5)
        user_frame.pack(side="right", padx=15)

        user_info = f"{self.user['username']}  |  {self.user['role']}"
        lbl_user = tk.Label(user_frame, text=user_info, font=("Segoe UI", 9, "bold"), fg=theme["fg"], bg=theme["sidebar_bg"])
        lbl_user.pack()

        # 2. MAIN CONTAINER
        main_container = tk.Frame(self.root, bg=theme["bg"])
        main_container.pack(fill="both", expand=True)

        # Sidebar
        self.sidebar = tk.Frame(main_container, bg=theme["sidebar_bg"], width=230)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Content Frame
        self.content_frame = tk.Frame(main_container, bg=theme["bg"])
        self.content_frame.pack(side="right", fill="both", expand=True)

        # 3. SIDEBAR NAVIGATION
        nav_items = [
            ("analytics", "Analytics Dashboard"),
            ("employees", "Employee Directory"),
            ("departments", "Departments & Roles"),
            ("payroll", "Payroll & Salary"),
            ("attendance", "Attendance & Leaves"),
            ("performance", "Performance Appraisals"),
            ("shifts", "Shift Scheduling"),
            ("tasks", "Task Allocation"),
            ("id_cards", "Digital ID & Vault"),
            ("kudos", "Kudos & Rewards"),
            ("floor_plan", "Office Floor Plan"),
            ("ai_chat", "Pulse AI Assistant"),
            ("security", "Security & Audit Logs")
        ]

        lbl_menu = tk.Label(self.sidebar, text="ENTERPRISE NAVIGATION", font=("Segoe UI", 8, "bold"), fg=theme["fg_dim"], bg=theme["sidebar_bg"])
        lbl_menu.pack(anchor="w", padx=18, pady=(25, 10))

        for key, label in nav_items:
            btn = tk.Button(
                self.sidebar,
                text=f"  {label}",
                font=("Segoe UI", 10),
                anchor="w",
                bg=theme["sidebar_bg"],
                fg=theme["fg"],
                activebackground=theme["accent"],
                activeforeground="white",
                bd=0,
                cursor="hand2",
                command=lambda k=key: self.switch_tab(k)
            )
            btn.pack(fill="x", pady=2, ipady=5)
            self.nav_buttons[key] = btn

    def switch_tab(self, tab_key):
        theme = config.get_theme()

        # Update button highlights
        for key, btn in self.nav_buttons.items():
            if key == tab_key:
                btn.configure(bg=theme["accent"], fg="white")
            else:
                btn.configure(bg=theme["sidebar_bg"], fg=theme["fg"])

        # Update Breadcrumb
        tab_names = {
            "analytics": "Executive Analytics",
            "employees": "Employee Directory",
            "departments": "Departments & Role Hierarchy",
            "payroll": "Payroll & Salary Processing",
            "attendance": "Attendance & Leave Management",
            "performance": "Performance Review & Ratings",
            "shifts": "Shift Scheduling & Roster",
            "tasks": "Task & Project Allocation",
            "id_cards": "Digital ID Badges & Document Vault",
            "kudos": "Gamified Rewards Leaderboard",
            "floor_plan": "Interactive Desk Booking Map",
            "ai_chat": "Pulse AI HR Assistant",
            "security": "System Security & Audit Logs"
        }
        self.lbl_breadcrumb.configure(text=f" / {tab_names.get(tab_key, 'Dashboard')}")

        if self.current_view:
            self.current_view.destroy()

        if tab_key == "analytics":
            self.current_view = AnalyticsView(self.content_frame, self.user)
        elif tab_key == "employees":
            self.current_view = EmployeesView(self.content_frame, self.user)
        elif tab_key == "departments":
            self.current_view = DepartmentsView(self.content_frame, self.user)
        elif tab_key == "payroll":
            self.current_view = PayrollView(self.content_frame, self.user)
        elif tab_key == "attendance":
            self.current_view = AttendanceLeaveView(self.content_frame, self.user)
        elif tab_key == "performance":
            self.current_view = PerformanceView(self.content_frame, self.user)
        elif tab_key == "shifts":
            self.current_view = ShiftsView(self.content_frame, self.user)
        elif tab_key == "tasks":
            self.current_view = TasksView(self.content_frame, self.user)
        elif tab_key == "id_cards":
            self.current_view = IDCardsView(self.content_frame, self.user)
        elif tab_key == "kudos":
            self.current_view = KudosView(self.content_frame, self.user)
        elif tab_key == "floor_plan":
            self.current_view = FloorPlanView(self.content_frame, self.user)
        elif tab_key == "ai_chat":
            self.current_view = AIChatView(self.content_frame, self.user)
        elif tab_key == "security":
            self.current_view = AuditSecurityView(self.content_frame, self.user)

        if self.current_view:
            self.current_view.pack(fill="both", expand=True)

    def toggle_theme(self):
        config.toggle_theme()
        config.apply_ttk_styles(self.root)
        active_key = [k for k, v in self.nav_buttons.items() if v.cget("bg") == config.get_theme()["accent"]]
        current_k = active_key[0] if active_key else "analytics"
        
        for widget in self.root.winfo_children():
            widget.destroy()

        self.apply_theme()
        self.build_ui()
        self.switch_tab(current_k)

    def handle_logout(self):
        if messagebox.askyesno("Confirm Logout", "Log out of your SaaS session?"):
            for widget in self.root.winfo_children():
                widget.destroy()
            self.on_logout()
