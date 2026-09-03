# ai_chat.py
# Feature: Pulse AI HR Assistant (Chatbot Simulation)

import tkinter as tk
from tkinter import ttk, messagebox
import config
from database import execute_query
import datetime
import random

class AIChatView(tk.Frame):
    def __init__(self, parent, user):
        super().__init__(parent, bg=config.get_theme()["bg"])
        self.user = user
        self.theme = config.get_theme()
        
        # Get employee data if applicable
        self.emp = execute_query(
            "SELECT * FROM employees e JOIN users u ON e.emp_id = u.employee_id WHERE u.username = %s",
            (self.user["username"],), fetchone=True
        )
        
        self.build_ui()
        self.add_message("Pulse AI", f"Hello {self.user['username']}! I am Pulse AI, your Enterprise HR Assistant. How can I help you today?\n\nYou can ask me things like:\n- How many leaves do I have left?\n- What is my current salary?\n- Who is the HOD of Engineering?", "ai")

    def build_ui(self):
        # ── Header ──────────────────────────────────────────────────────────────
        top_bar = tk.Frame(self, bg=self.theme["card_bg"], bd=1, relief="solid")
        top_bar.pack(fill="x", padx=20, pady=(20, 10))
        
        config.logo_canvas(top_bar, size=40, bg=self.theme["card_bg"]).pack(side="left", padx=15, pady=10)
        
        tk.Label(top_bar, text="Pulse AI Assistant", 
                 font=("Segoe UI", 16, "bold"), 
                 fg=self.theme["accent"], bg=self.theme["card_bg"]).pack(side="left")
                 
        tk.Label(top_bar, text="Online", 
                 font=("Segoe UI", 10, "bold"), 
                 fg=self.theme["success"], bg=self.theme["card_bg"]).pack(side="right", padx=20)

        # ── Chat Area ───────────────────────────────────────────────────────────
        chat_frame = tk.Frame(self, bg=self.theme["card_bg"], bd=1, relief="solid")
        chat_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.txt_chat = tk.Text(chat_frame, font=("Segoe UI", 11), bg=self.theme["bg"], 
                                fg=self.theme["fg"], bd=0, highlightthickness=0, 
                                state="disabled", padx=15, pady=15, wrap="word")
        
        scrollbar = ttk.Scrollbar(chat_frame, orient="vertical", command=self.txt_chat.yview)
        self.txt_chat.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y")
        self.txt_chat.pack(side="left", fill="both", expand=True)
        
        # Tags for styling text
        self.txt_chat.tag_configure("ai_name", font=("Segoe UI", 10, "bold"), foreground=self.theme["accent"])
        self.txt_chat.tag_configure("user_name", font=("Segoe UI", 10, "bold"), foreground=self.theme["success"])
        self.txt_chat.tag_configure("msg", font=("Segoe UI", 11), foreground=self.theme["fg"])
        self.txt_chat.tag_configure("time", font=("Segoe UI", 8), foreground=self.theme["fg_dim"])
        
        # ── Input Area ──────────────────────────────────────────────────────────
        input_frame = tk.Frame(self, bg=self.theme["bg"])
        input_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        self.ent_msg = tk.Entry(input_frame, font=("Segoe UI", 12), bg=self.theme["entry_bg"], 
                                fg=self.theme["fg"], insertbackground=self.theme["fg"], 
                                bd=1, relief="solid", highlightthickness=1, 
                                highlightbackground=self.theme["border"], highlightcolor=self.theme["accent"])
        self.ent_msg.pack(side="left", fill="x", expand=True, ipady=12)
        self.ent_msg.bind("<Return>", lambda e: self.send_message())
        
        btn_send = tk.Button(input_frame, text="Send →", font=("Segoe UI", 11, "bold"),
                             bg=self.theme["accent"], fg="white", bd=0, cursor="hand2",
                             activebackground=self.theme["accent_hover"], activeforeground="white",
                             command=self.send_message, padx=20)
        btn_send.pack(side="right", padx=(10, 0), fill="y")

    def add_message(self, sender, text, tag_type):
        self.txt_chat.configure(state="normal")
        
        time_str = datetime.datetime.now().strftime("%I:%M %p")
        name_tag = "ai_name" if tag_type == "ai" else "user_name"
        
        self.txt_chat.insert("end", f"{sender}  ", name_tag)
        self.txt_chat.insert("end", f"{time_str}\n", "time")
        self.txt_chat.insert("end", f"{text}\n\n", "msg")
        
        self.txt_chat.configure(state="disabled")
        self.txt_chat.see("end")

    def send_message(self):
        msg = self.ent_msg.get().strip()
        if not msg: return
        
        self.ent_msg.delete(0, "end")
        self.add_message("You", msg, "user")
        
        # Simulate AI thinking delay
        self.after(500, lambda: self.process_ai_response(msg.lower()))

    def process_ai_response(self, query):
        response = ""
        
        # Keyword matching logic for simulated AI
        if "leave" in query or "leaves" in query:
            if self.emp:
                leaves = execute_query("SELECT SUM(days) as used FROM leaves WHERE emp_id=%s AND status='Approved'", (self.emp["emp_id"],), fetchone=True)
                used = leaves.get("used") if leaves and leaves.get("used") else 0
                total_allowed = 24 # Standard policy
                response = f"According to your records, you have used {used} leave days this year. You have {total_allowed - used} days remaining.\nWould you like to apply for a leave through the 'Attendance & Leaves' tab?"
            else:
                response = "I can only check leave balances for registered employees. You are currently logged in as an Admin/System user."
                
        elif "salary" in query or "pay" in query:
            if self.emp:
                response = f"Your current base salary is ${self.emp['salary']:,.2f}.\nFor detailed payslips, please check the 'Payroll & Salary' tab."
            else:
                response = "I cannot find your salary information."
                
        elif "hod" in query or "head" in query:
            if "engineering" in query:
                dept = execute_query("SELECT hod FROM departments WHERE dept_name LIKE '%Engineering%'", fetchone=True)
                response = f"The Head of Engineering is {dept['hod']}." if dept else "I couldn't find the HOD for Engineering."
            elif "hr" in query or "human resource" in query:
                dept = execute_query("SELECT hod FROM departments WHERE dept_name LIKE '%Human%'", fetchone=True)
                response = f"The Head of HR is {dept['hod']}." if dept else "I couldn't find the HOD for HR."
            else:
                depts = execute_query("SELECT dept_name, hod FROM departments", fetchall=True)
                if depts:
                    response = "Here are the Department Heads:\n"
                    for d in depts: response += f"- {d['dept_name']}: {d['hod']}\n"
                else:
                    response = "I don't have department head information at this time."
                    
        elif "employee" in query and ("count" in query or "how many" in query):
            cnt = execute_query("SELECT COUNT(*) as c FROM employees WHERE status='Active'", fetchone=True)
            if cnt:
                response = f"We currently have {cnt['c']} active employees on the platform."
            else:
                response = "I am unable to retrieve the employee count right now."
                
        elif "hello" in query or "hi" in query:
            response = "Hello! I am Pulse AI. How can I assist you with your HR needs today?"
            
        elif "thank" in query:
            response = "You're very welcome! Let me know if you need anything else."
            
        elif "joke" in query:
            jokes = [
                "Why do programmers prefer dark mode?\nBecause light attracts bugs!",
                "Why did the employee get fired from the calendar factory?\nHe took a couple of days off.",
                "I asked the corporate network for a raise.\nIt gave me a 'Permission Denied' error."
            ]
            response = random.choice(jokes)
            
        else:
            response = "I'm sorry, I don't quite understand that yet. I am continuously learning. You can ask me about your leaves, salary, department heads, or active employee counts."
            
        self.add_message("Pulse AI", response, "ai")
