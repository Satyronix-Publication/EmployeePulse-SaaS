# employees.py
# Feature 1: Employee Directory CRUD & Search Engine

import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import config
from database import execute_query

class EmployeesView(tk.Frame):
    def __init__(self, parent, user):
        super().__init__(parent, bg=config.get_theme()["bg"])
        self.user = user
        self.theme = config.get_theme()
        self.build_ui()
        self.load_employees()

    def build_ui(self):
        top_bar = tk.Frame(self, bg=self.theme["card_bg"], pady=10)   # FIXED: was pdy=10
        top_bar.pack(fill="x", padx=15, pady=10)

        lbl_title = tk.Label(top_bar, text="Employee Directory",
                             font=("Segoe UI", 14, "bold"),
                             fg=self.theme["fg"], bg=self.theme["card_bg"])
        lbl_title.pack(side="left", padx=10)

        lbl_search = tk.Label(top_bar, text="Search:",
                              font=("Segoe UI", 10),
                              fg=self.theme["fg_dim"], bg=self.theme["card_bg"])
        lbl_search.pack(side="left", padx=(20, 5))

        self.ent_search = tk.Entry(top_bar, font=("Segoe UI", 10),
                                   bg=self.theme["entry_bg"], fg=self.theme["fg"],
                                   insertbackground=self.theme["fg"], width=22)
        self.ent_search.pack(side="left", padx=5)
        self.ent_search.bind("<KeyRelease>", lambda e: self.load_employees())

        btn_add = tk.Button(top_bar, text="+ Add New Employee",
                            font=("Segoe UI", 10, "bold"),
                            bg=self.theme["accent"], fg="white",
                            bd=0, cursor="hand2", padx=10,
                            command=self.open_add_dialog)
        btn_add.pack(side="right", padx=10)

        btn_refresh = tk.Button(top_bar, text="Refresh",
                                font=("Segoe UI", 10),
                                bg=self.theme["sidebar_bg"], fg=self.theme["fg"],
                                bd=0, cursor="hand2", padx=8,
                                command=self.load_employees)
        btn_refresh.pack(side="right", padx=5)

        # Treeview Table
        table_frame = tk.Frame(self, bg=self.theme["card_bg"])
        table_frame.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        cols = ("ID", "First Name", "Last Name", "Email", "Phone",
                "Department", "Designation", "Salary", "Join Date", "Status")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=15)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)

        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor="center")
        self.tree.column("ID", width=70)
        self.tree.column("Email", width=160)
        self.tree.column("Department", width=120)

        btn_frame = tk.Frame(self, bg=self.theme["bg"])
        btn_frame.pack(fill="x", padx=15, pady=5)

        tk.Button(btn_frame, text="Edit Employee",
                  font=("Segoe UI", 10), bg=self.theme["info"], fg="white",
                  bd=0, cursor="hand2", padx=10,
                  command=self.open_edit_dialog).pack(side="left", padx=5)

        tk.Button(btn_frame, text="Delete Record",
                  font=("Segoe UI", 10), bg=self.theme["danger"], fg="white",
                  bd=0, cursor="hand2", padx=10,
                  command=self.delete_employee).pack(side="left", padx=5)

    def load_employees(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        search = self.ent_search.get().strip()
        if search:
            query = """SELECT e.*, d.dept_name FROM employees e
                       LEFT JOIN departments d ON e.dept_id = d.dept_id
                       WHERE e.emp_id LIKE %s OR e.first_name LIKE %s
                          OR e.last_name LIKE %s OR e.email LIKE %s"""
            p = f"%{search}%"
            rows = execute_query(query, (p, p, p, p), fetchall=True)
        else:
            rows = execute_query(
                "SELECT e.*, d.dept_name FROM employees e LEFT JOIN departments d ON e.dept_id = d.dept_id",
                fetchall=True)

        if rows:
            for r in rows:
                self.tree.insert("", "end", values=(
                    r["emp_id"], r["first_name"], r["last_name"],
                    r["email"], r["phone"],
                    r.get("dept_name") or "N/A",
                    r["designation"], f"${r['salary']:,.2f}",
                    r["join_date"], r["status"]
                ))

    def open_add_dialog(self):
        self.open_employee_form(title="Add New Employee")

    def open_edit_dialog(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select an employee row to edit.")
            return
        self.open_employee_form(title="Edit Employee",
                                data=self.tree.item(selected[0])["values"])

    def open_employee_form(self, title, data=None):
        win = tk.Toplevel(self)
        win.title(title)
        win.geometry("450x520")
        win.configure(bg=self.theme["card_bg"])
        win.grab_set()

        fields = [
            ("Emp ID:", "emp_id"), ("First Name:", "first_name"),
            ("Last Name:", "last_name"), ("Email:", "email"),
            ("Phone:", "phone"), ("Designation:", "designation"),
            ("Salary ($):", "salary"),
        ]
        entries = {}
        for i, (lbl_txt, key) in enumerate(fields):
            tk.Label(win, text=lbl_txt, font=("Segoe UI", 10, "bold"),
                     fg=self.theme["fg"], bg=self.theme["card_bg"]
                     ).grid(row=i, column=0, sticky="w", padx=20, pady=7)
            e = tk.Entry(win, font=("Segoe UI", 10),
                         bg=self.theme["entry_bg"], fg=self.theme["fg"],
                         insertbackground=self.theme["fg"])
            e.grid(row=i, column=1, sticky="ew", padx=20, pady=7)
            entries[key] = e

        tk.Label(win, text="Department:", font=("Segoe UI", 10, "bold"),
                 fg=self.theme["fg"], bg=self.theme["card_bg"]
                 ).grid(row=len(fields), column=0, sticky="w", padx=20, pady=7)
        depts = execute_query("SELECT dept_id, dept_name FROM departments", fetchall=True) or []
        dept_map = {d["dept_name"]: d["dept_id"] for d in depts}
        cmb_dept = ttk.Combobox(win, values=list(dept_map.keys()), state="readonly")
        cmb_dept.grid(row=len(fields), column=1, sticky="ew", padx=20, pady=7)
        if depts:
            cmb_dept.current(0)

        if data:
            entries["emp_id"].insert(0, data[0]);  entries["emp_id"].configure(state="disabled")
            entries["first_name"].insert(0, data[1])
            entries["last_name"].insert(0, data[2])
            entries["email"].insert(0, data[3])
            entries["phone"].insert(0, data[4])
            if data[5] in dept_map: cmb_dept.set(data[5])
            entries["designation"].insert(0, data[6])
            entries["salary"].insert(0, str(data[7]).replace("$", "").replace(",", ""))
        else:
            cnt = (execute_query("SELECT COUNT(*) as cnt FROM employees", fetchone=True) or {}).get("cnt", 0)
            entries["emp_id"].insert(0, f"EMP{int(cnt)+1:03d}")

        def save():
            eid = entries["emp_id"].get().strip()
            fn  = entries["first_name"].get().strip()
            ln  = entries["last_name"].get().strip()
            em  = entries["email"].get().strip()
            ph  = entries["phone"].get().strip()
            desg = entries["designation"].get().strip()
            dept_id = dept_map.get(cmb_dept.get(), 1)
            try:
                sal = float(entries["salary"].get().strip() or 0)
            except ValueError:
                messagebox.showerror("Error", "Invalid salary amount.")
                return
            if not fn or not ln or not em:
                messagebox.showwarning("Validation", "First Name, Last Name, and Email are required.")
                return
            today = datetime.date.today().strftime("%Y-%m-%d")
            if data:
                execute_query("""UPDATE employees SET first_name=%s, last_name=%s,
                                 email=%s, phone=%s, dept_id=%s, designation=%s,
                                 salary=%s WHERE emp_id=%s""",
                              (fn, ln, em, ph, dept_id, desg, sal, eid))
            else:
                execute_query("""INSERT INTO employees
                    (emp_id, first_name, last_name, email, phone, dept_id, designation, salary, join_date)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                              (eid, fn, ln, em, ph, dept_id, desg, sal, today))
                execute_query("INSERT INTO users (username, password, role, employee_id) VALUES (%s,%s,%s,%s)",
                              (eid.lower(), "emp123", "Employee", eid))
            execute_query("INSERT INTO audit_logs (username, action, timestamp) VALUES (%s,%s,%s)",
                          (self.user.get("username", "Admin"),
                           f"{'Updated' if data else 'Created'} employee {eid}",
                           datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            win.destroy(); self.load_employees()
            messagebox.showinfo("Success", "Employee record saved.")

        tk.Button(win, text="Save Employee", font=("Segoe UI", 11, "bold"),
                  bg=self.theme["accent"], fg="white", bd=0, cursor="hand2",
                  command=save
                  ).grid(row=len(fields)+1, column=0, columnspan=2,
                         sticky="ew", padx=20, pady=20)

    def delete_employee(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Select an employee to delete.")
            return
        emp_id = self.tree.item(selected[0])["values"][0]
        if messagebox.askyesno("Confirm Delete", f"Delete employee {emp_id}?"):
            execute_query("DELETE FROM employees WHERE emp_id = %s", (emp_id,))
            execute_query("DELETE FROM users WHERE employee_id = %s", (emp_id,))
            self.load_employees()
