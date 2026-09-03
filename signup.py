# signup.py
# Self-Service Account Registration & Sign Up Interface

import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import config
from database import execute_query

class SignUpWindow:
    def __init__(self, root, on_navigate_login, on_navigate_welcome, on_login_success):
        self.root = root
        self.on_navigate_login = on_navigate_login
        self.on_navigate_welcome = on_navigate_welcome
        self.on_login_success = on_login_success
        self.theme = config.get_theme()

        self.root.title(f"{config.APP_NAME} - Create Account")
        self.root.geometry("560x720")
        self.root.resizable(False, False)

        self.center_window()
        self.root.configure(bg=self.theme["bg"])
        self.build_ui()

    def center_window(self):
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        ws = self.root.winfo_screenwidth()
        hs = self.root.winfo_screenheight()
        x = (ws / 2) - (w / 2)
        y = (hs / 2) - (h / 2)
        self.root.geometry(f'{w}x{h}+{int(x)}+{int(y)}')

    def build_ui(self):
        theme = config.get_theme()

        # Header Frame
        header = tk.Frame(self.root, bg=theme["top_bar"], height=80)
        header.pack(fill="x")
        header.pack_propagate(False)

        lbl_title = tk.Label(header, text="💼 EmployeePulse SaaS Registration", font=("Segoe UI", 16, "bold"), fg=theme["accent"], bg=theme["top_bar"])
        lbl_title.pack(side="top", pady=(15, 2))

        lbl_sub = tk.Label(header, text="Create your Enterprise Account & Employee Profile", font=("Segoe UI", 9), fg=theme["fg_dim"], bg=theme["top_bar"])
        lbl_sub.pack(side="top")

        # Container Card
        card = tk.Frame(self.root, bg=theme["card_bg"], bd=1, relief="solid")
        card.pack(fill="both", expand=True, padx=35, pady=25)

        # Form Fields Grid
        grid_frame = tk.Frame(card, bg=theme["card_bg"])
        grid_frame.pack(fill="both", expand=True, padx=25, pady=20)

        fields = [
            ("First Name:", "first_name", 0, 0),
            ("Last Name:", "last_name", 0, 1),
            ("Email Address:", "email", 1, 0),
            ("Phone Number:", "phone", 1, 1),
            ("Username:", "username", 2, 0),
            ("Designation:", "designation", 2, 1),
            ("Password:", "password", 3, 0),
            ("Confirm Password:", "confirm_pwd", 3, 1),
        ]

        self.entries = {}

        for lbl_txt, key, r, c in fields:
            f_frame = tk.Frame(grid_frame, bg=theme["card_bg"])
            f_frame.grid(row=r, column=c, sticky="ew", padx=10, pady=8)
            grid_frame.grid_columnconfigure(c, weight=1)

            lbl = tk.Label(f_frame, text=lbl_txt, font=("Segoe UI", 9, "bold"), fg=theme["fg_dim"], bg=theme["card_bg"])
            lbl.pack(anchor="w", pady=(0, 2))

            show_char = "•" if "pwd" in key or key == "password" else ""
            ent = tk.Entry(f_frame, font=("Segoe UI", 10), show=show_char, bg=theme["entry_bg"], fg=theme["fg"], insertbackground=theme["fg"], bd=1, relief="solid")
            ent.pack(fill="x", ipady=4)
            self.entries[key] = ent

        # Row 4: Role & Department Dropdowns
        r4_frame1 = tk.Frame(grid_frame, bg=theme["card_bg"])
        r4_frame1.grid(row=4, column=0, sticky="ew", padx=10, pady=8)
        tk.Label(r4_frame1, text="Account Role:", font=("Segoe UI", 9, "bold"), fg=theme["fg_dim"], bg=theme["card_bg"]).pack(anchor="w", pady=(0, 2))
        self.cmb_role = ttk.Combobox(r4_frame1, values=["Employee", "HR", "Admin"], state="readonly", font=("Segoe UI", 10))
        self.cmb_role.pack(fill="x", ipady=3)
        self.cmb_role.current(0)

        r4_frame2 = tk.Frame(grid_frame, bg=theme["card_bg"])
        r4_frame2.grid(row=4, column=1, sticky="ew", padx=10, pady=8)
        tk.Label(r4_frame2, text="Department:", font=("Segoe UI", 9, "bold"), fg=theme["fg_dim"], bg=theme["card_bg"]).pack(anchor="w", pady=(0, 2))

        depts = execute_query("SELECT dept_id, dept_name FROM departments", fetchall=True) or []
        self.dept_map = {d["dept_name"]: d["dept_id"] for d in depts}
        self.cmb_dept = ttk.Combobox(r4_frame2, values=list(self.dept_map.keys()), state="readonly", font=("Segoe UI", 10))
        self.cmb_dept.pack(fill="x", ipady=3)
        if depts:
            self.cmb_dept.current(0)

        # Register Button
        btn_submit = tk.Button(
            card,
            text="CREATE MY SAAS ACCOUNT",
            font=("Segoe UI", 11, "bold"),
            bg=theme["accent"],
            fg="white",
            activebackground=theme["accent_hover"],
            activeforeground="white",
            bd=0,
            cursor="hand2",
            command=self.handle_signup
        )
        btn_submit.pack(fill="x", padx=35, pady=(15, 10), ipady=8)

        # Footer Links
        footer_frame = tk.Frame(card, bg=theme["card_bg"])
        footer_frame.pack(fill="x", padx=35, pady=(0, 15))

        btn_login = tk.Button(footer_frame, text="Already have an account? Sign In", font=("Segoe UI", 9), bg=theme["card_bg"], fg=theme["accent"], bd=0, cursor="hand2", command=self.on_navigate_login)
        btn_login.pack(side="left")

        btn_welcome = tk.Button(footer_frame, text="← Back to Welcome Screen", font=("Segoe UI", 9), bg=theme["card_bg"], fg=theme["fg_dim"], bd=0, cursor="hand2", command=self.on_navigate_welcome)
        btn_welcome.pack(side="right")

    def handle_signup(self):
        fn = self.entries["first_name"].get().strip()
        ln = self.entries["last_name"].get().strip()
        em = self.entries["email"].get().strip()
        ph = self.entries["phone"].get().strip()
        user = self.entries["username"].get().strip()
        desg = self.entries["designation"].get().strip()
        pwd = self.entries["password"].get().strip()
        cpwd = self.entries["confirm_pwd"].get().strip()
        role = self.cmb_role.get()
        dept_id = self.dept_map.get(self.cmb_dept.get(), 1)

        if not fn or not ln or not em or not user or not pwd:
            messagebox.showwarning("Validation Error", "First Name, Last Name, Email, Username, and Password are required.")
            return

        if pwd != cpwd:
            messagebox.showerror("Error", "Passwords do not match.")
            return

        # Check existing username
        existing = execute_query("SELECT id FROM users WHERE username = %s", (user,), fetchone=True)
        if existing:
            messagebox.showerror("Error", f"Username '{user}' is already taken.")
            return

        # Generate Employee ID
        emp_count = (execute_query("SELECT COUNT(*) as cnt FROM employees", fetchone=True) or {}).get("cnt", 0)
        emp_id = f"EMP{emp_count + 1:03d}"
        today = datetime.date.today().strftime("%Y-%m-%d")

        # 1. Create Employee Record
        execute_query("""INSERT INTO employees (emp_id, first_name, last_name, email, phone, dept_id, designation, salary, join_date, status) 
                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'Active')""",
                      (emp_id, fn, ln, em, ph, dept_id, desg or "Team Member", 75000.0, today))

        # 2. Create User Credentials
        execute_query("INSERT INTO users (username, password, role, employee_id, status) VALUES (%s, %s, %s, %s, 'Active')",
                      (user, pwd, role, emp_id))

        # 3. Log Audit Activity
        execute_query("INSERT INTO audit_logs (username, action, timestamp) VALUES (%s, %s, %s)",
                      (user, f"User self-registered account ({role})", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

        messagebox.showinfo("Success", f"Account created successfully!\n\nEmployee ID: {emp_id}\nUsername: {user}")
        
        # Auto login
        user_record = execute_query("SELECT * FROM users WHERE username = %s", (user,), fetchone=True)
        self.on_login_success(user_record)
