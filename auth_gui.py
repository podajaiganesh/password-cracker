import customtkinter as ctk
import hashlib
import secrets
from datetime import datetime, timedelta
import sqlite3
from utils import db, session

# Color palette
BG = "#0a0a0a"
SURFACE = "#111111"
CARD = "#141414"
BORDER = "#222222"
INPUT_BG = "#0f0f0f"
RED = "#e63946"
GREEN = "#2dc653"
CYAN = "#00b4d8"
AMBER = "#f4a261"
TEXT = "#f0f0f0"
TEXT_MID = "#777777"

class AuthWindow(ctk.CTkToplevel):
    def __init__(self, parent, on_success):
        super().__init__(parent)
        self.on_success = on_success
        self.title("SECURENETRA - Authentication")
        self.geometry("500x650")
        self.configure(fg_color=BG)
        self.resizable(False, False)
        
        self.current_email = None
        self.current_username = None
        self.otp_timer_id = None
        self.otp_seconds = 300
        
        # Container for switching screens
        self.container = ctk.CTkFrame(self, fg_color=BG)
        self.container.pack(fill="both", expand=True)
        
        self.show_login()
        
    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()
    
    def show_login(self):
        self.clear_container()
        
        frame = ctk.CTkFrame(self.container, fg_color=BG)
        frame.pack(expand=True, fill="both", padx=40, pady=40)
        
        # Logo
        logo = ctk.CTkLabel(frame, text="◈ SECURENETRA", font=("Courier New", 32, "bold"), text_color=CYAN)
        logo.pack(pady=(0, 10))
        
        subtitle = ctk.CTkLabel(frame, text="Offensive AI Simulator", font=("Courier New", 12), text_color=TEXT_MID)
        subtitle.pack(pady=(0, 40))
        
        # Username
        ctk.CTkLabel(frame, text="Username", font=("Courier New", 12), text_color=TEXT).pack(anchor="w", pady=(0, 5))
        self.login_username = ctk.CTkEntry(frame, height=40, fg_color=INPUT_BG, border_color=BORDER, 
                                           text_color=TEXT, font=("Courier New", 12))
        self.login_username.pack(fill="x", pady=(0, 15))
        
        # Password
        ctk.CTkLabel(frame, text="Password", font=("Courier New", 12), text_color=TEXT).pack(anchor="w", pady=(0, 5))
        pass_frame = ctk.CTkFrame(frame, fg_color=INPUT_BG, border_color=BORDER, border_width=1)
        pass_frame.pack(fill="x", pady=(0, 30))
        
        self.login_password = ctk.CTkEntry(pass_frame, fg_color=INPUT_BG, border_width=0, show="●",
                                           text_color=TEXT, font=("Courier New", 12))
        self.login_password.pack(side="left", fill="both", expand=True, padx=10, pady=5)
        
        self.show_pass = False
        toggle_btn = ctk.CTkButton(pass_frame, text="👁", width=40, fg_color=CARD, hover_color=BORDER,
                                   command=self.toggle_password, font=("Courier New", 14))
        toggle_btn.pack(side="right", padx=5, pady=5)
        
        # Login button
        login_btn = ctk.CTkButton(frame, text="LOGIN", height=45, fg_color=RED, hover_color="#c62e3a",
                                  font=("Courier New", 14, "bold"), command=self.handle_login)
        login_btn.pack(fill="x", pady=(0, 15))
        
        # Create account link
        create_btn = ctk.CTkButton(frame, text="Create Account", fg_color="transparent", 
                                   hover_color=CARD, text_color=CYAN, font=("Courier New", 11),
                                   command=self.show_signup)
        create_btn.pack(pady=(0, 10))
        
        # Demo mode
        demo_btn = ctk.CTkButton(frame, text="Demo Mode", fg_color=CARD, hover_color=BORDER,
                                 font=("Courier New", 11), command=self.handle_demo)
        demo_btn.pack()
        
    def toggle_password(self):
        self.show_pass = not self.show_pass
        self.login_password.configure(show="" if self.show_pass else "●")
    
    def handle_login(self):
        username = self.login_username.get().strip()
        password = self.login_password.get()
        
        if not username or not password:
            self.show_error("Please fill all fields")
            return
        
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()
        
        if not user:
            self.show_error("Invalid username or password")
            return
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        if user["password_hash"] != password_hash:
            self.show_error("Invalid username or password")
            return
        
        # Generate OTP
        otp = secrets.token_digits(6)
        expiry = (datetime.now() + timedelta(minutes=5)).isoformat()
        
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET otp_code = ?, otp_expiry = ? WHERE username = ?",
                      (otp, expiry, username))
        conn.commit()
        conn.close()
        
        self.current_username = username
        self.current_email = user["email"]
        self.show_otp(otp)
    
    def handle_demo(self):
        session.set_user("demo_user", demo_mode=True)
        self.destroy()
        self.on_success()
    
    def show_signup(self):
        self.clear_container()
        
        frame = ctk.CTkFrame(self.container, fg_color=BG)
        frame.pack(expand=True, fill="both", padx=40, pady=40)
        
        ctk.CTkLabel(frame, text="Create Account", font=("Courier New", 24, "bold"), 
                    text_color=TEXT).pack(pady=(0, 30))
        
        # Username
        ctk.CTkLabel(frame, text="Username", font=("Courier New", 11), text_color=TEXT).pack(anchor="w", pady=(0, 5))
        self.signup_username = ctk.CTkEntry(frame, height=40, fg_color=INPUT_BG, border_color=BORDER,
                                           text_color=TEXT, font=("Courier New", 12))
        self.signup_username.pack(fill="x", pady=(0, 15))
        
        # Email
        ctk.CTkLabel(frame, text="Email", font=("Courier New", 11), text_color=TEXT).pack(anchor="w", pady=(0, 5))
        self.signup_email = ctk.CTkEntry(frame, height=40, fg_color=INPUT_BG, border_color=BORDER,
                                        text_color=TEXT, font=("Courier New", 12))
        self.signup_email.pack(fill="x", pady=(0, 15))
        
        # Password
        ctk.CTkLabel(frame, text="Password", font=("Courier New", 11), text_color=TEXT).pack(anchor="w", pady=(0, 5))
        self.signup_password = ctk.CTkEntry(frame, height=40, fg_color=INPUT_BG, border_color=BORDER,
                                           show="●", text_color=TEXT, font=("Courier New", 12))
        self.signup_password.pack(fill="x", pady=(0, 10))
        self.signup_password.bind("<KeyRelease>", self.update_strength)
        
        # Strength meter
        self.strength_frame = ctk.CTkFrame(frame, height=8, fg_color=BORDER)
        self.strength_frame.pack(fill="x", pady=(0, 5))
        self.strength_bar = ctk.CTkFrame(self.strength_frame, height=8, width=0, fg_color=RED)
        self.strength_bar.place(x=0, y=0)
        
        self.strength_label = ctk.CTkLabel(frame, text="", font=("Courier New", 10), text_color=TEXT_MID)
        self.strength_label.pack(anchor="w", pady=(0, 15))
        
        # Confirm password
        ctk.CTkLabel(frame, text="Confirm Password", font=("Courier New", 11), text_color=TEXT).pack(anchor="w", pady=(0, 5))
        self.signup_confirm = ctk.CTkEntry(frame, height=40, fg_color=INPUT_BG, border_color=BORDER,
                                          show="●", text_color=TEXT, font=("Courier New", 12))
        self.signup_confirm.pack(fill="x", pady=(0, 25))
        
        # Create button
        create_btn = ctk.CTkButton(frame, text="CREATE ACCOUNT", height=45, fg_color=GREEN,
                                   hover_color="#25a045", font=("Courier New", 14, "bold"),
                                   command=self.handle_signup)
        create_btn.pack(fill="x", pady=(0, 15))
        
        # Back link
        back_btn = ctk.CTkButton(frame, text="← Back to Login", fg_color="transparent",
                                hover_color=CARD, text_color=CYAN, font=("Courier New", 11),
                                command=self.show_login)
        back_btn.pack()
    
    def update_strength(self, event=None):
        password = self.signup_password.get()
        score = 0
        
        if len(password) >= 8:
            score += 20
        if any(c.isupper() for c in password):
            score += 20
        if any(c.islower() for c in password):
            score += 20
        if any(c.isdigit() for c in password):
            score += 20
        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            score += 20
        
        width = int(self.strength_frame.winfo_width() * score / 100)
        self.strength_bar.configure(width=max(width, 1))
        
        if score < 40:
            self.strength_bar.configure(fg_color=RED)
            self.strength_label.configure(text="Weak password", text_color=RED)
        elif score < 70:
            self.strength_bar.configure(fg_color=AMBER)
            self.strength_label.configure(text="Moderate password", text_color=AMBER)
        else:
            self.strength_bar.configure(fg_color=GREEN)
            self.strength_label.configure(text="Strong password", text_color=GREEN)
    
    def handle_signup(self):
        username = self.signup_username.get().strip()
        email = self.signup_email.get().strip()
        password = self.signup_password.get()
        confirm = self.signup_confirm.get()
        
        if not username or not email or not password or not confirm:
            self.show_error("Please fill all fields")
            return
        
        if password != confirm:
            self.show_error("Passwords do not match")
            return
        
        if len(password) < 8:
            self.show_error("Password must be at least 8 characters")
            return
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        try:
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, created_at)
                VALUES (?, ?, ?, ?)
            """, (username, email, password_hash, datetime.now().isoformat()))
            conn.commit()
            conn.close()
            
            # Generate OTP
            otp = secrets.token_digits(6)
            expiry = (datetime.now() + timedelta(minutes=5)).isoformat()
            
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET otp_code = ?, otp_expiry = ? WHERE username = ?",
                          (otp, expiry, username))
            conn.commit()
            conn.close()
            
            self.current_username = username
            self.current_email = email
            self.show_otp(otp)
            
        except sqlite3.IntegrityError:
            self.show_error("Username or email already exists")
    
    def show_otp(self, otp_code):
        self.clear_container()
        self.otp_seconds = 300
        
        frame = ctk.CTkFrame(self.container, fg_color=BG)
        frame.pack(expand=True, fill="both", padx=40, pady=40)
        
        ctk.CTkLabel(frame, text="Verify Your Email", font=("Courier New", 24, "bold"),
                    text_color=TEXT).pack(pady=(0, 15))
        
        masked_email = self.current_email[:3] + "***@" + self.current_email.split("@")[1]
        ctk.CTkLabel(frame, text=f"Enter the 6-digit code sent to\n{masked_email}",
                    font=("Courier New", 11), text_color=TEXT_MID).pack(pady=(0, 30))
        
        # OTP input boxes
        otp_frame = ctk.CTkFrame(frame, fg_color=BG)
        otp_frame.pack(pady=(0, 20))
        
        self.otp_entries = []
        for i in range(6):
            entry = ctk.CTkEntry(otp_frame, width=50, height=60, fg_color=INPUT_BG, border_color=BORDER,
                                text_color=TEXT, font=("Courier New", 24, "bold"), justify="center")
            entry.pack(side="left", padx=5)
            entry.bind("<KeyRelease>", lambda e, idx=i: self.otp_key_release(e, idx))
            self.otp_entries.append(entry)
        
        self.otp_entries[0].focus()
        
        # Timer
        self.timer_label = ctk.CTkLabel(frame, text="5:00", font=("Courier New", 14),
                                       text_color=TEXT_MID)
        self.timer_label.pack(pady=(0, 15))
        self.update_timer()
        
        # Resend button
        self.resend_btn = ctk.CTkButton(frame, text="Resend OTP", fg_color=CARD, hover_color=BORDER,
                                       font=("Courier New", 11), state="disabled", command=self.resend_otp)
        self.resend_btn.pack(pady=(0, 20))
        
        # Demo mode OTP display
        demo_label = ctk.CTkLabel(frame, text=f"Demo mode: your OTP is {otp_code}",
                                 font=("Courier New", 10), text_color=TEXT_MID)
        demo_label.pack()
        
        # Back link
        back_btn = ctk.CTkButton(frame, text="← Back to Login", fg_color="transparent",
                                hover_color=CARD, text_color=CYAN, font=("Courier New", 11),
                                command=self.show_login)
        back_btn.pack(pady=(10, 0))
    
    def otp_key_release(self, event, idx):
        entry = self.otp_entries[idx]
        value = entry.get()
        
        # Only allow digits
        if value and not value.isdigit():
            entry.delete(0, "end")
            return
        
        # Limit to 1 character
        if len(value) > 1:
            entry.delete(1, "end")
            value = entry.get()
        
        # Auto-advance
        if value and idx < 5:
            self.otp_entries[idx + 1].focus()
        
        # Auto-submit when all filled
        if all(e.get() for e in self.otp_entries):
            self.verify_otp()
    
    def verify_otp(self):
        entered_otp = "".join(e.get() for e in self.otp_entries)
        
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT otp_code, otp_expiry FROM users WHERE username = ?",
                      (self.current_username,))
        user = cursor.fetchone()
        conn.close()
        
        if not user or not user["otp_code"]:
            self.show_error("OTP not found")
            return
        
        expiry = datetime.fromisoformat(user["otp_expiry"])
        if datetime.now() > expiry:
            self.show_error("OTP expired")
            return
        
        if entered_otp != user["otp_code"]:
            self.show_error("Invalid OTP")
            for entry in self.otp_entries:
                entry.delete(0, "end")
            self.otp_entries[0].focus()
            return
        
        # Success
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET is_verified = 1, otp_code = NULL, otp_expiry = NULL WHERE username = ?",
                      (self.current_username,))
        conn.commit()
        conn.close()
        
        session.set_user(self.current_username)
        if self.otp_timer_id:
            self.after_cancel(self.otp_timer_id)
        self.destroy()
        self.on_success()
    
    def update_timer(self):
        if self.otp_seconds > 0:
            mins = self.otp_seconds // 60
            secs = self.otp_seconds % 60
            self.timer_label.configure(text=f"{mins}:{secs:02d}")
            self.otp_seconds -= 1
            self.otp_timer_id = self.after(1000, self.update_timer)
        else:
            self.timer_label.configure(text="Expired", text_color=RED)
            self.resend_btn.configure(state="normal")
    
    def resend_otp(self):
        otp = secrets.token_digits(6)
        expiry = (datetime.now() + timedelta(minutes=5)).isoformat()
        
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET otp_code = ?, otp_expiry = ? WHERE username = ?",
                      (otp, expiry, self.current_username))
        conn.commit()
        conn.close()
        
        self.show_otp(otp)
    
    def show_error(self, message):
        error_win = ctk.CTkToplevel(self)
        error_win.title("Error")
        error_win.geometry("350x150")
        error_win.configure(fg_color=CARD)
        error_win.resizable(False, False)
        
        ctk.CTkLabel(error_win, text="⚠", font=("Courier New", 32), text_color=RED).pack(pady=(20, 10))
        ctk.CTkLabel(error_win, text=message, font=("Courier New", 12), text_color=TEXT).pack(pady=(0, 20))
        ctk.CTkButton(error_win, text="OK", fg_color=RED, hover_color="#c62e3a",
                     command=error_win.destroy).pack()
