# floor_plan.py
# Feature: Interactive Office Floor Plan & Desk Booking

import tkinter as tk
from tkinter import messagebox
import datetime
import config
from database import execute_query

class FloorPlanView(tk.Frame):
    def __init__(self, parent, user):
        super().__init__(parent, bg=config.get_theme()["bg"])
        self.user = user
        self.theme = config.get_theme()
        
        self.emp = execute_query(
            "SELECT employee_id FROM users WHERE username = %s", 
            (self.user["username"],), fetchone=True
        )
        if self.emp: self.emp = self.emp["employee_id"]
        
        self.desks = {} # Will map desk_id to canvas rect item
        self.build_ui()
        self.load_bookings()

    def build_ui(self):
        # ── Top Bar ─────────────────────────────────────────────────────────────
        top_bar = tk.Frame(self, bg=self.theme["card_bg"])
        top_bar.pack(fill="x", padx=20, pady=20)
        
        tk.Label(top_bar, text="Interactive Floor Plan", 
                 font=("Segoe UI", 16, "bold"), 
                 fg=self.theme["fg"], bg=self.theme["card_bg"]).pack(side="left", padx=15, pady=15)
                 
        tk.Label(top_bar, text="Click on an available (green) desk to book it for today.", 
                 font=("Segoe UI", 10), 
                 fg=self.theme["fg_dim"], bg=self.theme["card_bg"]).pack(side="left", padx=20)
                 
        btn_refresh = tk.Button(top_bar, text="Refresh Map", font=("Segoe UI", 10),
                                bg=self.theme["sidebar_bg"], fg=self.theme["fg"], bd=0, 
                                cursor="hand2", padx=10, pady=5, command=self.load_bookings)
        btn_refresh.pack(side="right", padx=20)

        # ── Legend ──────────────────────────────────────────────────────────────
        legend = tk.Frame(self, bg=self.theme["bg"])
        legend.pack(fill="x", padx=20)
        
        def add_legend(color, text):
            f = tk.Frame(legend, bg=self.theme["bg"])
            f.pack(side="left", padx=(0, 20))
            tk.Canvas(f, width=16, height=16, bg=color, highlightthickness=0).pack(side="left")
            tk.Label(f, text=f" {text}", font=("Segoe UI", 9), fg=self.theme["fg"], bg=self.theme["bg"]).pack(side="left")
            
        add_legend(self.theme["success"], "Available")
        add_legend(self.theme["danger"], "Booked")
        add_legend(self.theme["info"], "Your Desk")
        add_legend(self.theme["card_bg"], "Amenities")

        # ── Canvas Area ─────────────────────────────────────────────────────────
        self.canvas = tk.Canvas(self, bg=self.theme["card_bg"], bd=1, relief="solid", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.draw_floor_plan()

    def draw_floor_plan(self):
        t = self.theme
        c = self.canvas
        
        # Draw Rooms/Walls
        c.create_rectangle(50, 50, 950, 500, outline=t["border"], width=3)
        
        # Meeting Room
        c.create_rectangle(50, 50, 300, 250, fill=t["entry_bg"], outline=t["border"], width=2)
        c.create_text(175, 150, text="Meeting Room A", font=("Segoe UI", 12, "bold"), fill=t["fg_dim"])
        
        # Break Room
        c.create_rectangle(700, 50, 950, 200, fill=t["entry_bg"], outline=t["border"], width=2)
        c.create_text(825, 125, text="Break Room / Pantry", font=("Segoe UI", 12, "bold"), fill=t["fg_dim"])
        
        # Desks - Engineering Block
        c.create_text(500, 70, text="Engineering Block", font=("Segoe UI", 11, "bold"), fill=t["fg_dim"])
        self.create_desk("Desk_A1", 400, 100)
        self.create_desk("Desk_A2", 500, 100)
        self.create_desk("Desk_A3", 600, 100)
        self.create_desk("Desk_A4", 400, 180)
        self.create_desk("Desk_A5", 500, 180)
        self.create_desk("Desk_A6", 600, 180)
        
        # Desks - Sales/HR Block
        c.create_text(300, 310, text="Sales & HR Block", font=("Segoe UI", 11, "bold"), fill=t["fg_dim"])
        self.create_desk("Desk_B1", 100, 350)
        self.create_desk("Desk_B2", 200, 350)
        self.create_desk("Desk_B3", 300, 350)
        self.create_desk("Desk_B4", 400, 350)
        self.create_desk("Desk_B5", 100, 430)
        self.create_desk("Desk_B6", 200, 430)
        self.create_desk("Desk_B7", 300, 430)
        self.create_desk("Desk_B8", 400, 430)
        
        # Executive Offices
        c.create_rectangle(600, 300, 750, 500, fill=t["entry_bg"], outline=t["border"], width=2)
        c.create_text(675, 400, text="CEO Office", font=("Segoe UI", 12, "bold"), fill=t["fg_dim"])
        
        c.create_rectangle(750, 300, 950, 500, fill=t["entry_bg"], outline=t["border"], width=2)
        c.create_text(850, 400, text="CTO Office", font=("Segoe UI", 12, "bold"), fill=t["fg_dim"])

    def create_desk(self, desk_id, x, y):
        rect = self.canvas.create_rectangle(x, y, x+60, y+40, fill=self.theme["success"], outline=self.theme["bg"], width=2)
        txt = self.canvas.create_text(x+30, y+20, text=desk_id.split('_')[1], font=("Segoe UI", 10, "bold"), fill="white")
        
        self.desks[desk_id] = rect
        
        # Bind click events
        self.canvas.tag_bind(rect, "<Button-1>", lambda e, d=desk_id: self.handle_desk_click(d))
        self.canvas.tag_bind(txt, "<Button-1>", lambda e, d=desk_id: self.handle_desk_click(d))
        
        # Hand cursors
        self.canvas.tag_bind(rect, "<Enter>", lambda e: self.canvas.config(cursor="hand2"))
        self.canvas.tag_bind(rect, "<Leave>", lambda e: self.canvas.config(cursor=""))
        self.canvas.tag_bind(txt, "<Enter>", lambda e: self.canvas.config(cursor="hand2"))
        self.canvas.tag_bind(txt, "<Leave>", lambda e: self.canvas.config(cursor=""))

    def load_bookings(self):
        today = datetime.date.today().strftime("%Y-%m-%d")
        bookings = execute_query("SELECT desk_id, emp_id FROM desk_bookings WHERE date=%s AND status='Booked'", (today,), fetchall=True)
        
        booked_map = {b["desk_id"]: b["emp_id"] for b in (bookings or [])}
        
        for desk_id, rect_id in self.desks.items():
            if desk_id in booked_map:
                if booked_map[desk_id] == self.emp:
                    self.canvas.itemconfig(rect_id, fill=self.theme["info"])
                else:
                    self.canvas.itemconfig(rect_id, fill=self.theme["danger"])
            else:
                self.canvas.itemconfig(rect_id, fill=self.theme["success"])

    def handle_desk_click(self, desk_id):
        if not self.emp:
            messagebox.showerror("Error", "Only registered employees can book desks.")
            return
            
        today = datetime.date.today().strftime("%Y-%m-%d")
        
        # Check if already booked
        booking = execute_query("SELECT emp_id FROM desk_bookings WHERE desk_id=%s AND date=%s AND status='Booked'", (desk_id, today), fetchone=True)
        
        if booking:
            if booking["emp_id"] == self.emp:
                if messagebox.askyesno("Cancel Booking", f"You have booked {desk_id} for today. Cancel booking?"):
                    execute_query("DELETE FROM desk_bookings WHERE desk_id=%s AND date=%s", (desk_id, today))
                    self.load_bookings()
                    messagebox.showinfo("Cancelled", f"Booking for {desk_id} cancelled.")
            else:
                # Get name
                e = execute_query("SELECT first_name, last_name FROM employees WHERE emp_id=%s", (booking["emp_id"],), fetchone=True)
                name = f"{e['first_name']} {e['last_name']}" if e else booking["emp_id"]
                messagebox.showinfo("Unavailable", f"{desk_id} is already booked by {name} today.")
        else:
            # Check if user already has a desk
            my_booking = execute_query("SELECT desk_id FROM desk_bookings WHERE emp_id=%s AND date=%s AND status='Booked'", (self.emp, today), fetchone=True)
            if my_booking:
                messagebox.showwarning("Limit Reached", f"You have already booked {my_booking['desk_id']} today.")
                return
                
            if messagebox.askyesno("Confirm Booking", f"Book {desk_id} for today?"):
                execute_query("INSERT INTO desk_bookings (emp_id, desk_id, date, status) VALUES (%s, %s, %s, 'Booked')", (self.emp, desk_id, today))
                
                user_name = self.user.get("username", "Unknown")
                now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                execute_query("INSERT INTO audit_logs (username, action, timestamp) VALUES (%s, %s, %s)", 
                              (user_name, f"Booked {desk_id}", now_str))
                              
                self.load_bookings()
                messagebox.showinfo("Success", f"{desk_id} booked successfully for today!")
