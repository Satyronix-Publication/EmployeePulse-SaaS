# departments.py
# Feature 2: Department & Role Hierarchy Management

import tkinter as tk
from tkinter import ttk, messagebox
import config
from database import execute_query

class DepartmentsView(tk.Frame):
    def __init__(self, parent, user):
        super().__init__(parent, bg=config.get_theme()["bg"])
        self.user = user
        self.theme = config.get_theme()
        self.build_ui()
        self.load_departments()

    def build_ui(self):
        top_bar = tk.Frame(self, bg=self.theme["card_bg"], pady=10)
        top_bar.pack(fill="x", padx=15, pady=10)

        lbl_title = tk.Label(top_bar, text="🏢 Department & Role Hierarchy", font=("Segoe UI", 14, "bold"), fg=self.theme["fg"], bg=self.theme["card_bg"])
        lbl_title.pack(side="left", padx=10)

        btn_add = tk.Button(top_bar, text="+ Add Department", font=("Segoe UI", 10, "bold"), bg=self.theme["accent"], fg="white", bd=0, cursor="hand2", padx=10, command=self.open_add_dept)
        btn_add.pack(side="right", padx=10)

        # Treeview Table
        table_frame = tk.Frame(self, bg=self.theme["card_bg"])
        table_frame.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        cols = ("Dept ID", "Department Name", "Head of Department (HOD)", "Annual Budget", "Office Location", "Total Staff Count")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=15)
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)

        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=130, anchor="center")

        btn_frame = tk.Frame(self, bg=self.theme["bg"])
        btn_frame.pack(fill="x", padx=15, pady=5)

        btn_delete = tk.Button(btn_frame, text="🗑️ Delete Department", font=("Segoe UI", 10), bg=self.theme["danger"], fg="white", bd=0, cursor="hand2", padx=10, command=self.delete_dept)
        btn_delete.pack(side="left", padx=5)

    def load_departments(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        rows = execute_query("""
            SELECT d.*, COUNT(e.emp_id) as staff_count 
            FROM departments d 
            LEFT JOIN employees e ON d.dept_id = e.dept_id 
            GROUP BY d.dept_id
        """, fetchall=True)

        if rows:
            for r in rows:
                self.tree.insert("", "end", values=(
                    r["dept_id"], r["dept_name"], r["hod"] or "Unassigned", f"${r['budget']:,.2f}", r["location"] or "Main Campus", r.get("staff_count", 0)
                ))

    def open_add_dept(self):
        win = tk.Toplevel(self)
        win.title("Add New Department")
        win.geometry("400x380")
        win.configure(bg=self.theme["card_bg"])
        win.grab_set()

        fields = [("Department Name:", "name"), ("HOD Name:", "hod"), ("Annual Budget ($):", "budget"), ("Office Location:", "location")]
        entries = {}

        for i, (label, key) in enumerate(fields):
            tk.Label(win, text=label, font=("Segoe UI", 10, "bold"), fg=self.theme["fg"], bg=self.theme["card_bg"]).grid(row=i, column=0, sticky="w", padx=20, pady=10)
            ent = tk.Entry(win, font=("Segoe UI", 10), bg=self.theme["entry_bg"], fg=self.theme["fg"], insertbackground=self.theme["fg"])
            ent.grid(row=i, column=1, sticky="ew", padx=20, pady=10)
            entries[key] = ent

        def save():
            name = entries["name"].get().strip()
            hod = entries["hod"].get().strip()
            budget_str = entries["budget"].get().strip()
            loc = entries["location"].get().strip()

            if not name:
                messagebox.showwarning("Validation Error", "Department Name is required.")
                return

            try:
                budget = float(budget_str) if budget_str else 0.0
            except ValueError:
                messagebox.showerror("Error", "Invalid budget format.")
                return

            execute_query("INSERT INTO departments (dept_name, hod, budget, location) VALUES (%s, %s, %s, %s)",
                          (name, hod, budget, loc))

            win.destroy()
            self.load_departments()
            messagebox.showinfo("Success", "Department added successfully.")

        btn_save = tk.Button(win, text="Create Department", font=("Segoe UI", 11, "bold"), bg=self.theme["accent"], fg="white", bd=0, cursor="hand2", command=save)
        btn_save.grid(row=len(fields), column=0, columnspan=2, fill="x", padx=20, pady=20)

    def delete_dept(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a department to delete.")
            return
        dept_id = self.tree.item(selected[0])["values"][0]
        if messagebox.askyesno("Confirm Delete", f"Delete department #{dept_id}?"):
            execute_query("DELETE FROM departments WHERE dept_id = %s", (dept_id,))
            self.load_departments()
            messagebox.showinfo("Deleted", "Department deleted.")
