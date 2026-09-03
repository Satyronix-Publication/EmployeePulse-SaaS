# tasks.py
# Feature 7: Task & Project Allocation Tracker

import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import config
from database import execute_query

class TasksView(tk.Frame):
    def __init__(self, parent, user):
        super().__init__(parent, bg=config.get_theme()["bg"])
        self.user = user
        self.theme = config.get_theme()
        self.build_ui()
        self.load_tasks()

    def build_ui(self):
        top_bar = tk.Frame(self, bg=self.theme["card_bg"], pady=10)
        top_bar.pack(fill="x", padx=15, pady=10)

        lbl_title = tk.Label(top_bar, text="📋 Task & Project Allocation", font=("Segoe UI", 14, "bold"), fg=self.theme["fg"], bg=self.theme["card_bg"])
        lbl_title.pack(side="left", padx=10)

        btn_add = tk.Button(top_bar, text="+ Create New Task", font=("Segoe UI", 10, "bold"), bg=self.theme["accent"], fg="white", bd=0, cursor="hand2", padx=10, command=self.open_task_dialog)
        btn_add.pack(side="right", padx=10)

        table_frame = tk.Frame(self, bg=self.theme["card_bg"])
        table_frame.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        cols = ("Task ID", "Emp ID", "Assigned Employee", "Task Title", "Priority", "Deadline", "Status")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=15)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)

        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="center")
        self.tree.column("Task Title", width=220)

        btn_frame = tk.Frame(self, bg=self.theme["bg"])
        btn_frame.pack(fill="x", padx=15, pady=5)

        btn_complete = tk.Button(btn_frame, text="✅ Mark Completed", font=("Segoe UI", 10), bg=self.theme["success"], fg="white", bd=0, cursor="hand2", padx=10, command=self.mark_completed)
        btn_complete.pack(side="left", padx=5)

    def load_tasks(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        rows = execute_query("""SELECT t.*, e.first_name, e.last_name FROM tasks t 
                                LEFT JOIN employees e ON t.emp_id = e.emp_id ORDER BY t.task_id DESC""", fetchall=True)

        if rows:
            for r in rows:
                name = f"{r.get('first_name', '')} {r.get('last_name', '')}".strip() or r["emp_id"]
                self.tree.insert("", "end", values=(
                    r["task_id"], r["emp_id"], name, r["task_title"], r["priority"], r["deadline"], r["status"]
                ))

    def open_task_dialog(self):
        win = tk.Toplevel(self)
        win.title("Assign New Task")
        win.geometry("400x420")
        win.configure(bg=self.theme["card_bg"])
        win.grab_set()

        tk.Label(win, text="Assign To Employee:", font=("Segoe UI", 10, "bold"), fg=self.theme["fg"], bg=self.theme["card_bg"]).pack(anchor="w", padx=20, pady=(15, 2))
        emps = execute_query("SELECT emp_id, first_name, last_name FROM employees", fetchall=True) or []
        emp_map = {f"{e['emp_id']} - {e['first_name']} {e['last_name']}": e["emp_id"] for e in emps}

        cmb_emp = ttk.Combobox(win, values=list(emp_map.keys()), state="readonly", font=("Segoe UI", 10))
        cmb_emp.pack(fill="x", padx=20, pady=(0, 10))
        if emps:
            cmb_emp.current(0)

        tk.Label(win, text="Task Title:", font=("Segoe UI", 10, "bold"), fg=self.theme["fg"], bg=self.theme["card_bg"]).pack(anchor="w", padx=20, pady=(5, 2))
        ent_title = tk.Entry(win, font=("Segoe UI", 10), bg=self.theme["entry_bg"], fg=self.theme["fg"])
        ent_title.pack(fill="x", padx=20, pady=(0, 10))

        tk.Label(win, text="Priority Level:", font=("Segoe UI", 10, "bold"), fg=self.theme["fg"], bg=self.theme["card_bg"]).pack(anchor="w", padx=20, pady=(5, 2))
        cmb_prio = ttk.Combobox(win, values=["High", "Medium", "Low"], state="readonly")
        cmb_prio.pack(fill="x", padx=20, pady=(0, 10))
        cmb_prio.current(1)

        tk.Label(win, text="Deadline (YYYY-MM-DD):", font=("Segoe UI", 10, "bold"), fg=self.theme["fg"], bg=self.theme["card_bg"]).pack(anchor="w", padx=20, pady=(5, 2))
        ent_deadline = tk.Entry(win, font=("Segoe UI", 10), bg=self.theme["entry_bg"], fg=self.theme["fg"])
        ent_deadline.pack(fill="x", padx=20, pady=(0, 15))
        ent_deadline.insert(0, (datetime.date.today() + datetime.timedelta(days=7)).strftime("%Y-%m-%d"))

        def save():
            eid = emp_map.get(cmb_emp.get())
            title = ent_title.get().strip()
            prio = cmb_prio.get()
            dline = ent_deadline.get().strip()

            if not title:
                messagebox.showwarning("Validation Error", "Task Title is required.")
                return

            execute_query("INSERT INTO tasks (emp_id, task_title, priority, deadline, status) VALUES (%s, %s, %s, %s, 'In Progress')",
                          (eid, title, prio, dline))

            win.destroy()
            self.load_tasks()
            messagebox.showinfo("Success", "Task assigned successfully.")

        btn_save = tk.Button(win, text="Create Task Assignment", font=("Segoe UI", 11, "bold"), bg=self.theme["accent"], fg="white", bd=0, cursor="hand2", command=save)
        btn_save.pack(fill="x", padx=20, pady=15)

    def mark_completed(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Select a task row to complete.")
            return
        tid = self.tree.item(selected[0])["values"][0]
        execute_query("UPDATE tasks SET status = 'Completed' WHERE task_id = %s", (tid,))
        self.load_tasks()
        messagebox.showinfo("Completed", f"Task #{tid} marked as Completed.")
