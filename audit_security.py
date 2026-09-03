# audit_security.py
# Feature 10: Multi-Role Access Control, User Management & Audit Logs

import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import config
from database import execute_query

class AuditSecurityView(tk.Frame):
    def __init__(self, parent, user):
        super().__init__(parent, bg=config.get_theme()["bg"])
        self.user = user
        self.theme = config.get_theme()
        self.build_ui()

    def build_ui(self):
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=15, pady=10)

        # Tab 1: System Audit Log
        audit_tab = tk.Frame(notebook, bg=self.theme["bg"])
        notebook.add(audit_tab, text="📜 Real-time System Audit Trail")

        top_audit = tk.Frame(audit_tab, bg=self.theme["card_bg"], pady=8)
        top_audit.pack(fill="x", padx=10, pady=10)

        lbl_a = tk.Label(top_audit, text="Security & Operations Audit Trail", font=("Segoe UI", 12, "bold"), fg=self.theme["fg"], bg=self.theme["card_bg"])
        lbl_a.pack(side="left", padx=10)

        btn_ref = tk.Button(top_audit, text="🔄 Refresh Log", bg=self.theme["sidebar_bg"], fg=self.theme["fg"], font=("Segoe UI", 9), bd=0, cursor="hand2", command=self.load_logs)
        btn_ref.pack(side="right", padx=10)

        cols_audit = ("Log ID", "Username", "Action Description", "Timestamp")
        self.tree_audit = ttk.Treeview(audit_tab, columns=cols_audit, show="headings", height=15)
        self.tree_audit.pack(fill="both", expand=True, padx=10, pady=5)

        for c in cols_audit:
            self.tree_audit.heading(c, text=c)
            self.tree_audit.column(c, width=120, anchor="center")
        self.tree_audit.column("Action Description", width=350)

        # Tab 2: User Account Administration
        user_tab = tk.Frame(notebook, bg=self.theme["bg"])
        notebook.add(user_tab, text="🔐 Role & Account Administration")

        top_user = tk.Frame(user_tab, bg=self.theme["card_bg"], pady=8)
        top_user.pack(fill="x", padx=10, pady=10)

        btn_new_user = tk.Button(top_user, text="+ Create User Credentials", bg=self.theme["accent"], fg="white", font=("Segoe UI", 10, "bold"), bd=0, cursor="hand2", command=self.open_user_dialog)
        btn_new_user.pack(side="left", padx=10)

        cols_user = ("User ID", "Username", "Assigned Role", "Emp ID Link", "Account Status")
        self.tree_user = ttk.Treeview(user_tab, columns=cols_user, show="headings", height=15)
        self.tree_user.pack(fill="both", expand=True, padx=10, pady=5)

        for c in cols_user:
            self.tree_user.heading(c, text=c)
            self.tree_user.column(c, width=130, anchor="center")

        self.load_logs()
        self.load_users()

    def load_logs(self):
        for item in self.tree_audit.get_children():
            self.tree_audit.delete(item)

        rows = execute_query("SELECT * FROM audit_logs ORDER BY log_id DESC", fetchall=True)
        if rows:
            for r in rows:
                self.tree_audit.insert("", "end", values=(r["log_id"], r["username"], r["action"], r["timestamp"]))

    def load_users(self):
        for item in self.tree_user.get_children():
            self.tree_user.delete(item)

        rows = execute_query("SELECT * FROM users ORDER BY id ASC", fetchall=True)
        if rows:
            for r in rows:
                self.tree_user.insert("", "end", values=(r["id"], r["username"], r["role"], r["employee_id"] or "None", r["status"]))

    def open_user_dialog(self):
        win = tk.Toplevel(self)
        win.title("Create User Login")
        win.geometry("380x360")
        win.configure(bg=self.theme["card_bg"])

        fields = [("Username:", "user"), ("Password:", "pwd"), ("Emp ID Link:", "eid")]
        entries = {}

        for i, (lbl, key) in enumerate(fields):
            tk.Label(win, text=lbl, font=("Segoe UI", 10, "bold"), fg=self.theme["fg"], bg=self.theme["card_bg"]).grid(row=i, column=0, sticky="w", padx=20, pady=10)
            ent = tk.Entry(win, font=("Segoe UI", 10), bg=self.theme["entry_bg"], fg=self.theme["fg"])
            ent.grid(row=i, column=1, sticky="ew", padx=20, pady=10)
            entries[key] = ent

        tk.Label(win, text="Assigned Role:", font=("Segoe UI", 10, "bold"), fg=self.theme["fg"], bg=self.theme["card_bg"]).grid(row=len(fields), column=0, sticky="w", padx=20, pady=10)
        cmb_role = ttk.Combobox(win, values=["Admin", "HR", "Employee"], state="readonly")
        cmb_role.grid(row=len(fields), column=1, sticky="ew", padx=20, pady=10)
        cmb_role.current(0)

        def save():
            u = entries["user"].get().strip()
            p = entries["pwd"].get().strip()
            eid = entries["eid"].get().strip()
            role = cmb_role.get()

            if not u or not p:
                messagebox.showwarning("Validation Error", "Username and password required.")
                return

            execute_query("INSERT INTO users (username, password, role, employee_id, status) VALUES (%s, %s, %s, %s, 'Active')",
                          (u, p, role, eid))
            win.destroy()
            self.load_users()
            messagebox.showinfo("Success", f"User {u} created as {role}.")

        btn_save = tk.Button(win, text="Create User Account", bg=self.theme["accent"], fg="white", font=("Segoe UI", 11, "bold"), bd=0, cursor="hand2", command=save)
        btn_save.grid(row=len(fields)+1, column=0, columnspan=2, fill="x", padx=20, pady=20)
