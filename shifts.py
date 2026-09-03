# shifts.py
# Feature 6: Shift Roster & Work Schedule Planner

import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import config
from database import execute_query

class ShiftsView(tk.Frame):
    def __init__(self, parent, user):
        super().__init__(parent, bg=config.get_theme()["bg"])
        self.user = user
        self.theme = config.get_theme()
        self.build_ui()
        self.load_shifts()

    def build_ui(self):
        top_bar = tk.Frame(self, bg=self.theme["card_bg"], pady=10)
        top_bar.pack(fill="x", padx=15, pady=10)

        lbl_title = tk.Label(top_bar, text="⏰ Shift Scheduling & Rosters", font=("Segoe UI", 14, "bold"), fg=self.theme["fg"], bg=self.theme["card_bg"])
        lbl_title.pack(side="left", padx=10)

        btn_assign = tk.Button(top_bar, text="+ Assign Shift Schedule", font=("Segoe UI", 10, "bold"), bg=self.theme["accent"], fg="white", bd=0, cursor="hand2", padx=10, command=self.open_assign_dialog)
        btn_assign.pack(side="right", padx=10)

        table_frame = tk.Frame(self, bg=self.theme["card_bg"])
        table_frame.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        cols = ("Shift ID", "Emp ID", "Employee Name", "Shift Type", "Start Time", "End Time", "Assigned Date")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=15)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)

        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="center")

    def load_shifts(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        rows = execute_query("""SELECT s.*, e.first_name, e.last_name FROM shifts s 
                                LEFT JOIN employees e ON s.emp_id = e.emp_id ORDER BY s.shift_id DESC""", fetchall=True)

        if rows:
            for r in rows:
                name = f"{r.get('first_name', '')} {r.get('last_name', '')}".strip() or r["emp_id"]
                self.tree.insert("", "end", values=(
                    r["shift_id"], r["emp_id"], name, r["shift_type"], r["start_time"], r["end_time"], r["assigned_date"]
                ))

    def open_assign_dialog(self):
        win = tk.Toplevel(self)
        win.title("Assign Shift Roster")
        win.geometry("380x380")
        win.configure(bg=self.theme["card_bg"])
        win.grab_set()

        tk.Label(win, text="Select Employee:", font=("Segoe UI", 10, "bold"), fg=self.theme["fg"], bg=self.theme["card_bg"]).pack(anchor="w", padx=20, pady=(15, 2))
        emps = execute_query("SELECT emp_id, first_name, last_name FROM employees", fetchall=True) or []
        emp_map = {f"{e['emp_id']} - {e['first_name']} {e['last_name']}": e["emp_id"] for e in emps}

        cmb_emp = ttk.Combobox(win, values=list(emp_map.keys()), state="readonly", font=("Segoe UI", 10))
        cmb_emp.pack(fill="x", padx=20, pady=(0, 10))
        if emps:
            cmb_emp.current(0)

        tk.Label(win, text="Shift Type:", font=("Segoe UI", 10, "bold"), fg=self.theme["fg"], bg=self.theme["card_bg"]).pack(anchor="w", padx=20, pady=(5, 2))
        cmb_shift = ttk.Combobox(win, values=["Morning Shift (09:00 AM - 06:00 PM)", "Evening Shift (02:00 PM - 11:00 PM)", "Night Shift (10:00 PM - 07:00 AM)"], state="readonly")
        cmb_shift.pack(fill="x", padx=20, pady=(0, 10))
        cmb_shift.current(0)

        tk.Label(win, text="Assigned Date (YYYY-MM-DD):", font=("Segoe UI", 10, "bold"), fg=self.theme["fg"], bg=self.theme["card_bg"]).pack(anchor="w", padx=20, pady=(5, 2))
        ent_date = tk.Entry(win, font=("Segoe UI", 10), bg=self.theme["entry_bg"], fg=self.theme["fg"])
        ent_date.pack(fill="x", padx=20, pady=(0, 15))
        ent_date.insert(0, datetime.date.today().strftime("%Y-%m-%d"))

        def save():
            eid = emp_map.get(cmb_emp.get())
            stype = cmb_shift.get()
            adate = ent_date.get().strip()

            if "Morning" in stype:
                stime, etime = "09:00 AM", "06:00 PM"
            elif "Evening" in stype:
                stime, etime = "02:00 PM", "11:00 PM"
            else:
                stime, etime = "10:00 PM", "07:00 AM"

            execute_query("INSERT INTO shifts (emp_id, shift_type, start_time, end_time, assigned_date) VALUES (%s, %s, %s, %s, %s)",
                          (eid, stype, stime, etime, adate))

            win.destroy()
            self.load_shifts()
            messagebox.showinfo("Success", "Shift roster assigned successfully.")

        btn_save = tk.Button(win, text="Assign Shift Roster", font=("Segoe UI", 11, "bold"), bg=self.theme["accent"], fg="white", bd=0, cursor="hand2", command=save)
        btn_save.pack(fill="x", padx=20, pady=20)
