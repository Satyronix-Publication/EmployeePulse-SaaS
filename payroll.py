# payroll.py
# Feature 3: Automated Payroll Processing & Pay Slip Generator

import tkinter as tk
from tkinter import ttk, messagebox
import config
from database import execute_query

class PayrollView(tk.Frame):
    def __init__(self, parent, user):
        super().__init__(parent, bg=config.get_theme()["bg"])
        self.user = user
        self.theme = config.get_theme()
        self.build_ui()
        self.load_payroll()

    def build_ui(self):
        top_bar = tk.Frame(self, bg=self.theme["card_bg"], pady=10)
        top_bar.pack(fill="x", padx=15, pady=10)

        lbl_title = tk.Label(top_bar, text="💵 Payroll & Salary Management", font=("Segoe UI", 14, "bold"), fg=self.theme["fg"], bg=self.theme["card_bg"])
        lbl_title.pack(side="left", padx=10)

        btn_run_payroll = tk.Button(top_bar, text="⚡ Process Monthly Payroll", font=("Segoe UI", 10, "bold"), bg=self.theme["accent"], fg="white", bd=0, cursor="hand2", padx=10, command=self.open_payroll_dialog)
        btn_run_payroll.pack(side="right", padx=10)

        # Table
        table_frame = tk.Frame(self, bg=self.theme["card_bg"])
        table_frame.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        cols = ("Pay ID", "Emp ID", "Employee Name", "Month", "Year", "Base Salary", "HRA", "DA", "PF Deduct", "Tax Deduct", "Net Salary", "Status")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=15)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)

        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor="center")

        btn_frame = tk.Frame(self, bg=self.theme["bg"])
        btn_frame.pack(fill="x", padx=15, pady=5)

        btn_payslip = tk.Button(btn_frame, text="📄 Generate Pay Slip", font=("Segoe UI", 10, "bold"), bg=self.theme["info"], fg="white", bd=0, cursor="hand2", padx=10, command=self.generate_payslip)
        btn_payslip.pack(side="left", padx=5)

    def load_payroll(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        rows = execute_query("""
            SELECT p.*, e.first_name, e.last_name 
            FROM payroll p 
            LEFT JOIN employees e ON p.emp_id = e.emp_id 
            ORDER BY p.pay_id DESC
        """, fetchall=True)

        if rows:
            for r in rows:
                name = f"{r.get('first_name', '')} {r.get('last_name', '')}".strip() or r["emp_id"]
                self.tree.insert("", "end", values=(
                    r["pay_id"], r["emp_id"], name, r["month"], r["year"],
                    f"${r['base_salary']:,.2f}", f"${r['hra']:,.2f}", f"${r['da']:,.2f}",
                    f"${r['pf_deduction']:,.2f}", f"${r['tax_deduction']:,.2f}", f"${r['net_salary']:,.2f}", r["status"]
                ))

    def open_payroll_dialog(self):
        win = tk.Toplevel(self)
        win.title("Process Salary Run")
        win.geometry("420x450")
        win.configure(bg=self.theme["card_bg"])
        win.grab_set()

        # Employee Dropdown
        tk.Label(win, text="Select Employee:", font=("Segoe UI", 10, "bold"), fg=self.theme["fg"], bg=self.theme["card_bg"]).pack(anchor="w", padx=20, pady=(15, 2))
        emps = execute_query("SELECT emp_id, first_name, last_name, salary FROM employees", fetchall=True) or []
        emp_map = {f"{e['emp_id']} - {e['first_name']} {e['last_name']} (${e['salary']:,.0f})": e for e in emps}

        cmb_emp = ttk.Combobox(win, values=list(emp_map.keys()), state="readonly", font=("Segoe UI", 10))
        cmb_emp.pack(fill="x", padx=20, pady=(0, 10))
        if emps:
            cmb_emp.current(0)

        # Month and Year
        tk.Label(win, text="Payroll Month:", font=("Segoe UI", 10, "bold"), fg=self.theme["fg"], bg=self.theme["card_bg"]).pack(anchor="w", padx=20, pady=(5, 2))
        cmb_month = ttk.Combobox(win, values=["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"], state="readonly")
        cmb_month.pack(fill="x", padx=20, pady=(0, 10))
        cmb_month.current(8) # September

        tk.Label(win, text="Payroll Year:", font=("Segoe UI", 10, "bold"), fg=self.theme["fg"], bg=self.theme["card_bg"]).pack(anchor="w", padx=20, pady=(5, 2))
        ent_year = tk.Entry(win, font=("Segoe UI", 10), bg=self.theme["entry_bg"], fg=self.theme["fg"])
        ent_year.pack(fill="x", padx=20, pady=(0, 15))
        ent_year.insert(0, "2026")

        def calculate_and_save():
            emp_data = emp_map.get(cmb_emp.get())
            if not emp_data:
                messagebox.showwarning("Warning", "Select a valid employee.")
                return
            base = float(emp_data["salary"])
            hra = base * 0.20       # 20% House Rent Allowance
            da = base * 0.10        # 10% Dearness Allowance
            pf = base * 0.12        # 12% Provident Fund
            tax = base * 0.15       # 15% Income Tax
            net = (base + hra + da) - (pf + tax)

            execute_query("""INSERT INTO payroll (emp_id, month, year, base_salary, hra, da, pf_deduction, tax_deduction, net_salary, status)
                             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'Processed')""",
                          (emp_data["emp_id"], cmb_month.get(), int(ent_year.get()), base, hra, da, pf, tax, net))

            win.destroy()
            self.load_payroll()
            messagebox.showinfo("Payroll Processed", f"Net Pay calculated for {emp_data['first_name']}: ${net:,.2f}")

        btn_calc = tk.Button(win, text="Calculate & Process Net Salary", font=("Segoe UI", 11, "bold"), bg=self.theme["accent"], fg="white", bd=0, cursor="hand2", command=calculate_and_save)
        btn_calc.pack(fill="x", padx=20, pady=20, ipady=5)

    def generate_payslip(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Select a payroll row to generate pay slip.")
            return

        vals = self.tree.item(selected[0])["values"]

        win = tk.Toplevel(self)
        win.title(f"Pay Slip - {vals[1]} ({vals[3]} {vals[4]})")
        win.geometry("450x520")
        win.configure(bg=self.theme["card_bg"])

        lbl_hdr = tk.Label(win, text="🏢 EmployeePulse SaaS Pay Slip", font=("Segoe UI", 16, "bold"), fg=self.theme["accent"], bg=self.theme["card_bg"])
        lbl_hdr.pack(pady=15)

        slip_txt = f"""
        ====================================================
        EMPLOYEE PAYSLIP STATEMENT
        ====================================================
        Employee ID  : {vals[1]}
        Employee Name: {vals[2]}
        Pay Period   : {vals[3]} {vals[4]}
        Status       : {vals[11]}
        ----------------------------------------------------
        EARNINGS:
          Base Salary : {vals[5]}
          HRA (20%)   : {vals[6]}
          DA  (10%)   : {vals[7]}

        DEDUCTIONS:
          PF (12%)    : {vals[8]}
          Income Tax  : {vals[9]}
        ----------------------------------------------------
        TOTAL NET PAYABLE: {vals[10]}
        ====================================================
        This is a computer-generated statement.
        """
        txt_box = tk.Text(win, font=("Courier New", 10), bg=self.theme["entry_bg"], fg=self.theme["fg"], bd=1, relief="solid")
        txt_box.pack(fill="both", expand=True, padx=20, pady=10)
        txt_box.insert("1.0", slip_txt)
        txt_box.configure(state="disabled")
