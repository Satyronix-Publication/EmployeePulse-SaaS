# welcome.py
# EmployeePulse SaaS - Hero Welcome Screen

import tkinter as tk
import config
from database import execute_query


class WelcomeWindow:
    def __init__(self, root, on_navigate_login, on_navigate_signup, on_login_success):
        self.root = root
        self.on_navigate_login  = on_navigate_login
        self.on_navigate_signup = on_navigate_signup
        self.on_login_success   = on_login_success

        self.root.title("EmployeePulse SaaS - Welcome")
        self.root.geometry("820x640")
        self.root.minsize(700, 540)
        self.root.resizable(True, True)
        self._center()
        self.root.configure(bg=config.get_theme()["bg"])
        config.apply_ttk_styles(self.root)
        self._build()

    def _center(self):
        w, h = 820, 640
        ws, hs = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.root.geometry(f"{w}x{h}+{int(ws/2-w/2)}+{int(hs/2-h/2)}")

    def _build(self):
        t = config.get_theme()
        self.root.configure(bg=t["bg"])

        # ── Outer centred container ─────────────────────────────
        outer = tk.Frame(self.root, bg=t["bg"])
        outer.place(relx=0.5, rely=0.5, anchor="center")

        # ── Logo ────────────────────────────────────────────────
        config.logo_canvas(outer, size=160, bg=t["bg"]).pack(pady=(0, 0))

        # ── App Name ────────────────────────────────────────────
        tk.Label(outer, text="EmployeePulse SaaS",
                 font=("Segoe UI", 26, "bold"),
                 fg=t["fg"], bg=t["bg"]).pack(pady=(16, 3))

        tk.Label(outer, text="Professional Employee Management Platform",
                 font=("Segoe UI", 11),
                 fg=t["fg_dim"], bg=t["bg"]).pack(pady=(0, 22))

        # ── Feature Pills ───────────────────────────────────────
        pills = tk.Frame(outer, bg=t["bg"])
        pills.pack(pady=(0, 28))
        features = [("Employees", "People"), ("Payroll", "Finance"),
                    ("Shifts",    "Schedule"), ("Analytics", "Reports"),
                    ("ID Cards",  "Vault")]
        for i, (label, _) in enumerate(features):
            if i > 0:
                tk.Label(pills, text="  |  ", font=("Segoe UI", 10),
                         fg=t["border"], bg=t["bg"]).pack(side="left")
            tk.Label(pills, text=label, font=("Segoe UI", 11, "bold"),
                     fg=t["accent"], bg=t["bg"]).pack(side="left")

        # ── Primary CTA ─────────────────────────────────────────
        btn_start = tk.Button(outer, text="Get Started - Create Account",
                              font=("Segoe UI", 13, "bold"),
                              bg=t["success"], fg="white",
                              activebackground="#059669", activeforeground="white",
                              bd=0, cursor="hand2", pady=12, padx=30,
                              command=self.on_navigate_signup)
        btn_start.pack(pady=(0, 14))

        # ── Secondary links ─────────────────────────────────────
        links = tk.Frame(outer, bg=t["bg"])
        links.pack(pady=(0, 0))
        tk.Button(links, text="Already have an account?  Sign In",
                  font=("Segoe UI", 10, "bold"),
                  bg=t["bg"], fg=t["accent"], bd=0, cursor="hand2",
                  command=self.on_navigate_login).pack(side="left", padx=18)
        tk.Button(links, text="One-Click Demo Login",
                  font=("Segoe UI", 10),
                  bg=t["bg"], fg=t["accent_secondary"], bd=0, cursor="hand2",
                  command=self._demo_login).pack(side="left", padx=18)

        # ── Theme Toggle (top-right) ─────────────────────────────
        self._toggle = config.ThemeToggle(
            self.root,
            command=self._toggle_theme,
            bg=t["bg"]
        )
        self._toggle.place(relx=1.0, x=-16, y=12, anchor="ne")

        # ── Footer ──────────────────────────────────────────────
        tk.Label(self.root,
                 text="(c) 2026 EmployeePulse SaaS Platform. All rights reserved.",
                 font=("Segoe UI", 8), fg=t["fg_dim"], bg=t["bg"]
                 ).place(relx=0.5, rely=1.0, y=-12, anchor="s")

    def _demo_login(self):
        u = execute_query("SELECT * FROM users WHERE username = 'admin'", fetchone=True)
        if u:
            self.on_login_success(u)
        else:
            from tkinter import messagebox
            messagebox.showerror("Error", "Demo admin not found. Restart the app.")

    def _toggle_theme(self):
        config.toggle_theme()
        for w in self.root.winfo_children():
            w.destroy()
        self.root.configure(bg=config.get_theme()["bg"])
        self._build()
