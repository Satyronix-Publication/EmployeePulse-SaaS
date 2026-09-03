# attendance_leave.py
# Feature 4: Attendance Tracking & Leave Requests Engine

import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import config
from database import execute_query

class AttendanceLeaveView(tk.Frame):
    def __init__(self, parent, user):
        super().__init__(parent, bg=config.get_theme()["bg"])
        self.user = user
        self.theme = config.get_theme()
        self.build_ui()

    def build_ui(self):
        # Notebook tabs for Attendance vs Leaves
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=15, pady=10)

        # Tab 1: Attendance Log
        att_tab = tk.Frame(notebook, bg=self.theme["bg"])
        notebook.add(att_tab, text="📅 Daily Attendance Log")

        top_att = tk.Frame(att_tab, bg=self.theme["card_bg"], pady=8)
        top_att.pack(fill="x", padx=10, pady=10)

        btn_punch = tk.Button(top_att, text="⏱️ Quick Punch In / Out", font=("Segoe UI", 10, "bold"), bg=self.theme["accent"], fg="white", bd=0, cursor="hand2", padx=10, command=self.quick_punch)
        btn_punch.pack(side="left", padx=10)

        cols_att = ("Att ID", "Emp ID", "Employee Name", "Date", "Status", "Check In", "Check Out")
        self.tree_att = ttk.Treeview(att_tab, columns=cols_att, show="headings", height=12)
        self.tree_att.pack(fill="both", expand=True, padx=10, pady=5)

        for c in cols_att:
            self.tree_att.heading(c, text=c)
            self.tree_att.column(c, width=110, anchor="center")

        # Tab 2: Leave Requests & Approval
        leave_tab = tk.Frame(notebook, bg=self.theme["bg"])
        notebook.add(leave_tab, text="🏖️ Leave Requests & Approvals")

        top_leave = tk.Frame(leave_tab, bg=self.theme["card_bg"], pady=8)
        top_leave.pack(fill="x", padx=10, pady=10)

        btn_apply = tk.Button(top_leave, text="+ Apply for Leave", font=("Segoe UI", 10, "bold"), bg=self.theme["accent"], fg="white", bd=0, cursor="hand2", padx=10, command=self.apply_leave_dialog)
        btn_apply.pack(side="left", padx=10)

        btn_approve = tk.Button(top_leave, text="✅ Approve Selected", font=("Segoe UI", 10), bg=self.theme["success"], fg="white", bd=0, cursor="hand2", padx=10, command=lambda: self.update_leave_status("Approved"))
        btn_approve.pack(side="right", padx=5)

        btn_reject = tk.Button(top_leave, text="❌ Reject Selected", font=("Segoe UI", 10), bg=self.theme["danger"], fg="white", bd=0, cursor="hand2", padx=10, command=lambda: self.update_leave_status("Rejected"))
        btn_reject.pack(side="right", padx=5)

        cols_leave = ("Leave ID", "Emp ID", "Type", "Start Date", "End Date", "Days", "Reason", "Status", "Applied On")
        self.tree_leave = ttk.Treeview(leave_tab, columns=cols_leave, show="headings", height=12)
        self.tree_leave.pack(fill="both", expand=True, padx=10, pady=5)

        for c in cols_leave:
            self.tree_leave.heading(c, text=c)
            self.tree_leave.column(c, width=100, anchor="center")

        self.load_attendance()
        self.load_leaves()

    def load_attendance(self):
        for item in self.tree_att.get_children():
            self.tree_att.delete(item)
        rows = execute_query("""SELECT a.*, e.first_name, e.last_name FROM attendance a 
                                LEFT JOIN employees e ON a.emp_id = e.emp_id ORDER BY a.att_id DESC""", fetchall=True)
        if rows:
            for r in rows:
                name = f"{r.get('first_name', '')} {r.get('last_name', '')}".strip() or r["emp_id"]
                self.tree_att.insert("", "end", values=(r["att_id"], r["emp_id"], name, r["date"], r["status"], r["check_in"], r["check_out"]))

    def load_leaves(self):
        for item in self.tree_leave.get_children():
            self.tree_leave.delete(item)
        rows = execute_query("SELECT * FROM leaves ORDER BY leave_id DESC", fetchall=True)
        if rows:
            for r in rows:
                self.tree_leave.insert("", "end", values=(r["leave_id"], r["emp_id"], r["leave_type"], r["start_date"], r["end_date"], r["days"], r["reason"], r["status"], r["applied_on"]))

    def quick_punch(self):
        win = tk.Toplevel(self)
        win.title("Punch Attendance")
        win.geometry("350x250")
        win.configure(bg=self.theme["card_bg"])
        win.grab_set()

        tk.Label(win, text="Employee ID:", font=("Segoe UI", 10, "bold"), fg=self.theme["fg"], bg=self.theme["card_bg"]).pack(pady=(20, 5))
        ent_emp = tk.Entry(win, font=("Segoe UI", 11), bg=self.theme["entry_bg"], fg=self.theme["fg"])
        ent_emp.pack(fill="x", padx=30, pady=5)
        ent_emp.insert(0, self.user.get("employee_id", "EMP001"))

        def punch(status):
            eid = ent_emp.get().strip()
            today = datetime.date.today().strftime("%Y-%m-%d")
            now_time = datetime.datetime.now().strftime("%I:%M %p")

            execute_query("INSERT INTO attendance (emp_id, date, status, check_in, check_out) VALUES (%s, %s, %s, %s, %s)",
                          (eid, today, status, now_time, "06:00 PM"))
            win.destroy()
            self.load_attendance()
            messagebox.showinfo("Success", f"Attendance logged as {status} for {eid} at {now_time}")

        btn_p = tk.Button(win, text="Mark Present Now", bg=self.theme["success"], fg="white", font=("Segoe UI", 10, "bold"), bd=0, cursor="hand2", command=lambda: punch("Present"))
        btn_p.pack(fill="x", padx=30, pady=10)

        btn_l = tk.Button(win, text="Mark Late Entry", bg=self.theme["warning"], fg="white", font=("Segoe UI", 10, "bold"), bd=0, cursor="hand2", command=lambda: punch("Late"))
        btn_l.pack(fill="x", padx=30, pady=5)

    def apply_leave_dialog(self):
        win = tk.Toplevel(self)
        win.title("Leave Application")
        win.geometry("400x420")
        win.configure(bg=self.theme["card_bg"])

        fields = [("Emp ID:", "emp_id"), ("Leave Type:", "type"), ("Start Date (YYYY-MM-DD):", "start"), ("End Date (YYYY-MM-DD):", "end"), ("Reason:", "reason")]
        entries = {}

        for i, (lbl, key) in enumerate(fields):
            tk.Label(win, text=lbl, font=("Segoe UI", 10, "bold"), fg=self.theme["fg"], bg=self.theme["card_bg"]).grid(row=i, column=0, sticky="w", padx=20, pady=8)
            ent = tk.Entry(win, font=("Segoe UI", 10), bg=self.theme["entry_bg"], fg=self.theme["fg"])
            ent.grid(row=i, column=1, sticky="ew", padx=20, pady=8)
            entries[key] = ent

        entries["emp_id"].insert(0, self.user.get("employee_id", "EMP001"))
        entries["type"].insert(0, "Casual Leave")
        today = datetime.date.today().strftime("%Y-%m-%d")
        entries["start"].insert(0, today)
        entries["end"].insert(0, today)

        def save():
            eid = entries["emp_id"].get().strip()
            ltype = entries["type"].get().strip()
            sdate = entries["start"].get().strip()
            edate = entries["end"].get().strip()
            rsn = entries["reason"].get().strip()

            execute_query("INSERT INTO leaves (emp_id, leave_type, start_date, end_date, days, reason, status, applied_on) VALUES (%s, %s, %s, %s, %s, %s, 'Pending', %s)",
                          (eid, ltype, sdate, edate, 1, rsn, today))
            win.destroy()
            self.load_leaves()
            messagebox.showinfo("Submitted", "Leave request submitted for approval.")

        btn_sub = tk.Button(win, text="Submit Leave Request", bg=self.theme["accent"], fg="white", font=("Segoe UI", 11, "bold"), bd=0, cursor="hand2", command=save)
        btn_sub.grid(row=len(fields), column=0, columnspan=2, fill="x", padx=20, pady=20)

    def update_leave_status(self, new_status):
        selected = self.tree_leave.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a leave row first.")
            return
        lid = self.tree_leave.item(selected[0])["values"][0]
        execute_query("UPDATE leaves SET status = %s WHERE leave_id = %s", (new_status, lid))
        self.load_leaves()
        messagebox.showinfo("Updated", f"Leave #{lid} status changed to {new_status}")
