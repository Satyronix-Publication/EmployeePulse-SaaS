# login.py
# EmployeePulse SaaS - Combined Professional Auth Screen
# Sign In / Create Account tab toggle — no emojis, logo on both panels

import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import config
from database import execute_query


class LoginWindow:
    def __init__(self, root, on_login_success,
                 on_navigate_signup=None,
                 on_navigate_welcome=None):
        self.root = root
        self.on_login_success    = on_login_success
        self.on_navigate_welcome = on_navigate_welcome
        self._mode = tk.StringVar(value="signin")

        self.root.title(f"{config.APP_NAME} - Account Access")
        self.root.geometry("960x640")
        self.root.minsize(820, 560)
        self.root.resizable(True, True)
        self._center()
        self.root.configure(bg=config.get_theme()["bg"])
        config.apply_ttk_styles(self.root)
        self._build()

    def _center(self):
        w, h = 960, 640
        ws, hs = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.root.geometry(f"{w}x{h}+{int(ws/2-w/2)}+{int(hs/2-h/2)}")

    def _build(self):
        t = config.get_theme()

        split = tk.Frame(self.root, bg=t["bg"])
        split.pack(fill="both", expand=True)

        # ── LEFT BRAND PANEL ────────────────────────────────────
        left = tk.Frame(split, bg=t["sidebar_bg"], width=300)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        inner_l = tk.Frame(left, bg=t["sidebar_bg"])
        inner_l.place(relx=0.5, rely=0.45, anchor="center")

        # Logo — uses shared loader from config
        config.logo_canvas(inner_l, size=115, bg=t["sidebar_bg"]).pack(pady=(0, 16))

        tk.Label(inner_l, text="EmployeePulse SaaS",
                 font=("Segoe UI", 16, "bold"), fg=t["accent"],
                 bg=t["sidebar_bg"]).pack()
        tk.Label(inner_l, text="ENTERPRISE WORKFORCE PLATFORM",
                 font=("Segoe UI", 8, "bold"), fg=t["accent_secondary"],
                 bg=t["sidebar_bg"]).pack(pady=(2, 20))

        perks = [
            "Automated Payroll and Payslips",
            "Executive KPI Analytics",
            "Digital ID Badge Vault",
            "Shift Rosters and Scheduling",
            "Role Security and Audit Trail",
        ]
        for p in perks:
            tk.Label(inner_l, text=f"  {p}", font=("Segoe UI", 10),
                     fg=t["fg"], bg=t["sidebar_bg"]).pack(anchor="w", pady=4)

        if self.on_navigate_welcome:
            tk.Button(inner_l, text="Back to Welcome",
                      font=("Segoe UI", 9), bg=t["sidebar_bg"],
                      fg=t["fg_dim"], bd=0, cursor="hand2",
                      command=self.on_navigate_welcome
                      ).pack(anchor="w", pady=(22, 0))

        # ── RIGHT FORM PANEL ────────────────────────────────────
        right = tk.Frame(split, bg=t["bg"])
        right.pack(side="right", fill="both", expand=True)

        self._card_wrap = tk.Frame(right, bg=t["bg"])
        self._card_wrap.place(relx=0.5, rely=0.5, anchor="center")

        # Theme toggle (top-right of right panel)
        self._toggle = config.ThemeToggle(right, command=self._toggle_theme)
        self._toggle.place(relx=1.0, x=-16, y=12, anchor="ne")

        self._draw_form()

    def _draw_form(self):
        t   = config.get_theme()
        mode = self._mode.get()

        for w in self._card_wrap.winfo_children():
            w.destroy()

        # ── Tab Toggle Row ──────────────────────────────────────
        tab_row = tk.Frame(self._card_wrap, bg=t["card_bg"],
                           bd=1, relief="solid", width=430)
        tab_row.pack(fill="x")

        for label, val in [("Existing User  —  Sign In", "signin"),
                            ("New User  —  Create Account", "signup")]:
            is_active = (mode == val)
            tk.Button(tab_row, text=label,
                      font=("Segoe UI", 10, "bold" if is_active else "normal"),
                      bg=t["accent"] if is_active else t["card_bg"],
                      fg="white" if is_active else t["fg_dim"],
                      bd=0, cursor="hand2", padx=16, pady=10,
                      activebackground=t["accent"], activeforeground="white",
                      command=lambda v=val: self._switch_mode(v)
                      ).pack(side="left", fill="x", expand=True)

        # ── Form Card ───────────────────────────────────────────
        card = tk.Frame(self._card_wrap, bg=t["card_bg"],
                        bd=1, relief="solid", width=430)
        card.pack(fill="x")

        inner = tk.Frame(card, bg=t["card_bg"])
        inner.pack(fill="both", padx=30, pady=20)

        if mode == "signin":
            self._signin_form(inner, t)
        else:
            self._signup_form(inner, t)

    def _switch_mode(self, mode):
        self._mode.set(mode)
        self._draw_form()

    # ── helpers ───────────────────────────────────────────────────────────────
    def _lbl(self, parent, text, t):
        tk.Label(parent, text=text, font=("Segoe UI", 9, "bold"),
                 fg=t["fg_dim"], bg=t["card_bg"]).pack(anchor="w", pady=(7, 2))

    def _ent(self, parent, t, show="", ph=""):
        e = tk.Entry(parent, font=("Segoe UI", 11), show=show,
                     bg=t["entry_bg"], fg=t["fg"],
                     insertbackground=t["fg"], bd=0,
                     highlightthickness=1, highlightcolor=t["accent"],
                     highlightbackground=t["card_border"])
        e.pack(fill="x", ipady=6)
        if ph:
            e.insert(0, ph)
        return e

    # ── Sign In Form ──────────────────────────────────────────────────────────
    def _signin_form(self, p, t):
        tk.Label(p, text="Welcome back",
                 font=("Segoe UI", 17, "bold"), fg=t["fg"],
                 bg=t["card_bg"]).pack(anchor="w", pady=(0, 3))
        tk.Label(p, text="Sign in to your enterprise SaaS account",
                 font=("Segoe UI", 10), fg=t["fg_dim"],
                 bg=t["card_bg"]).pack(anchor="w", pady=(0, 10))

        self._lbl(p, "Username", t)
        self.ent_user = self._ent(p, t, ph="admin")
        self._lbl(p, "Password", t)
        self.ent_pass = self._ent(p, t, show="*", ph="admin123")
        self._lbl(p, "Login Role", t)
        self.cmb_role = ttk.Combobox(p, values=["Admin", "HR", "Employee"],
                                     state="readonly", font=("Segoe UI", 10))
        self.cmb_role.pack(fill="x", ipady=5); self.cmb_role.current(0)

        tk.Button(p, text="Sign In",
                  font=("Segoe UI", 11, "bold"),
                  bg=t["accent"], fg="white",
                  activebackground=t["accent_hover"], bd=0,
                  cursor="hand2", pady=10,
                  command=self._do_login).pack(fill="x", pady=(16, 6))

        tk.Button(p, text="View default credentials",
                  font=("Segoe UI", 8), bg=t["card_bg"],
                  fg=t["fg_dim"], bd=0, cursor="hand2",
                  command=self._hint).pack(anchor="e")

    # ── Create Account Form ───────────────────────────────────────────────────
    def _signup_form(self, p, t):
        tk.Label(p, text="Create your account",
                 font=("Segoe UI", 17, "bold"), fg=t["fg"],
                 bg=t["card_bg"]).pack(anchor="w", pady=(0, 3))
        tk.Label(p, text="Register as a new employee on the platform",
                 font=("Segoe UI", 10), fg=t["fg_dim"],
                 bg=t["card_bg"]).pack(anchor="w", pady=(0, 10))

        g = tk.Frame(p, bg=t["card_bg"])
        g.pack(fill="x")
        g.columnconfigure(0, weight=1); g.columnconfigure(1, weight=1)

        def ge(label, row, col, show=""):
            tk.Label(g, text=label, font=("Segoe UI", 9, "bold"),
                     fg=t["fg_dim"], bg=t["card_bg"]
                     ).grid(row=row*2, column=col, sticky="w", padx=(0, 8), pady=(5, 1))
            e = tk.Entry(g, font=("Segoe UI", 10), show=show,
                         bg=t["entry_bg"], fg=t["fg"], insertbackground=t["fg"],
                         bd=0, highlightthickness=1,
                         highlightcolor=t["accent"],
                         highlightbackground=t["card_border"])
            e.grid(row=row*2+1, column=col, sticky="ew", padx=(0, 8), ipady=5)
            return e

        self.r_fn    = ge("First Name",  0, 0)
        self.r_ln    = ge("Last Name",   0, 1)
        self.r_email = ge("Email",        1, 0)
        self.r_phone = ge("Phone",        1, 1)
        self.r_user  = ge("Username",     2, 0)
        self.r_desg  = ge("Designation",  2, 1)
        self.r_pwd   = ge("Password",     3, 0, show="*")
        self.r_cpwd  = ge("Confirm Password", 3, 1, show="*")

        rr = tk.Frame(p, bg=t["card_bg"])
        rr.pack(fill="x", pady=(8, 0))
        rr.columnconfigure(0, weight=1); rr.columnconfigure(1, weight=1)

        tk.Label(rr, text="Account Role:", font=("Segoe UI", 9, "bold"),
                 fg=t["fg_dim"], bg=t["card_bg"]
                 ).grid(row=0, column=0, sticky="w", padx=(0, 8))
        self.r_role = ttk.Combobox(rr, values=["Employee", "HR", "Admin"],
                                   state="readonly", font=("Segoe UI", 10))
        self.r_role.grid(row=1, column=0, sticky="ew", padx=(0, 8), ipady=4)
        self.r_role.current(0)

        depts = execute_query("SELECT dept_id, dept_name FROM departments", fetchall=True) or []
        self._dept_map = {d["dept_name"]: d["dept_id"] for d in depts}
        tk.Label(rr, text="Department:", font=("Segoe UI", 9, "bold"),
                 fg=t["fg_dim"], bg=t["card_bg"]
                 ).grid(row=0, column=1, sticky="w")
        self.r_dept = ttk.Combobox(rr, values=list(self._dept_map.keys()),
                                   state="readonly", font=("Segoe UI", 10))
        self.r_dept.grid(row=1, column=1, sticky="ew", ipady=4)
        if depts: self.r_dept.current(0)

        tk.Button(p, text="Create My Account",
                  font=("Segoe UI", 11, "bold"),
                  bg=t["accent_secondary"], fg="white",
                  activebackground="#4338ca", bd=0,
                  cursor="hand2", pady=10,
                  command=self._do_signup).pack(fill="x", pady=(14, 0))

    # ── Handlers ─────────────────────────────────────────────────────────────
    def _do_login(self):
        user = self.ent_user.get().strip()
        pwd  = self.ent_pass.get().strip()
        role = self.cmb_role.get().strip()
        if not user or not pwd:
            messagebox.showwarning("Required", "Username and Password are required.")
            return
        res = execute_query(
            "SELECT * FROM users WHERE username=%s AND password=%s AND role=%s AND status='Active'",
            (user, pwd, role), fetchone=True)
        if res:
            execute_query("INSERT INTO audit_logs (username, action, timestamp) VALUES (%s,%s,%s)",
                          (user, f"Logged in as {role}",
                           datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            self.on_login_success(res)
        else:
            messagebox.showerror("Access Denied", "Invalid Username, Password, or Role.")

    def _do_signup(self):
        fn   = self.r_fn.get().strip()
        ln   = self.r_ln.get().strip()
        em   = self.r_email.get().strip()
        ph   = self.r_phone.get().strip()
        user = self.r_user.get().strip()
        desg = self.r_desg.get().strip()
        pwd  = self.r_pwd.get().strip()
        cpwd = self.r_cpwd.get().strip()
        role = self.r_role.get()
        dept_id = self._dept_map.get(self.r_dept.get(), 1)

        if not fn or not ln or not em or not user or not pwd:
            messagebox.showwarning("Required",
                                   "First Name, Last Name, Email, Username and Password are required.")
            return
        if pwd != cpwd:
            messagebox.showerror("Error", "Passwords do not match.")
            return
        if execute_query("SELECT id FROM users WHERE username=%s", (user,), fetchone=True):
            messagebox.showerror("Error", f"Username '{user}' is already taken.")
            return

        cnt    = (execute_query("SELECT COUNT(*) as c FROM employees", fetchone=True) or {}).get("c", 0)
        emp_id = f"EMP{int(cnt)+1:03d}"
        today  = datetime.date.today().strftime("%Y-%m-%d")

        execute_query(
            """INSERT INTO employees
               (emp_id, first_name, last_name, email, phone, dept_id, designation, salary, join_date, status)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,'Active')""",
            (emp_id, fn, ln, em, ph, dept_id, desg or "Team Member", 75000.0, today))
        execute_query(
            "INSERT INTO users (username, password, role, employee_id, status) VALUES (%s,%s,%s,%s,'Active')",
            (user, pwd, role, emp_id))
        execute_query(
            "INSERT INTO audit_logs (username, action, timestamp) VALUES (%s,%s,%s)",
            (user, f"Self-registered as {role}",
             datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

        messagebox.showinfo("Account Created",
                            f"Welcome, {fn}!\n\nEmployee ID : {emp_id}\nUsername    : {user}")
        rec = execute_query("SELECT * FROM users WHERE username=%s", (user,), fetchone=True)
        self.on_login_success(rec)

    def _hint(self):
        messagebox.showinfo("Default Accounts",
                            "Admin    ->  admin / admin123\n"
                            "HR       ->  hr_manager / hr123\n"
                            "Employee ->  emp001 / emp123")

    def _toggle_theme(self):
        config.toggle_theme()
        config.apply_ttk_styles(self.root)
        for w in self.root.winfo_children():
            w.destroy()
        self.root.configure(bg=config.get_theme()["bg"])
        self._build()
