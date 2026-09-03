# id_cards.py
# Feature 8: Digital ID Card Badge Generator & Document Vault

import tkinter as tk
from tkinter import ttk, messagebox
import config
from database import execute_query

class IDCardsView(tk.Frame):
    def __init__(self, parent, user):
        super().__init__(parent, bg=config.get_theme()["bg"])
        self.user = user
        self.theme = config.get_theme()
        self.build_ui()

    def build_ui(self):
        # Header selection
        top_bar = tk.Frame(self, bg=self.theme["card_bg"], pady=10)
        top_bar.pack(fill="x", padx=15, pady=10)

        lbl_title = tk.Label(top_bar, text="🪪 Digital Employee ID Cards & Vault", font=("Segoe UI", 14, "bold"), fg=self.theme["fg"], bg=self.theme["card_bg"])
        lbl_title.pack(side="left", padx=10)

        tk.Label(top_bar, text="Select Employee:", font=("Segoe UI", 10, "bold"), fg=self.theme["fg_dim"], bg=self.theme["card_bg"]).pack(side="left", padx=(20, 5))
        
        self.emps = execute_query("""SELECT e.*, d.dept_name FROM employees e LEFT JOIN departments d ON e.dept_id = d.dept_id""", fetchall=True) or []
        self.emp_map = {f"{e['emp_id']} - {e['first_name']} {e['last_name']}": e for e in self.emps}

        self.cmb_emp = ttk.Combobox(top_bar, values=list(self.emp_map.keys()), state="readonly", font=("Segoe UI", 10), width=30)
        self.cmb_emp.pack(side="left", padx=5)
        self.cmb_emp.bind("<<ComboboxSelected>>", lambda e: self.render_badge())
        if self.emps:
            self.cmb_emp.current(0)

        # Main Container
        main_container = tk.Frame(self, bg=self.theme["bg"])
        main_container.pack(fill="both", expand=True, padx=15, pady=10)

        # ID Card Preview Canvas Frame (Left)
        badge_frame = tk.Frame(main_container, bg=self.theme["card_bg"], bd=2, relief="solid", width=340, height=480)
        badge_frame.pack(side="left", padx=20, pady=10)
        badge_frame.pack_propagate(False)

        self.badge_canvas = tk.Canvas(badge_frame, bg=self.theme["card_bg"], highlightthickness=0)
        self.badge_canvas.pack(fill="both", expand=True)

        # Document Vault Info (Right)
        vault_frame = tk.Frame(main_container, bg=self.theme["card_bg"], bd=1, relief="solid")
        vault_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        lbl_vault = tk.Label(vault_frame, text="📁 Verified Document Vault", font=("Segoe UI", 12, "bold"), fg=self.theme["fg"], bg=self.theme["card_bg"])
        lbl_vault.pack(anchor="w", padx=15, pady=15)

        cols = ("Doc Name", "Type", "Status", "Expiration Date")
        self.tree_doc = ttk.Treeview(vault_frame, columns=cols, show="headings", height=10)
        self.tree_doc.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        for c in cols:
            self.tree_doc.heading(c, text=c)
            self.tree_doc.column(c, width=110, anchor="center")

        self.render_badge()

    def render_badge(self):
        emp = self.emp_map.get(self.cmb_emp.get())
        if not emp:
            return

        c = self.badge_canvas
        c.delete("all")

        w, h = 340, 480

        # Background Header Gradient / Top Banner
        c.create_rectangle(0, 0, w, 110, fill=self.theme["top_bar"], outline="")
        c.create_text(w/2, 35, text="EmployeePulse SaaS", font=("Segoe UI", 15, "bold"), fill="white")
        c.create_text(w/2, 60, text="ENTERPRISE ACCESS BADGE", font=("Segoe UI", 9, "bold"), fill="#e2e8f0")

        # Avatar placeholder circle
        c.create_oval(w/2 - 45, 80, w/2 + 45, 170, fill=self.theme["accent"], outline="white", width=3)
        initials = f"{emp['first_name'][0]}{emp['last_name'][0]}"
        c.create_text(w/2, 125, text=initials, font=("Segoe UI", 24, "bold"), fill="white")

        # Name & Title
        full_name = f"{emp['first_name']} {emp['last_name']}"
        c.create_text(w/2, 195, text=full_name, font=("Segoe UI", 14, "bold"), fill=self.theme["fg"])
        c.create_text(w/2, 220, text=emp['designation'], font=("Segoe UI", 10, "italic"), fill=self.theme["accent"])

        # Details Divider Line
        c.create_line(30, 240, w-30, 240, fill=self.theme["border"], width=1)

        # Info Key-Values
        y_start = 260
        info_lines = [
            ("Employee ID:", emp["emp_id"]),
            ("Department:", emp.get("dept_name") or "Engineering"),
            ("Email:", emp["email"]),
            ("Phone:", emp["phone"]),
            ("Status:", emp["status"])
        ]

        for label, val in info_lines:
            c.create_text(40, y_start, text=label, font=("Segoe UI", 10, "bold"), fill=self.theme["fg_dim"], anchor="w")
            c.create_text(160, y_start, text=val, font=("Segoe UI", 10), fill=self.theme["fg"], anchor="w")
            y_start += 30

        # Barcode placeholder
        c.create_rectangle(40, 420, w-40, 455, fill="white", outline=self.theme["border"])
        # Draw fake barcode lines
        for x in range(50, w-50, 6):
            c.create_line(x, 425, x, 450, fill="black", width=2)
        c.create_text(w/2, 465, text=f"*{emp['emp_id']}*", font=("Courier", 8), fill=self.theme["fg_dim"])

        # Load dummy docs into tree
        for item in self.tree_doc.get_children():
            self.tree_doc.delete(item)

        docs = [
            ("Employment Contract", "PDF", "Verified", "2028-12-31"),
            ("National ID Card", "Scan", "Verified", "2030-05-15"),
            ("Tax Form W2 / 16", "Tax Document", "Verified", "2027-03-31"),
            ("Health Insurance", "Policy", "Active", "2026-12-31")
        ]
        for doc in docs:
            self.tree_doc.insert("", "end", values=doc)
