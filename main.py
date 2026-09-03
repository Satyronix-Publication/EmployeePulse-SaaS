# main.py
# EmployeePulse SaaS — CBSE Class 12 Project Entry Point
# Flow: Welcome → Login (has Sign In + Create Account tabs) → Dashboard

"""
====================================================
   EMPLOYEEPULSE SAAS - WORKFORCE OPERATING SYSTEM
   CBSE Class 12 Python Computer Science Project
====================================================
   Default Login Credentials:
   - Admin    : admin      / admin123
   - HR       : hr_manager / hr123
   - Employee : emp001     / emp123
====================================================
"""

import tkinter as tk
import config
from database import init_database
from welcome import WelcomeWindow
from login import LoginWindow
from dashboard import DashboardWindow


class ApplicationController:
    def __init__(self):
        print("=" * 55)
        print("   EMPLOYEEPULSE SAAS - Initializing Engine...")
        print("=" * 55)
        init_database()

        self.root = tk.Tk()
        self.root.title(config.APP_NAME)
        config.apply_ttk_styles(self.root)

        # Always launch the welcome screen first
        self.show_welcome()

    def clear_screen(self):
        """Destroys all widgets in the root window."""
        for widget in self.root.winfo_children():
            widget.destroy()

    # ── Screen Controllers ────────────────────────────────────────────────────

    def show_welcome(self):
        """Hero welcome / splash screen."""
        self.clear_screen()
        WelcomeWindow(
            self.root,
            on_navigate_login=self.show_login,
            on_navigate_signup=lambda: self.show_login(default_tab="signup"),
            on_login_success=self.show_dashboard
        )

    def show_login(self, default_tab="signin"):
        """Combined Sign In + Create Account screen."""
        self.clear_screen()
        win = LoginWindow(
            self.root,
            on_login_success=self.show_dashboard,
            on_navigate_welcome=self.show_welcome
        )
        # Switch to signup tab if user clicked "Get Started"
        if default_tab == "signup":
            win._switch_mode("signup")

    def show_dashboard(self, user):
        """Main enterprise SaaS dashboard (after login)."""
        self.clear_screen()
        DashboardWindow(
            self.root,
            user,
            on_logout=self.show_welcome
        )

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = ApplicationController()
    app.run()
