# kudos.py
# Feature: Gamified Kudos & Rewards Leaderboard

import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import config
from database import execute_query

class KudosView(tk.Frame):
    def __init__(self, parent, user):
        super().__init__(parent, bg=config.get_theme()["bg"])
        self.user = user
        self.theme = config.get_theme()
        
        # Get the current employee ID for the logged in user
        self.emp_id = execute_query(
            "SELECT employee_id FROM users WHERE username = %s", 
            (self.user["username"],), fetchone=True
        )
        if self.emp_id:
            self.emp_id = self.emp_id["employee_id"]
            
        self.build_ui()
        self.load_leaderboard()

    def build_ui(self):
        # ── Top Bar ─────────────────────────────────────────────────────────────
        top_bar = tk.Frame(self, bg=self.theme["card_bg"])
        top_bar.pack(fill="x", padx=20, pady=20)
        
        tk.Label(top_bar, text="Kudos & Rewards Leaderboard", 
                 font=("Segoe UI", 16, "bold"), 
                 fg=self.theme["fg"], bg=self.theme["card_bg"]).pack(side="left", padx=15, pady=15)
                 
        btn_give = tk.Button(top_bar, text="Give Kudos", 
                             font=("Segoe UI", 11, "bold"),
                             bg=self.theme["accent"], fg="white", bd=0, 
                             cursor="hand2", padx=20, pady=8,
                             activebackground=self.theme["accent_hover"],
                             activeforeground="white",
                             command=self.open_give_kudos_dialog)
        btn_give.pack(side="right", padx=20)

        # ── Main Content Split ──────────────────────────────────────────────────
        main_content = tk.Frame(self, bg=self.theme["bg"])
        main_content.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # LEFT: Leaderboard
        left_frame = tk.Frame(main_content, bg=self.theme["card_bg"], bd=1, relief="solid")
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        tk.Label(left_frame, text="Top Performers This Month", 
                 font=("Segoe UI", 12, "bold"), 
                 fg=self.theme["accent"], bg=self.theme["card_bg"]).pack(anchor="w", padx=20, pady=15)
                 
        cols = ("Rank", "Employee", "Department", "Total Points")
        self.tree = ttk.Treeview(left_frame, columns=cols, show="headings", height=15)
        
        for col in cols:
            self.tree.heading(col, text=col)
            
        self.tree.column("Rank", width=60, anchor="center")
        self.tree.column("Employee", width=200)
        self.tree.column("Department", width=150)
        self.tree.column("Total Points", width=100, anchor="center")
        
        self.tree.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # RIGHT: Recent Kudos Feed
        right_frame = tk.Frame(main_content, bg=self.theme["card_bg"], bd=1, relief="solid", width=350)
        right_frame.pack(side="right", fill="y")
        right_frame.pack_propagate(False)
        
        tk.Label(right_frame, text="Recent Recognitions", 
                 font=("Segoe UI", 12, "bold"), 
                 fg=self.theme["fg"], bg=self.theme["card_bg"]).pack(anchor="w", padx=20, pady=15)
                 
        # Scrollable feed canvas
        feed_canvas = tk.Canvas(right_frame, bg=self.theme["card_bg"], bd=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=feed_canvas.yview)
        
        self.feed_frame = tk.Frame(feed_canvas, bg=self.theme["card_bg"])
        self.feed_frame.bind("<Configure>", lambda e: feed_canvas.configure(scrollregion=feed_canvas.bbox("all")))
        
        feed_canvas.create_window((0, 0), window=self.feed_frame, anchor="nw", width=330)
        feed_canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y")
        feed_canvas.pack(side="left", fill="both", expand=True, padx=(20, 0), pady=(0, 20))

    def load_leaderboard(self):
        # Clear existing
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for widget in self.feed_frame.winfo_children():
            widget.destroy()
            
        # Load Leaderboard Data
        query = """
            SELECT e.first_name, e.last_name, d.dept_name, SUM(k.points) as total_points
            FROM kudos k
            JOIN employees e ON k.receiver_id = e.emp_id
            LEFT JOIN departments d ON e.dept_id = d.dept_id
            GROUP BY k.receiver_id
            ORDER BY total_points DESC
        """
        rows = execute_query(query, fetchall=True)
        
        if rows:
            for i, r in enumerate(rows):
                rank = i + 1
                name = f"{r['first_name']} {r['last_name']}"
                dept = r.get("dept_name") or "N/A"
                pts  = r.get("total_points", 0)
                
                # Add medal to top 3
                if rank == 1: rank_str = "1 (Gold)"
                elif rank == 2: rank_str = "2 (Silver)"
                elif rank == 3: rank_str = "3 (Bronze)"
                else: rank_str = str(rank)
                
                self.tree.insert("", "end", values=(rank_str, name, dept, pts))
                
        # Load Feed Data
        feed_query = """
            SELECT s.first_name as s_first, s.last_name as s_last,
                   r.first_name as r_first, r.last_name as r_last,
                   k.message, k.points, k.date
            FROM kudos k
            JOIN employees s ON k.sender_id = s.emp_id
            JOIN employees r ON k.receiver_id = r.emp_id
            ORDER BY k.kudo_id DESC
            LIMIT 10
        """
        feed_rows = execute_query(feed_query, fetchall=True)
        
        if feed_rows:
            for r in feed_rows:
                f = tk.Frame(self.feed_frame, bg=self.theme["entry_bg"], bd=1, relief="solid")
                f.pack(fill="x", pady=5)
                
                sender = f"{r['s_first']} {r['s_last']}"
                receiver = f"{r['r_first']} {r['r_last']}"
                
                header = tk.Frame(f, bg=self.theme["entry_bg"])
                header.pack(fill="x", padx=10, pady=(10, 5))
                
                tk.Label(header, text=f"{sender} recognized {receiver}", 
                         font=("Segoe UI", 9, "bold"), fg=self.theme["fg"], bg=self.theme["entry_bg"]).pack(side="left")
                tk.Label(header, text=f"+{r['points']} pts", 
                         font=("Segoe UI", 9, "bold"), fg=self.theme["success"], bg=self.theme["entry_bg"]).pack(side="right")
                         
                msg = tk.Message(f, text=r['message'], width=280,
                                 font=("Segoe UI", 9), fg=self.theme["fg_dim"], bg=self.theme["entry_bg"])
                msg.pack(anchor="w", padx=10, pady=(0, 10))
        else:
            tk.Label(self.feed_frame, text="No kudos given yet.", 
                     font=("Segoe UI", 10), fg=self.theme["fg_dim"], bg=self.theme["card_bg"]).pack(pady=20)

    def open_give_kudos_dialog(self):
        if not self.emp_id:
            messagebox.showerror("Error", "You must be logged in as an employee to give Kudos.")
            return
            
        win = tk.Toplevel(self)
        win.title("Give Kudos")
        win.geometry("450x400")
        win.configure(bg=self.theme["card_bg"])
        win.grab_set()
        
        tk.Label(win, text="Recognize a Colleague", 
                 font=("Segoe UI", 14, "bold"), 
                 fg=self.theme["fg"], bg=self.theme["card_bg"]).pack(anchor="w", padx=20, pady=(20, 10))
                 
        tk.Label(win, text="Select Employee:", font=("Segoe UI", 10, "bold"), 
                 fg=self.theme["fg"], bg=self.theme["card_bg"]).pack(anchor="w", padx=20, pady=(10, 2))
                 
        emps = execute_query("SELECT emp_id, first_name, last_name FROM employees WHERE status='Active' AND emp_id != %s", 
                             (self.emp_id,), fetchall=True)
                             
        if not emps:
            tk.Label(win, text="No other active employees found.", fg=self.theme["danger"], bg=self.theme["card_bg"]).pack()
            return
            
        emp_map = {f"{e['first_name']} {e['last_name']} ({e['emp_id']})": e["emp_id"] for e in emps}
        cmb_emp = ttk.Combobox(win, values=list(emp_map.keys()), state="readonly", font=("Segoe UI", 10))
        cmb_emp.pack(fill="x", padx=20, ipady=4)
        if emp_map:
            cmb_emp.current(0)
            
        tk.Label(win, text="Points to Award:", font=("Segoe UI", 10, "bold"), 
                 fg=self.theme["fg"], bg=self.theme["card_bg"]).pack(anchor="w", padx=20, pady=(15, 2))
        cmb_pts = ttk.Combobox(win, values=["10", "20", "50", "100"], state="readonly", font=("Segoe UI", 10))
        cmb_pts.pack(fill="x", padx=20, ipady=4)
        cmb_pts.current(0)
        
        tk.Label(win, text="Message of Recognition:", font=("Segoe UI", 10, "bold"), 
                 fg=self.theme["fg"], bg=self.theme["card_bg"]).pack(anchor="w", padx=20, pady=(15, 2))
        txt_msg = tk.Text(win, font=("Segoe UI", 10), bg=self.theme["entry_bg"], fg=self.theme["fg"], 
                          insertbackground=self.theme["fg"], height=4, bd=0, highlightthickness=1, highlightbackground=self.theme["border"])
        txt_msg.pack(fill="x", padx=20)
        
        def save():
            receiver = emp_map.get(cmb_emp.get())
            points = int(cmb_pts.get())
            msg = txt_msg.get("1.0", tk.END).strip()
            
            if not msg:
                messagebox.showwarning("Validation", "Please write a message.")
                return
                
            today = datetime.date.today().strftime("%Y-%m-%d")
            execute_query(
                "INSERT INTO kudos (sender_id, receiver_id, message, points, date) VALUES (%s, %s, %s, %s, %s)",
                (self.emp_id, receiver, msg, points, today)
            )
            
            # Log action
            user_name = self.user.get("username", "Unknown")
            now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            execute_query(
                "INSERT INTO audit_logs (username, action, timestamp) VALUES (%s, %s, %s)", 
                (user_name, f"Awarded {points} kudos to {receiver}", now_str)
            )
            
            win.destroy()
            self.load_leaderboard()
            messagebox.showinfo("Success", "Kudos sent successfully!")
            
        tk.Button(win, text="Send Kudos", font=("Segoe UI", 11, "bold"),
                  bg=self.theme["accent"], fg="white", bd=0, cursor="hand2", 
                  command=save).pack(fill="x", padx=20, pady=25, ipady=5)
