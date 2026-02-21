import customtkinter as ctk
from datetime import datetime
from utils import db
import os

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

LESSONS = [
    {"title": "Password Hygiene", "time": "5 min", "difficulty": "Beginner", "icon": "🔐",
     "content": """PASSWORD HYGIENE BEST PRACTICES

DO:
• Use unique passwords for each account
• Make passwords at least 12 characters long
• Use a mix of uppercase, lowercase, numbers, and symbols
• Use a password manager to store passwords securely
• Enable two-factor authentication wherever possible
• Change passwords immediately if a breach is suspected

DON'T:
• Reuse passwords across multiple sites
• Use personal information (birthdays, names, etc.)
• Share passwords with others
• Write passwords on paper or sticky notes
• Use common words or patterns (password123, qwerty)
• Store passwords in plain text files

TIPS:
Create memorable passphrases using random words
Example: correct-horse-battery-staple
Use password generators for maximum security"""},
    
    {"title": "Phishing Red Flags", "time": "6 min", "difficulty": "Beginner", "icon": "🎣",
     "content": """IDENTIFYING PHISHING ATTEMPTS

RED FLAGS:
• Urgent or threatening language
• Requests for personal information
• Suspicious sender email addresses
• Generic greetings (Dear Customer)
• Spelling and grammar errors
• Mismatched URLs (hover to check)
• Unexpected attachments
• Too good to be true offers

WHAT TO DO:
• Verify sender through official channels
• Never click suspicious links
• Check URL carefully before entering credentials
• Report phishing to your IT department
• Delete suspicious emails immediately
• Use email filters and spam protection

REMEMBER:
Legitimate companies never ask for passwords via email
When in doubt, contact the company directly"""},
    
    {"title": "2FA Setup Guide", "time": "4 min", "difficulty": "Beginner", "icon": "📱",
     "content": """TWO-FACTOR AUTHENTICATION

WHAT IS 2FA?
An extra layer of security requiring two forms of verification:
1. Something you know (password)
2. Something you have (phone, token)

TYPES OF 2FA:
• SMS codes (least secure)
• Authenticator apps (Google, Microsoft, Authy)
• Hardware tokens (YubiKey)
• Biometric verification

SETUP STEPS:
1. Enable 2FA in account security settings
2. Choose your preferred method
3. Scan QR code with authenticator app
4. Save backup codes in secure location
5. Test the setup before logging out

BEST PRACTICES:
• Use authenticator apps over SMS
• Keep backup codes secure
• Enable 2FA on all critical accounts
• Update phone number if it changes"""},
    
    {"title": "Safe Browsing", "time": "5 min", "difficulty": "Intermediate", "icon": "🌐",
     "content": """SAFE BROWSING PRACTICES

SECURE CONNECTIONS:
• Always look for HTTPS (padlock icon)
• Avoid entering sensitive data on HTTP sites
• Use VPN on public networks
• Keep browser updated

PRIVACY SETTINGS:
• Block third-party cookies
• Use private/incognito mode when needed
• Clear browsing data regularly
• Disable location tracking
• Review browser permissions

EXTENSIONS & PLUGINS:
• Only install from official stores
• Review permissions before installing
• Keep extensions updated
• Remove unused extensions
• Use ad blockers and script blockers

WARNING SIGNS:
• Certificate errors
• Unexpected redirects
• Pop-up warnings
• Download prompts from unknown sites"""},
    
    {"title": "Social Engineering", "time": "7 min", "difficulty": "Intermediate", "icon": "🎭",
     "content": """SOCIAL ENGINEERING DEFENSE

COMMON TACTICS:
• Pretexting (fake scenarios)
• Baiting (free offers)
• Quid pro quo (something for something)
• Tailgating (physical access)
• Impersonation (authority figures)

PROTECTION STRATEGIES:
• Verify identities before sharing information
• Be skeptical of unsolicited requests
• Don't share sensitive info over phone/email
• Follow company security policies
• Report suspicious interactions
• Trust your instincts

PHONE SCAMS:
• Tech support scams
• IRS/government impersonation
• Bank fraud alerts
• Prize/lottery scams

REMEMBER:
Attackers exploit trust and urgency
Take time to verify before acting"""},
    
    {"title": "Public WiFi Risks", "time": "5 min", "difficulty": "Beginner", "icon": "📶",
     "content": """PUBLIC WIFI SECURITY

RISKS:
• Man-in-the-middle attacks
• Unencrypted data transmission
• Fake hotspots (evil twins)
• Session hijacking
• Malware distribution

SAFE PRACTICES:
• Use VPN on all public networks
• Avoid accessing sensitive accounts
• Disable auto-connect to WiFi
• Forget networks after use
• Turn off file sharing
• Use HTTPS websites only

VPN BENEFITS:
• Encrypts all traffic
• Hides your IP address
• Protects from snooping
• Secures data transmission

ALTERNATIVES:
• Use mobile data for sensitive tasks
• Create personal hotspot
• Wait for secure network"""},
    
    {"title": "Ransomware Defense", "time": "6 min", "difficulty": "Advanced", "icon": "🛡️",
     "content": """RANSOMWARE PROTECTION

PREVENTION:
• Keep systems and software updated
• Use reputable antivirus software
• Enable firewall protection
• Backup data regularly (3-2-1 rule)
• Disable macros in Office documents
• Use email filtering
• Restrict user permissions

BACKUP STRATEGY (3-2-1):
• 3 copies of data
• 2 different media types
• 1 offsite backup

IF INFECTED:
• Disconnect from network immediately
• Don't pay the ransom
• Report to authorities
• Restore from backups
• Scan all systems
• Change all passwords

WARNING SIGNS:
• Files become encrypted
• Ransom note appears
• Unusual file extensions
• System performance issues"""},
    
    {"title": "Incident Response", "time": "8 min", "difficulty": "Advanced", "icon": "🚨",
     "content": """SECURITY INCIDENT RESPONSE

IMMEDIATE ACTIONS:
1. Identify the incident type
2. Contain the threat
3. Document everything
4. Notify appropriate personnel
5. Preserve evidence

INCIDENT TYPES:
• Malware infection
• Data breach
• Unauthorized access
• Phishing attack
• Lost/stolen device
• Insider threat

RESPONSE STEPS:
PREPARATION: Have plan ready
IDENTIFICATION: Detect and verify
CONTAINMENT: Limit damage
ERADICATION: Remove threat
RECOVERY: Restore operations
LESSONS LEARNED: Improve defenses

REPORTING:
• Contact IT security team
• Document timeline
• List affected systems
• Note any data accessed
• Preserve logs and evidence

POST-INCIDENT:
• Review and update policies
• Conduct training
• Improve monitoring
• Test incident response plan"""}
]

QUIZ_QUESTIONS = [
    {"q": "What is the minimum recommended password length?", "options": ["6 characters", "8 characters", "12 characters", "16 characters"], "correct": 2},
    {"q": "Which 2FA method is most secure?", "options": ["SMS codes", "Email codes", "Authenticator app", "Security questions"], "correct": 2},
    {"q": "What does HTTPS indicate?", "options": ["Fast connection", "Encrypted connection", "Government site", "Free website"], "correct": 1},
    {"q": "What should you do if you receive a suspicious email?", "options": ["Click to investigate", "Reply asking if real", "Delete and report", "Forward to friends"], "correct": 2},
    {"q": "How often should you update software?", "options": ["Never", "Once a year", "When reminded", "As soon as updates available"], "correct": 3},
    {"q": "What is phishing?", "options": ["Fishing online", "Fake emails to steal info", "A type of virus", "Slow internet"], "correct": 1},
    {"q": "Should you use public WiFi for banking?", "options": ["Yes, always", "Yes, with VPN", "No, never", "Only on weekends"], "correct": 1},
    {"q": "What is ransomware?", "options": ["Free software", "Malware that encrypts files", "A type of game", "Antivirus program"], "correct": 1},
    {"q": "What does VPN stand for?", "options": ["Very Private Network", "Virtual Private Network", "Verified Public Network", "Visual Protocol Node"], "correct": 1},
    {"q": "What should you do if your device is stolen?", "options": ["Wait and see", "Change all passwords", "Buy a new one", "Nothing"], "correct": 1},
    {"q": "What is social engineering?", "options": ["Building bridges", "Manipulating people for info", "Social media marketing", "Engineering software"], "correct": 1},
    {"q": "How many backup copies should you maintain?", "options": ["1", "2", "3", "5"], "correct": 2},
    {"q": "What is a strong password example?", "options": ["password123", "MyName2024", "Tr0ub4dor&3", "12345678"], "correct": 2},
    {"q": "Should you click links in unexpected emails?", "options": ["Yes, always", "Yes, if curious", "No, verify first", "Only on mobile"], "correct": 2},
    {"q": "What is the purpose of a firewall?", "options": ["Speed up internet", "Block unauthorized access", "Store passwords", "Send emails"], "correct": 1},
    {"q": "How often should you backup important data?", "options": ["Never", "Once a year", "Monthly", "Regularly/Daily"], "correct": 3},
    {"q": "What should you do before installing software?", "options": ["Install immediately", "Verify source", "Ask friends", "Ignore warnings"], "correct": 1},
    {"q": "What is a zero-day vulnerability?", "options": ["Old bug", "Unknown exploit", "Free software", "Daily update"], "correct": 1},
    {"q": "Should you share passwords with coworkers?", "options": ["Yes, for convenience", "Yes, if trusted", "No, never", "Only with manager"], "correct": 2},
    {"q": "What is the best way to dispose of sensitive documents?", "options": ["Trash bin", "Recycle", "Shred", "Burn"], "correct": 2}
]

TIPS = [
    {"category": "Password", "tip": "Use a unique password for every account", "severity": "High", "icon": "🔐"},
    {"category": "Password", "tip": "Enable password manager auto-fill to avoid keyloggers", "severity": "Medium", "icon": "🔐"},
    {"category": "Email", "tip": "Hover over links before clicking to see real destination", "severity": "High", "icon": "📧"},
    {"category": "Email", "tip": "Check sender email address carefully for misspellings", "severity": "High", "icon": "📧"},
    {"category": "Network", "tip": "Always use VPN on public WiFi networks", "severity": "Critical", "icon": "📶"},
    {"category": "Network", "tip": "Disable auto-connect to WiFi networks", "severity": "Medium", "icon": "📶"},
    {"category": "Device", "tip": "Enable full disk encryption on all devices", "severity": "High", "icon": "💻"},
    {"category": "Device", "tip": "Set devices to auto-lock after 5 minutes", "severity": "Medium", "icon": "💻"},
    {"category": "Social", "tip": "Verify identity before sharing sensitive information", "severity": "Critical", "icon": "👤"},
    {"category": "Social", "tip": "Be cautious of urgent requests from unknown contacts", "severity": "High", "icon": "👤"},
    {"category": "Browser", "tip": "Clear cookies and cache regularly", "severity": "Low", "icon": "🌐"},
    {"category": "Browser", "tip": "Use private browsing for sensitive activities", "severity": "Medium", "icon": "🌐"},
    {"category": "Password", "tip": "Change passwords immediately after a breach", "severity": "Critical", "icon": "🔐"},
    {"category": "Email", "tip": "Never open attachments from unknown senders", "severity": "Critical", "icon": "📧"},
    {"category": "Network", "tip": "Use WPA3 encryption for home WiFi", "severity": "High", "icon": "📶"},
    {"category": "Device", "tip": "Keep all software and OS updated", "severity": "Critical", "icon": "💻"},
    {"category": "Social", "tip": "Don't share personal details on social media", "severity": "Medium", "icon": "👤"},
    {"category": "Browser", "tip": "Install ad-blocker and script-blocker extensions", "severity": "Medium", "icon": "🌐"},
    {"category": "Password", "tip": "Use passphrases instead of complex passwords", "severity": "Medium", "icon": "🔐"},
    {"category": "Email", "tip": "Enable spam filters and report phishing", "severity": "High", "icon": "📧"},
    {"category": "Network", "tip": "Disable remote access when not needed", "severity": "High", "icon": "📶"},
    {"category": "Device", "tip": "Use biometric authentication where available", "severity": "Medium", "icon": "💻"},
    {"category": "Social", "tip": "Verify requests through alternate communication channel", "severity": "High", "icon": "👤"},
    {"category": "Browser", "tip": "Check for HTTPS before entering credentials", "severity": "Critical", "icon": "🌐"},
    {"category": "Password", "tip": "Never reuse passwords across accounts", "severity": "Critical", "icon": "🔐"},
    {"category": "Email", "tip": "Be wary of emails creating sense of urgency", "severity": "High", "icon": "📧"},
    {"category": "Network", "tip": "Use firewall on all devices", "severity": "High", "icon": "📶"},
    {"category": "Device", "tip": "Backup data using 3-2-1 rule", "severity": "Critical", "icon": "💻"},
    {"category": "Social", "tip": "Question unexpected requests for money or info", "severity": "Critical", "icon": "👤"},
    {"category": "Browser", "tip": "Review and limit browser extension permissions", "severity": "Medium", "icon": "🌐"}
]

class TrainingWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Security Awareness Training")
        self.geometry("1200x740")
        self.configure(fg_color=BG)
        self.resizable(False, False)
        
        self.completed_lessons = set()
        self.read_tips = set()
        self.current_question = 0
        self.score = 0
        self.wrong_categories = []
        
        self._build()
    
    def _build(self):
        top = ctk.CTkFrame(self, fg_color=SURFACE, height=50, corner_radius=0)
        top.pack(fill="x")
        top.pack_propagate(False)
        
        home_btn = ctk.CTkButton(top, text="← HOME", width=100, fg_color=CARD,
                                 hover_color=BORDER, font=("Courier New", 11),
                                 command=self.go_home)
        home_btn.pack(side="left", padx=15, pady=10)
        
        ctk.CTkLabel(top, text="SECURITY AWARENESS TRAINING", font=("Courier New", 16, "bold"),
                    text_color=GREEN).pack(side="left", padx=15)
        
        ctk.CTkFrame(self, fg_color=BORDER, height=1).pack(fill="x")
        
        # Tabview
        self.tabview = ctk.CTkTabview(self, fg_color=BG, segmented_button_fg_color=SURFACE,
                                      segmented_button_selected_color=CARD,
                                      segmented_button_unselected_color=SURFACE)
        self.tabview.pack(fill="both", expand=True, padx=15, pady=15)
        
        self.tabview.add("LESSONS")
        self.tabview.add("QUIZ")
        self.tabview.add("TIPS FEED")
        
        self._build_lessons()
        self._build_quiz()
        self._build_tips()
    
    def go_home(self):
        self.destroy()
        import subprocess, sys
        subprocess.Popen([sys.executable, os.path.join(os.path.dirname(__file__), "home.py")])
    
    def _build_lessons(self):
        tab = self.tabview.tab("LESSONS")
        
        scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        scroll.grid_columnconfigure((0, 1), weight=1)
        
        for i, lesson in enumerate(LESSONS):
            row = i // 2
            col = i % 2
            
            card = ctk.CTkFrame(scroll, fg_color=CARD, border_color=BORDER, border_width=1, cursor="hand2")
            card.grid(row=row, column=col, sticky="ew", padx=5, pady=5)
            
            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="x", padx=15, pady=15)
            
            top_row = ctk.CTkFrame(inner, fg_color="transparent")
            top_row.pack(fill="x", pady=(0, 10))
            
            ctk.CTkLabel(top_row, text=lesson["icon"], font=("Courier New", 24)).pack(side="left", padx=(0, 10))
            
            title_frame = ctk.CTkFrame(top_row, fg_color="transparent")
            title_frame.pack(side="left", fill="x", expand=True)
            
            ctk.CTkLabel(title_frame, text=lesson["title"], font=("Courier New", 13, "bold"),
                        text_color=TEXT, anchor="w").pack(anchor="w")
            
            meta = ctk.CTkFrame(title_frame, fg_color="transparent")
            meta.pack(anchor="w")
            
            ctk.CTkLabel(meta, text=f"⏱ {lesson['time']}", font=("Courier New", 9),
                        text_color=TEXT_MID).pack(side="left", padx=(0, 10))
            
            diff_colors = {"Beginner": GREEN, "Intermediate": AMBER, "Advanced": RED}
            diff_color = diff_colors.get(lesson["difficulty"], TEXT_MID)
            
            badge = ctk.CTkFrame(meta, fg_color=diff_color, corner_radius=3)
            badge.pack(side="left")
            ctk.CTkLabel(badge, text=lesson["difficulty"], font=("Courier New", 8),
                        text_color=BG).pack(padx=6, pady=2)
            
            if i in self.completed_lessons:
                ctk.CTkLabel(top_row, text="✓", font=("Courier New", 20), text_color=GREEN).pack(side="right")
            
            card.bind("<Button-1>", lambda e, idx=i: self._show_lesson(idx))
    
    def _show_lesson(self, idx):
        lesson = LESSONS[idx]
        
        win = ctk.CTkToplevel(self)
        win.title(lesson["title"])
        win.geometry("700x600")
        win.configure(fg_color=BG)
        
        header = ctk.CTkFrame(win, fg_color=SURFACE, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        ctk.CTkLabel(header, text=f"{lesson['icon']}  {lesson['title']}", 
                    font=("Courier New", 16, "bold"), text_color=TEXT).pack(pady=15)
        
        content = ctk.CTkScrollableFrame(win, fg_color=CARD)
        content.pack(fill="both", expand=True, padx=20, pady=20)
        
        text = ctk.CTkTextbox(content, fg_color=CARD, font=("Courier New", 11),
                             text_color=TEXT, wrap="word", activate_scrollbars=False)
        text.pack(fill="both", expand=True)
        text.insert("1.0", lesson["content"])
        text.configure(state="disabled")
        
        btn_frame = ctk.CTkFrame(win, fg_color=BG)
        btn_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        if idx not in self.completed_lessons:
            complete_btn = ctk.CTkButton(btn_frame, text="Mark as Complete", height=40,
                                        fg_color=GREEN, hover_color="#25a045",
                                        font=("Courier New", 12, "bold"),
                                        command=lambda: self._complete_lesson(idx, win))
            complete_btn.pack(side="right")
        
        close_btn = ctk.CTkButton(btn_frame, text="Close", height=40, fg_color=CARD,
                                 hover_color=BORDER, font=("Courier New", 12),
                                 command=win.destroy)
        close_btn.pack(side="right", padx=(0, 10))
    
    def _complete_lesson(self, idx, window):
        self.completed_lessons.add(idx)
        window.destroy()
        self._build_lessons()
    
    def _build_quiz(self):
        tab = self.tabview.tab("QUIZ")
        
        self.quiz_container = ctk.CTkFrame(tab, fg_color="transparent")
        self.quiz_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        self._show_question()
    
    def _show_question(self):
        for widget in self.quiz_container.winfo_children():
            widget.destroy()
        
        if self.current_question >= len(QUIZ_QUESTIONS):
            self._show_results()
            return
        
        q = QUIZ_QUESTIONS[self.current_question]
        
        # Progress
        progress_frame = ctk.CTkFrame(self.quiz_container, fg_color=CARD, height=60)
        progress_frame.pack(fill="x", pady=(0, 20))
        progress_frame.pack_propagate(False)
        
        ctk.CTkLabel(progress_frame, text=f"Question {self.current_question + 1} of {len(QUIZ_QUESTIONS)}",
                    font=("Courier New", 12, "bold"), text_color=TEXT).pack(side="left", padx=20, pady=15)
        
        ctk.CTkLabel(progress_frame, text=f"Score: {self.score}/{self.current_question}",
                    font=("Courier New", 12), text_color=CYAN).pack(side="right", padx=20, pady=15)
        
        # Progress bar
        prog_bg = ctk.CTkFrame(self.quiz_container, fg_color=BORDER, height=8)
        prog_bg.pack(fill="x", pady=(0, 30))
        
        prog_width = int((self.current_question / len(QUIZ_QUESTIONS)) * prog_bg.winfo_reqwidth())
        prog_bar = ctk.CTkFrame(prog_bg, fg_color=CYAN, height=8, width=max(prog_width, 1))
        prog_bar.place(x=0, y=0)
        
        # Question
        q_frame = ctk.CTkFrame(self.quiz_container, fg_color=CARD, border_color=BORDER, border_width=1)
        q_frame.pack(fill="x", pady=(0, 30))
        
        ctk.CTkLabel(q_frame, text=q["q"], font=("Courier New", 14, "bold"),
                    text_color=TEXT, wraplength=800).pack(padx=30, pady=25)
        
        # Options
        for i, option in enumerate(q["options"]):
            opt_card = ctk.CTkFrame(self.quiz_container, fg_color=CARD, border_color=BORDER,
                                   border_width=1, cursor="hand2")
            opt_card.pack(fill="x", pady=5)
            
            ctk.CTkLabel(opt_card, text=f"{chr(65+i)}.  {option}", font=("Courier New", 12),
                        text_color=TEXT, anchor="w").pack(fill="x", padx=25, pady=20)
            
            opt_card.bind("<Button-1>", lambda e, idx=i: self._check_answer(idx))
    
    def _check_answer(self, selected):
        q = QUIZ_QUESTIONS[self.current_question]
        correct = q["correct"]
        
        if selected == correct:
            self.score += 1
            self._flash_feedback(GREEN, "✓ Correct!")
        else:
            self.wrong_categories.append(q["q"][:20])
            self._flash_feedback(RED, f"✗ Wrong! Correct answer: {chr(65+correct)}. {q['options'][correct]}")
        
        self.current_question += 1
        self.after(2000, self._show_question)
    
    def _flash_feedback(self, color, message):
        for widget in self.quiz_container.winfo_children():
            widget.destroy()
        
        feedback = ctk.CTkFrame(self.quiz_container, fg_color=color)
        feedback.pack(fill="both", expand=True)
        
        ctk.CTkLabel(feedback, text=message, font=("Courier New", 18, "bold"),
                    text_color=BG if color != BG else TEXT, wraplength=700).pack(expand=True)
    
    def _show_results(self):
        for widget in self.quiz_container.winfo_children():
            widget.destroy()
        
        percentage = (self.score / len(QUIZ_QUESTIONS)) * 100
        
        if percentage >= 90:
            grade = "A"
            color = GREEN
            advice = "Excellent! You have strong security awareness."
        elif percentage >= 80:
            grade = "B"
            color = GREEN
            advice = "Good job! Minor improvements needed."
        elif percentage >= 70:
            grade = "C"
            color = AMBER
            advice = "Fair. Review the lessons for better understanding."
        elif percentage >= 60:
            grade = "D"
            color = AMBER
            advice = "Needs improvement. Study the training materials."
        else:
            grade = "F"
            color = RED
            advice = "Poor. Please retake the training seriously."
        
        # Log to database
        weak_areas = ", ".join(self.wrong_categories[:5]) if self.wrong_categories else "None"
        db.log_quiz_result(self.score, len(QUIZ_QUESTIONS), percentage, weak_areas)
        
        result_card = ctk.CTkFrame(self.quiz_container, fg_color=CARD)
        result_card.pack(fill="both", expand=True, padx=50, pady=50)
        
        ctk.CTkLabel(result_card, text="Quiz Complete!", font=("Courier New", 24, "bold"),
                    text_color=TEXT).pack(pady=(40, 20))
        
        grade_frame = ctk.CTkFrame(result_card, fg_color=color, width=120, height=120, corner_radius=60)
        grade_frame.pack(pady=20)
        grade_frame.pack_propagate(False)
        
        ctk.CTkLabel(grade_frame, text=grade, font=("Courier New", 48, "bold"),
                    text_color=BG).pack(expand=True)
        
        ctk.CTkLabel(result_card, text=f"{self.score} / {len(QUIZ_QUESTIONS)} ({percentage:.0f}%)",
                    font=("Courier New", 18), text_color=TEXT).pack(pady=10)
        
        ctk.CTkLabel(result_card, text=advice, font=("Courier New", 12),
                    text_color=TEXT_MID, wraplength=500).pack(pady=20)
        
        btn_frame = ctk.CTkFrame(result_card, fg_color="transparent")
        btn_frame.pack(pady=(20, 40))
        
        retry_btn = ctk.CTkButton(btn_frame, text="Retry Quiz", height=40, fg_color=CYAN,
                                 hover_color="#0096b8", font=("Courier New", 12),
                                 command=self._retry_quiz)
        retry_btn.pack(side="left", padx=5)
        
        if self.wrong_categories:
            weak_btn = ctk.CTkButton(btn_frame, text="Retry Weak Areas", height=40, fg_color=AMBER,
                                    hover_color="#d88a4d", font=("Courier New", 12),
                                    command=self._retry_weak)
            weak_btn.pack(side="left", padx=5)
    
    def _retry_quiz(self):
        self.current_question = 0
        self.score = 0
        self.wrong_categories = []
        self._show_question()
    
    def _retry_weak(self):
        self.current_question = 0
        self.score = 0
        self.wrong_categories = []
        self._show_question()
    
    def _build_tips(self):
        tab = self.tabview.tab("TIPS FEED")
        
        # Filter bar
        filter_frame = ctk.CTkFrame(tab, fg_color=SURFACE, height=50)
        filter_frame.pack(fill="x", padx=10, pady=(10, 0))
        filter_frame.pack_propagate(False)
        
        ctk.CTkLabel(filter_frame, text="Filter:", font=("Courier New", 11),
                    text_color=TEXT_MID).pack(side="left", padx=15)
        
        self.filter_var = ctk.StringVar(value="All")
        
        categories = ["All", "Password", "Email", "Network", "Device", "Social", "Browser"]
        for cat in categories:
            btn = ctk.CTkButton(filter_frame, text=cat, width=80, height=30,
                               fg_color=CARD if cat != "All" else CYAN,
                               hover_color=BORDER, font=("Courier New", 9),
                               command=lambda c=cat: self._filter_tips(c))
            btn.pack(side="left", padx=2)
        
        # Tips scroll
        self.tips_scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        self.tips_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        self._show_tips("All")
    
    def _filter_tips(self, category):
        self.filter_var.set(category)
        self._show_tips(category)
    
    def _show_tips(self, category):
        for widget in self.tips_scroll.winfo_children():
            widget.destroy()
        
        # Daily tip
        daily_idx = datetime.now().day % len(TIPS)
        daily_tip = TIPS[daily_idx]
        
        daily_card = ctk.CTkFrame(self.tips_scroll, fg_color=CYAN, border_color=CYAN, border_width=2)
        daily_card.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(daily_card, text="⭐ TIP OF THE DAY", font=("Courier New", 10, "bold"),
                    text_color=BG).pack(anchor="w", padx=15, pady=(10, 5))
        
        ctk.CTkLabel(daily_card, text=f"{daily_tip['icon']}  {daily_tip['tip']}",
                    font=("Courier New", 12), text_color=BG, anchor="w",
                    wraplength=1000).pack(anchor="w", padx=15, pady=(0, 10))
        
        # Regular tips
        for i, tip in enumerate(TIPS):
            if category != "All" and tip["category"] != category:
                continue
            
            is_read = i in self.read_tips
            
            tip_card = ctk.CTkFrame(self.tips_scroll, fg_color=CARD if not is_read else INPUT_BG,
                                   border_color=BORDER, border_width=1)
            tip_card.pack(fill="x", pady=5)
            
            inner = ctk.CTkFrame(tip_card, fg_color="transparent")
            inner.pack(fill="x", padx=15, pady=12)
            
            left = ctk.CTkFrame(inner, fg_color="transparent")
            left.pack(side="left", fill="x", expand=True)
            
            top_row = ctk.CTkFrame(left, fg_color="transparent")
            top_row.pack(fill="x", pady=(0, 5))
            
            ctk.CTkLabel(top_row, text=tip["icon"], font=("Courier New", 16)).pack(side="left", padx=(0, 10))
            
            ctk.CTkLabel(top_row, text=tip["category"], font=("Courier New", 9, "bold"),
                        text_color=TEXT_MID).pack(side="left")
            
            severity_colors = {"Critical": RED, "High": AMBER, "Medium": CYAN, "Low": GREEN}
            sev_color = severity_colors.get(tip["severity"], TEXT_MID)
            
            sev_badge = ctk.CTkFrame(top_row, fg_color=sev_color, corner_radius=3)
            sev_badge.pack(side="left", padx=(10, 0))
            ctk.CTkLabel(sev_badge, text=tip["severity"], font=("Courier New", 8),
                        text_color=BG).pack(padx=6, pady=2)
            
            ctk.CTkLabel(left, text=tip["tip"], font=("Courier New", 11),
                        text_color=TEXT if not is_read else TEXT_MID, anchor="w",
                        wraplength=900).pack(anchor="w")
            
            if not is_read:
                mark_btn = ctk.CTkButton(inner, text="✓", width=40, height=40,
                                        fg_color=GREEN, hover_color="#25a045",
                                        font=("Courier New", 16),
                                        command=lambda idx=i: self._mark_read(idx, category))
                mark_btn.pack(side="right")
    
    def _mark_read(self, idx, category):
        self.read_tips.add(idx)
        self._show_tips(category)

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    root = ctk.CTk()
    root.withdraw()
    app = TrainingWindow(root)
    app.mainloop()
