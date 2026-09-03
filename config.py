# config.py
# EmployeePulse SaaS - Central Configuration, Theme Engine & Shared UI Utilities

import tkinter as tk
from tkinter import ttk
import os

APP_NAME    = "EmployeePulse SaaS"
APP_VERSION = "3.0 (CBSE Class 12 CS Edition)"
LOGO_FILE   = "employee_management_system_logo.png"   # filename in project dir

MYSQL_HOST     = "localhost"
MYSQL_USER     = "root"
MYSQL_PASSWORD = ""
MYSQL_DB       = "employee_saas_db"
SQLITE_DB      = "employee_saas.db"

# ── Colour Palettes ───────────────────────────────────────────────────────────
THEMES = {
    "dark": {
        "bg":               "#080c14",
        "sidebar_bg":       "#0f172a",
        "card_bg":          "#111827",
        "card_border":      "#1e293b",
        "accent":           "#06b6d4",
        "accent_secondary": "#6366f1",
        "accent_hover":     "#0891b2",
        "fg":               "#f8fafc",
        "fg_dim":           "#94a3b8",
        "success":          "#10b981",
        "danger":           "#f43f5e",
        "warning":          "#f59e0b",
        "info":             "#3b82f6",
        "row_even":         "#111827",
        "row_odd":          "#0b1120",
        "entry_bg":         "#1e293b",
        "tree_bg":          "#0f172a",
        "tree_head":        "#1e293b",
        "top_bar":          "#0f172a",
        "border":           "#334155",
        "name":             "Midnight Cyber",
    },
    "light": {
        "bg":               "#f0f4f8",
        "sidebar_bg":       "#ffffff",
        "card_bg":          "#ffffff",
        "card_border":      "#e2e8f0",
        "accent":           "#0284c7",
        "accent_secondary": "#4f46e5",
        "accent_hover":     "#0369a1",
        "fg":               "#0f172a",
        "fg_dim":           "#64748b",
        "success":          "#059669",
        "danger":           "#e11d48",
        "warning":          "#d97706",
        "info":             "#2563eb",
        "row_even":         "#ffffff",
        "row_odd":          "#f1f5f9",
        "entry_bg":         "#f1f5f9",
        "tree_bg":          "#ffffff",
        "tree_head":        "#e2e8f0",
        "top_bar":          "#ffffff",
        "border":           "#cbd5e1",
        "name":             "Crystal Light",
    }
}

current_theme = "dark"

def get_theme():
    return THEMES[current_theme]

def toggle_theme():
    global current_theme
    current_theme = "light" if current_theme == "dark" else "dark"
    return THEMES[current_theme]

# ── Global TTK Styling ────────────────────────────────────────────────────────
def apply_ttk_styles(root):
    t = get_theme()
    style = ttk.Style(root)
    style.theme_use("clam")

    style.configure("Treeview",
                    background=t["tree_bg"], foreground=t["fg"],
                    fieldbackground=t["tree_bg"], rowheight=36,
                    font=("Segoe UI", 10), borderwidth=0)
    style.map("Treeview",
              background=[("selected", t["accent"])],
              foreground=[("selected", "white")])
    style.configure("Treeview.Heading",
                    background=t["tree_head"], foreground=t["fg"],
                    font=("Segoe UI", 10, "bold"), relief="flat", padding=6)
    style.map("Treeview.Heading",
              background=[("active", t["accent"])])
    style.configure("TCombobox",
                    fieldbackground=t["entry_bg"], background=t["entry_bg"],
                    foreground=t["fg"], arrowcolor=t["accent"],
                    bordercolor=t["border"], padding=6)
    style.configure("TNotebook",
                    background=t["bg"], borderwidth=0)
    style.configure("TNotebook.Tab",
                    background=t["card_bg"], foreground=t["fg_dim"],
                    font=("Segoe UI", 10, "bold"), padding=[16, 8], borderwidth=0)
    style.map("TNotebook.Tab",
              background=[("selected", t["accent"])],
              foreground=[("selected", "white")])

# ── Shared Logo Loader ────────────────────────────────────────────────────────
_logo_cache = {}   # keyed by (path, size)

def load_logo(size=110):
    """
    Returns a PhotoImage of the branding logo, resized to `size` x `size`.
    Falls back to None if Pillow or the file is unavailable.
    Cached so multiple calls don't re-read disk.
    """
    key = (LOGO_FILE, size)
    if key in _logo_cache:
        return _logo_cache[key]

    logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), LOGO_FILE)
    if not os.path.exists(logo_path):
        return None
    try:
        from PIL import Image, ImageTk
        img = Image.open(logo_path).resize((size, size), Image.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        _logo_cache[key] = photo
        return photo
    except Exception:
        return None

def logo_canvas(parent, size=100, bg=None):
    """
    Creates and returns a tk.Canvas widget containing the logo.
    Uses PNG if Pillow is available; otherwise draws a branded canvas fallback.
    `bg` defaults to the current theme sidebar_bg.
    """
    t = get_theme()
    bg = bg or t["sidebar_bg"]
    c = tk.Canvas(parent, width=size, height=size, bg=bg, highlightthickness=0)

    photo = load_logo(size)
    if photo:
        # Store reference on canvas to prevent GC
        c._logo_photo = photo
        c.create_image(size // 2, size // 2, image=photo)
    else:
        # Fallback: draw a branded circle
        import math
        r, cx, cy = size // 2, size // 2, size // 2
        c.create_oval(2, 2, size-2, size-2,
                      fill="#0d1b2e", outline=t["accent"], width=3)
        c.create_oval(size//8, size//8, size - size//8, size - size//8,
                      fill="#0d1b2e", outline=t["accent_secondary"], width=2)
        c.create_text(cx, cy - size//10,
                      text="EP", font=("Segoe UI", size // 4, "bold"),
                      fill=t["accent"])
        c.create_text(cx, cy + size // 4,
                      text="SAAS", font=("Segoe UI", size // 12, "bold"),
                      fill=t["accent_secondary"])
        for deg in range(0, 360, 45):
            rad = math.radians(deg)
            c.create_oval(cx + (r-7)*math.cos(rad)-3, cy + (r-7)*math.sin(rad)-3,
                          cx + (r-7)*math.cos(rad)+3, cy + (r-7)*math.sin(rad)+3,
                          fill=t["accent"], outline="")
    return c

# ── Unique Canvas Toggle Switch (Dark / Light mode) ──────────────────────────
class ThemeToggle(tk.Canvas):
    """
    A premium pill-shaped toggle switch that shows DARK / LIGHT mode.
    Call .set_command(fn) to register the toggle callback.
    """
    W, H = 80, 30   # dimensions

    def __init__(self, parent, command=None, **kwargs):
        t = get_theme()
        kwargs.setdefault("bg", t["top_bar"])
        super().__init__(parent, width=self.W, height=self.H,
                         highlightthickness=0, cursor="hand2", **kwargs)
        self._command = command
        self._draw()
        self.bind("<Button-1>", self._on_click)

    def set_command(self, fn):
        self._command = fn

    def _draw(self):
        self.delete("all")
        t = get_theme()
        is_dark = (current_theme == "dark")

        # Pill background
        pill_bg = "#1e293b" if is_dark else "#e2e8f0"
        self.create_rounded_rect(0, 0, self.W, self.H, radius=15, fill=pill_bg, outline="")

        # Sun icon (right side)
        self.create_text(self.W - 16, self.H // 2, text="Day",
                         font=("Segoe UI", 7, "bold"),
                         fill="#f59e0b" if not is_dark else "#64748b")

        # Moon icon (left side)
        self.create_text(16, self.H // 2, text="Night",
                         font=("Segoe UI", 7, "bold"),
                         fill=t["accent"] if is_dark else "#94a3b8")

        # Sliding circle knob
        knob_x = 16 if is_dark else self.W - 16
        knob_color = t["accent"] if is_dark else "#f59e0b"
        self.create_oval(knob_x - 11, 4, knob_x + 11, self.H - 4,
                         fill=knob_color, outline="white", width=2)

    def create_rounded_rect(self, x1, y1, x2, y2, radius=15, **kwargs):
        """Draws a rounded rectangle on the canvas."""
        pts = [
            x1+radius, y1,
            x2-radius, y1,
            x2, y1,
            x2, y1+radius,
            x2, y2-radius,
            x2, y2,
            x2-radius, y2,
            x1+radius, y2,
            x1, y2,
            x1, y2-radius,
            x1, y1+radius,
            x1, y1,
        ]
        return self.create_polygon(pts, smooth=True, **kwargs)

    def _on_click(self, event=None):
        if self._command:
            self._command()
        self._draw()

    def refresh(self):
        """Call after external theme toggle to redraw."""
        self._draw()
