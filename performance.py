# performance.py
# Feature 5: Employee Performance Review & KPI Rating System

import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import config
from database import execute_query

class PerformanceView(tk.Frame):
    def __init__(self, parent, user):
        super().__init__(parent, bg=config.get_theme()["bg"])
        self.user = user
        self.theme = config.get_theme()
        self.build_ui()
        self.load_performance()

    def build_ui(self):
        top_bar = tk.Frame(self, bg=self.theme["card_bg"], pady=10)
        top_bar.pack(fill="x", padx=15, pady=10)

        lbl_title = tk.Label(top_bar, text="⭐ Performance & KPI Appraisals", font=("Segoe UI", 14, "bold"), fg=self.theme["fg"], bg=self.theme["card_bg"])
        lbl_title.pack(side="left", padx=10)

        btn_add = tk.Button(top_bar, text="+ Submit Performance Review", font=("Segoe UI", 10, "bold"), bg=self.theme["accent"], fg="white", bd=0, cursor="hand2", padx=10, command=self.open_review_dialog)
        btn_add.pack(side="right", padx=10)

        table_frame = tk.Frame(self, bg=self.theme["card_bg"])
        table_frame.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        cols = ("Review ID", "Emp ID", "Employee Name", "Star Rating (1-5)", "KPI Score (%)", "Reviewer Feedback", "Review Date")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=15)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)

        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="center")

        self.tree.column("Reviewer Feedback", width=250)

    def load_performance(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        rows = execute_query("""SELECT p.*, e.first_name, e.last_name FROM performance p 
                                LEFT JOIN employees e ON p.emp_id = e.emp_id ORDER BY p.review_id DESC""", fetchall=True)

        if rows:
            for r in rows:
                name = f"{r.get('first_name', '')} {r.get('last_name', '')}".strip() or r["emp_id"]
                rating_stars = "★" * int(r["rating"]) + "☆" * (5 - int(r["rating"])) + f" ({r['rating']})"
                self.tree.insert("", "end", values=(
                    r["review_id"], r["emp_id"], name, rating_stars, f"{r['kpi_score']}%", r["reviewer_feedback"], r["review_date"]
                ))

    def open_review_dialog(self):
        win = tk.Toplevel(self)
        win.title("Submit Employee Performance Appraisal")
        win.geometry("420x450")
        win.configure(bg=self.theme["card_bg"])
        win.grab_set()

        tk.Label(win, text="Select Employee:", font=("Segoe UI", 10, "bold"), fg=self.theme["fg"], bg=self.theme["card_bg"]).pack(anchor="w", padx=20, pady=(15, 2))
        emps = execute_query("SELECT emp_id, first_name, last_name FROM employees", fetchall=True) or []
        emp_map = {f"{e['emp_id']} - {e['first_name']} {e['last_name']}": e["emp_id"] for e in emps}

        cmb_emp = ttk.Combobox(win, values=list(emp_map.keys()), state="readonly", font=("Segoe UI", 10))
        cmb_emp.pack(fill="x", padx=20, pady=(0, 10))
        if emps:
            cmb_emp.current(0)

        tk.Label(win, text="Rating Score (1.0 to 5.0):", font=("Segoe UI", 10, "bold"), fg=self.theme["fg"], bg=self.theme["card_bg"]).pack(anchor="w", padx=20, pady=(5, 2))
        ent_rating = tk.Entry(win, font=("Segoe UI", 10), bg=self.theme["entry_bg"], fg=self.theme["fg"])
        ent_rating.pack(fill="x", padx=20, pady=(0, 10))
        ent_rating.insert(0, "4.8")

        tk.Label(win, text="KPI Goal Completion (%):", font=("Segoe UI", 10, "bold"), fg=self.theme["fg"], bg=self.theme["card_bg"]).pack(anchor="w", padx=20, pady=(5, 2))
        ent_kpi = tk.Entry(win, font=("Segoe UI", 10), bg=self.theme["entry_bg"], fg=self.theme["fg"])
        ent_kpi.pack(fill="x", padx=20, pady=(0, 10))
        ent_kpi.insert(0, "95")

        tk.Label(win, text="Reviewer Feedback Comments:", font=("Segoe UI", 10, "bold"), fg=self.theme["fg"], bg=self.theme["card_bg"]).pack(anchor="w", padx=20, pady=(5, 2))
        txt_feedback = tk.Text(win, font=("Segoe UI", 10), height=4, bg=self.theme["entry_bg"], fg=self.theme["fg"])
        txt_feedback.pack(fill="x", padx=20, pady=(0, 15))
        txt_feedback.insert("1.0", "Demonstrated exemplary leadership and codebase quality.")

        def save():
            eid = emp_map.get(cmb_emp.get())
            try:
                rate = float(ent_rating.get().strip())
                kpi = float(ent_kpi.get().strip())
            except ValueError:
                messagebox.showerror("Error", "Invalid numeric rating or KPI.")
                return

            fb = txt_feedback.get("1.0", "end-1c").strip()
            today = datetime.date.today().strftime("%Y-%m-%d")

            execute_query("INSERT INTO performance (emp_id, rating, kpi_score, reviewer_feedback, review_date) VALUES (%s, %s, %s, %s, %s)",
                          (eid, rate, kpi, fb, today))

            win.destroy()
            self.load_performance()
            messagebox.showinfo("Success", "Performance appraisal recorded.")

        btn_save = tk.Button(win, text="Save Appraisal", font=("Segoe UI", 11, "bold"), bg=self.theme["accent"], fg="white", bd=0, cursor="hand2", command=save)
        btn_save.pack(fill="x", padx=20, pady=10)
