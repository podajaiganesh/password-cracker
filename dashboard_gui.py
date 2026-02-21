import customtkinter as ctk
from datetime import datetime, timedelta
from utils import db
import json
import os
import tkinter as tk

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

class DashboardWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Risk & Analytics Dashboard")
        self.geometry("1300x800")
        self.configure(fg_color=BG)
        self.resizable(False, False)
        
        self._build()
        self._load_data()
    
    def _build(self):
        top = ctk.CTkFrame(self, fg_color=SURFACE, height=50, corner_radius=0)
        top.pack(fill="x")
        top.pack_propagate(False)
        
        home_btn = ctk.CTkButton(top, text="← HOME", width=100, fg_color=CARD,
                                 hover_color=BORDER, font=("Courier New", 11),
                                 command=self.go_home)
        home_btn.pack(side="left", padx=15, pady=10)
        
        ctk.CTkLabel(top, text="RISK & ANALYTICS DASHBOARD", font=("Courier New", 16, "bold"),
                    text_color="#9d4edd").pack(side="left", padx=15)
        
        export_frame = ctk.CTkFrame(top, fg_color="transparent")
        export_frame.pack(side="right", padx=15)
        
        ctk.CTkButton(export_frame, text="PDF Report", width=100, height=30, fg_color=CARD,
                     hover_color=BORDER, font=("Courier New", 9),
                     command=self.export_pdf).pack(side="left", padx=3)
        
        ctk.CTkButton(export_frame, text="JSON Export", width=100, height=30, fg_color=CARD,
                     hover_color=BORDER, font=("Courier New", 9),
                     command=self.export_json).pack(side="left", padx=3)
        
        ctk.CTkButton(export_frame, text="Clear Data", width=100, height=30, fg_color=RED,
                     hover_color="#c62e3a", font=("Courier New", 9),
                     command=self.clear_data).pack(side="left", padx=3)
        
        ctk.CTkFrame(self, fg_color=BORDER, height=1).pack(fill="x")
        
        content = ctk.CTkScrollableFrame(self, fg_color=BG)
        content.pack(fill="both", expand=True, padx=15, pady=15)
        
        self._build_metrics(content)
        self._build_charts(content)
        self._build_reports(content)
    
    def go_home(self):
        self.destroy()
        import subprocess, sys
        subprocess.Popen([sys.executable, os.path.join(os.path.dirname(__file__), "home.py")])
    
    def _build_metrics(self, parent):
        metrics_frame = ctk.CTkFrame(parent, fg_color="transparent")
        metrics_frame.pack(fill="x", pady=(0, 20))
        
        metrics_frame.grid_columnconfigure((0,1,2,3,4,5), weight=1)
        
        self.metric_widgets = {}
        
        metrics = [
            ("Total Attacks", "0", CYAN),
            ("Crack Rate", "0%", RED),
            ("Avg Speed", "0 H/s", AMBER),
            ("Phishing Checked", "0", "#9d4edd"),
            ("High Risk Domains", "0", RED),
            ("Quiz Average", "0%", GREEN)
        ]
        
        for i, (label, value, color) in enumerate(metrics):
            card = ctk.CTkFrame(metrics_frame, fg_color=CARD, border_color=BORDER, border_width=1)
            card.grid(row=0, column=i, sticky="ew", padx=5)
            
            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(padx=15, pady=15)
            
            val_label = ctk.CTkLabel(inner, text=value, font=("Courier New", 20, "bold"),
                                    text_color=color)
            val_label.pack()
            
            ctk.CTkLabel(inner, text=label, font=("Courier New", 9),
                        text_color=TEXT_MID).pack()
            
            self.metric_widgets[label] = val_label
    
    def _build_charts(self, parent):
        charts_frame = ctk.CTkFrame(parent, fg_color="transparent")
        charts_frame.pack(fill="x", pady=(0, 20))
        
        charts_frame.grid_columnconfigure((0,1), weight=1)
        
        # Bar chart
        bar_card = ctk.CTkFrame(charts_frame, fg_color=CARD, border_color=BORDER, border_width=1)
        bar_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        ctk.CTkLabel(bar_card, text="Attacks Per Day (Last 7 Days)", font=("Courier New", 12, "bold"),
                    text_color=TEXT).pack(pady=(15, 10))
        
        self.bar_container = ctk.CTkFrame(bar_card, fg_color=INPUT_BG, height=200)
        self.bar_container.pack(fill="x", padx=20, pady=(0, 15))
        
        # Donut chart
        donut_card = ctk.CTkFrame(charts_frame, fg_color=CARD, border_color=BORDER, border_width=1)
        donut_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        ctk.CTkLabel(donut_card, text="Attack Success Rate", font=("Courier New", 12, "bold"),
                    text_color=TEXT).pack(pady=(15, 10))
        
        self.donut_canvas = tk.Canvas(donut_card, width=250, height=200, bg=INPUT_BG,
                                     highlightthickness=0)
        self.donut_canvas.pack(pady=(0, 15))
    
    def _build_reports(self, parent):
        reports_frame = ctk.CTkFrame(parent, fg_color=CARD, border_color=BORDER, border_width=1)
        reports_frame.pack(fill="both", expand=True)
        
        ctk.CTkLabel(reports_frame, text="DETAILED REPORTS", font=("Courier New", 12, "bold"),
                    text_color=TEXT).pack(pady=15)
        
        self.report_tabs = ctk.CTkTabview(reports_frame, fg_color=CARD,
                                          segmented_button_fg_color=INPUT_BG,
                                          segmented_button_selected_color=SURFACE)
        self.report_tabs.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        self.report_tabs.add("ATTACKS")
        self.report_tabs.add("PHISHING")
        self.report_tabs.add("DOMAINS")
        self.report_tabs.add("TIMELINE")
        
        self.attacks_scroll = ctk.CTkScrollableFrame(self.report_tabs.tab("ATTACKS"), fg_color="transparent")
        self.attacks_scroll.pack(fill="both", expand=True)
        
        self.phishing_scroll = ctk.CTkScrollableFrame(self.report_tabs.tab("PHISHING"), fg_color="transparent")
        self.phishing_scroll.pack(fill="both", expand=True)
        
        self.domains_scroll = ctk.CTkScrollableFrame(self.report_tabs.tab("DOMAINS"), fg_color="transparent")
        self.domains_scroll.pack(fill="both", expand=True)
        
        self.timeline_scroll = ctk.CTkScrollableFrame(self.report_tabs.tab("TIMELINE"), fg_color="transparent")
        self.timeline_scroll.pack(fill="both", expand=True)
    
    def _load_data(self):
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Metrics
        cursor.execute("SELECT COUNT(*) FROM attacks")
        total_attacks = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM attacks WHERE result = 'SUCCESS'")
        successful = cursor.fetchone()[0]
        crack_rate = (successful / total_attacks * 100) if total_attacks > 0 else 0
        
        cursor.execute("SELECT AVG(speed) FROM attacks WHERE speed IS NOT NULL")
        avg_speed = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT COUNT(*) FROM phishing_checks")
        phishing_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM domain_checks WHERE verdict = 'HIGH RISK'")
        high_risk = cursor.fetchone()[0]
        
        cursor.execute("SELECT AVG(percentage) FROM quiz_results")
        quiz_avg = cursor.fetchone()[0] or 0
        
        self.metric_widgets["Total Attacks"].configure(text=str(total_attacks))
        self.metric_widgets["Crack Rate"].configure(text=f"{crack_rate:.1f}%")
        self.metric_widgets["Avg Speed"].configure(text=f"{avg_speed:.0f} H/s")
        self.metric_widgets["Phishing Checked"].configure(text=str(phishing_count))
        self.metric_widgets["High Risk Domains"].configure(text=str(high_risk))
        self.metric_widgets["Quiz Average"].configure(text=f"{quiz_avg:.0f}%")
        
        # Bar chart data
        self._draw_bar_chart(cursor)
        
        # Donut chart
        self._draw_donut_chart(successful, total_attacks - successful)
        
        # Reports
        self._load_attacks_report(cursor)
        self._load_phishing_report(cursor)
        self._load_domains_report(cursor)
        self._load_timeline(cursor)
        
        conn.close()
    
    def _draw_bar_chart(self, cursor):
        days_data = []
        for i in range(6, -1, -1):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            cursor.execute("SELECT COUNT(*) FROM attacks WHERE DATE(timestamp) = ?", (date,))
            count = cursor.fetchone()[0]
            days_data.append((date[-5:], count))
        
        max_count = max([d[1] for d in days_data]) if days_data else 1
        if max_count == 0:
            max_count = 1
        
        bar_width = 60
        spacing = 20
        
        for i, (day, count) in enumerate(days_data):
            x = i * (bar_width + spacing) + 30
            height = int((count / max_count) * 150) if count > 0 else 5
            
            bar = ctk.CTkFrame(self.bar_container, fg_color=CYAN, width=bar_width, height=height)
            bar.place(x=x, y=160 - height)
            
            ctk.CTkLabel(self.bar_container, text=str(count), font=("Courier New", 9),
                        text_color=TEXT).place(x=x + bar_width//2, y=160 - height - 15, anchor="center")
            
            ctk.CTkLabel(self.bar_container, text=day, font=("Courier New", 8),
                        text_color=TEXT_MID).place(x=x + bar_width//2, y=175, anchor="center")
    
    def _draw_donut_chart(self, success, fail):
        total = success + fail
        if total == 0:
            self.donut_canvas.create_text(125, 100, text="No Data", fill=TEXT_MID,
                                         font=("Courier New", 14))
            return
        
        success_angle = int((success / total) * 360)
        
        # Draw arcs
        self.donut_canvas.create_arc(25, 25, 225, 225, start=0, extent=success_angle,
                                     fill=GREEN, outline="")
        self.donut_canvas.create_arc(25, 25, 225, 225, start=success_angle, extent=360-success_angle,
                                     fill=RED, outline="")
        
        # Inner circle
        self.donut_canvas.create_oval(75, 75, 175, 175, fill=INPUT_BG, outline="")
        
        # Center text
        self.donut_canvas.create_text(125, 100, text=f"{(success/total*100):.0f}%",
                                     fill=TEXT, font=("Courier New", 20, "bold"))
        self.donut_canvas.create_text(125, 125, text="Success Rate",
                                     fill=TEXT_MID, font=("Courier New", 9))
    
    def _load_attacks_report(self, cursor):
        cursor.execute("SELECT * FROM attacks ORDER BY timestamp DESC LIMIT 50")
        attacks = cursor.fetchall()
        
        if not attacks:
            ctk.CTkLabel(self.attacks_scroll, text="No attack data available",
                        font=("Courier New", 11), text_color=TEXT_MID).pack(pady=50)
            return
        
        for attack in attacks:
            card = ctk.CTkFrame(self.attacks_scroll, fg_color=INPUT_BG, border_color=BORDER, border_width=1)
            card.pack(fill="x", pady=5)
            
            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="x", padx=15, pady=10)
            
            left = ctk.CTkFrame(inner, fg_color="transparent")
            left.pack(side="left", fill="x", expand=True)
            
            ctk.CTkLabel(left, text=f"{attack['mode']} - {attack['algorithm']}",
                        font=("Courier New", 11, "bold"), text_color=TEXT, anchor="w").pack(anchor="w")
            
            ctk.CTkLabel(left, text=f"{attack['timestamp'][:19]} | {attack['attempts']} attempts | {attack['time_taken']:.2f}s",
                        font=("Courier New", 9), text_color=TEXT_MID, anchor="w").pack(anchor="w")
            
            result_color = GREEN if attack['result'] == 'SUCCESS' else RED
            result_badge = ctk.CTkFrame(inner, fg_color=result_color, corner_radius=3)
            result_badge.pack(side="right")
            ctk.CTkLabel(result_badge, text=attack['result'], font=("Courier New", 9),
                        text_color=BG).pack(padx=10, pady=5)
    
    def _load_phishing_report(self, cursor):
        cursor.execute("SELECT * FROM phishing_checks ORDER BY timestamp DESC LIMIT 50")
        checks = cursor.fetchall()
        
        if not checks:
            ctk.CTkLabel(self.phishing_scroll, text="No phishing data available",
                        font=("Courier New", 11), text_color=TEXT_MID).pack(pady=50)
            return
        
        for check in checks:
            card = ctk.CTkFrame(self.phishing_scroll, fg_color=INPUT_BG, border_color=BORDER, border_width=1)
            card.pack(fill="x", pady=5)
            
            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="x", padx=15, pady=10)
            
            left = ctk.CTkFrame(inner, fg_color="transparent")
            left.pack(side="left", fill="x", expand=True)
            
            ctk.CTkLabel(left, text=check['subject'] or "No Subject",
                        font=("Courier New", 11, "bold"), text_color=TEXT, anchor="w").pack(anchor="w")
            
            ctk.CTkLabel(left, text=f"{check['timestamp'][:19]} | From: {check['sender']}",
                        font=("Courier New", 9), text_color=TEXT_MID, anchor="w").pack(anchor="w")
            
            right = ctk.CTkFrame(inner, fg_color="transparent")
            right.pack(side="right")
            
            score = check['risk_score']
            if score >= 70:
                bar_color = RED
            elif score >= 40:
                bar_color = AMBER
            else:
                bar_color = GREEN
            
            score_frame = ctk.CTkFrame(right, fg_color=BORDER, width=100, height=20)
            score_frame.pack()
            score_frame.pack_propagate(False)
            
            bar = ctk.CTkFrame(score_frame, fg_color=bar_color, height=20, width=score)
            bar.place(x=0, y=0)
            
            ctk.CTkLabel(score_frame, text=f"{score}%", font=("Courier New", 9),
                        text_color=TEXT).place(relx=0.5, rely=0.5, anchor="center")
    
    def _load_domains_report(self, cursor):
        cursor.execute("SELECT * FROM domain_checks ORDER BY timestamp DESC LIMIT 50")
        domains = cursor.fetchall()
        
        if not domains:
            ctk.CTkLabel(self.domains_scroll, text="No domain data available",
                        font=("Courier New", 11), text_color=TEXT_MID).pack(pady=50)
            return
        
        for domain in domains:
            card = ctk.CTkFrame(self.domains_scroll, fg_color=INPUT_BG, border_color=BORDER, border_width=1)
            card.pack(fill="x", pady=5)
            
            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="x", padx=15, pady=10)
            
            left = ctk.CTkFrame(inner, fg_color="transparent")
            left.pack(side="left", fill="x", expand=True)
            
            ctk.CTkLabel(left, text=domain['domain'],
                        font=("Courier New", 11, "bold"), text_color=TEXT, anchor="w").pack(anchor="w")
            
            ctk.CTkLabel(left, text=f"{domain['timestamp'][:19]} | IP: {domain['ip_address']} | SSL: {domain['ssl_valid']}",
                        font=("Courier New", 9), text_color=TEXT_MID, anchor="w").pack(anchor="w")
            
            verdict_colors = {"HIGH RISK": RED, "SUSPICIOUS": AMBER, "SAFE": GREEN}
            verdict_color = verdict_colors.get(domain['verdict'], TEXT_MID)
            
            verdict_badge = ctk.CTkFrame(inner, fg_color=verdict_color, corner_radius=3)
            verdict_badge.pack(side="right")
            ctk.CTkLabel(verdict_badge, text=domain['verdict'], font=("Courier New", 9),
                        text_color=BG).pack(padx=10, pady=5)
    
    def _load_timeline(self, cursor):
        events = []
        
        cursor.execute("SELECT 'ATTACK' as type, timestamp, mode, result FROM attacks ORDER BY timestamp DESC LIMIT 20")
        for row in cursor.fetchall():
            events.append(dict(row))
        
        cursor.execute("SELECT 'PHISHING' as type, timestamp, subject, risk_score FROM phishing_checks ORDER BY timestamp DESC LIMIT 20")
        for row in cursor.fetchall():
            events.append(dict(row))
        
        cursor.execute("SELECT 'DOMAIN' as type, timestamp, domain, verdict FROM domain_checks ORDER BY timestamp DESC LIMIT 20")
        for row in cursor.fetchall():
            events.append(dict(row))
        
        cursor.execute("SELECT 'QUIZ' as type, timestamp, score, total FROM quiz_results ORDER BY timestamp DESC LIMIT 20")
        for row in cursor.fetchall():
            events.append(dict(row))
        
        events.sort(key=lambda x: x['timestamp'], reverse=True)
        
        if not events:
            ctk.CTkLabel(self.timeline_scroll, text="No events recorded",
                        font=("Courier New", 11), text_color=TEXT_MID).pack(pady=50)
            return
        
        for event in events[:100]:
            card = ctk.CTkFrame(self.timeline_scroll, fg_color=INPUT_BG, border_color=BORDER, border_width=1)
            card.pack(fill="x", pady=3)
            
            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="x", padx=15, pady=8)
            
            type_colors = {"ATTACK": CYAN, "PHISHING": AMBER, "DOMAIN": "#9d4edd", "QUIZ": GREEN}
            type_color = type_colors.get(event['type'], TEXT_MID)
            
            type_badge = ctk.CTkFrame(inner, fg_color=type_color, corner_radius=3, width=80)
            type_badge.pack(side="left")
            type_badge.pack_propagate(False)
            ctk.CTkLabel(type_badge, text=event['type'], font=("Courier New", 8),
                        text_color=BG).pack(pady=3)
            
            ctk.CTkLabel(inner, text=event['timestamp'][:19], font=("Courier New", 9),
                        text_color=TEXT_MID).pack(side="left", padx=10)
            
            if event['type'] == 'ATTACK':
                text = f"{event['mode']} - {event['result']}"
            elif event['type'] == 'PHISHING':
                text = f"{event.get('subject', 'N/A')} - Risk: {event.get('risk_score', 0)}%"
            elif event['type'] == 'DOMAIN':
                text = f"{event.get('domain', 'N/A')} - {event.get('verdict', 'N/A')}"
            else:
                text = f"Score: {event.get('score', 0)}/{event.get('total', 0)}"
            
            ctk.CTkLabel(inner, text=text, font=("Courier New", 10),
                        text_color=TEXT, anchor="w").pack(side="left", fill="x", expand=True)
    
    def export_pdf(self):
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas
            
            downloads = os.path.expanduser("~/Downloads")
            filename = f"securenetra_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            filepath = os.path.join(downloads, filename)
            
            c = canvas.Canvas(filepath, pagesize=letter)
            c.setFont("Courier", 16)
            c.drawString(50, 750, "SECURENETRA - Security Report")
            c.setFont("Courier", 10)
            c.drawString(50, 730, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            y = 700
            c.drawString(50, y, f"Total Attacks: {self.metric_widgets['Total Attacks'].cget('text')}")
            y -= 20
            c.drawString(50, y, f"Crack Rate: {self.metric_widgets['Crack Rate'].cget('text')}")
            y -= 20
            c.drawString(50, y, f"Phishing Checked: {self.metric_widgets['Phishing Checked'].cget('text')}")
            
            c.save()
            self._show_success(f"PDF saved to:\n{filepath}")
        except ImportError:
            self._export_txt()
    
    def _export_txt(self):
        downloads = os.path.expanduser("~/Downloads")
        filename = f"securenetra_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = os.path.join(downloads, filename)
        
        with open(filepath, "w") as f:
            f.write("SECURENETRA - SECURITY REPORT\n")
            f.write("=" * 60 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("METRICS\n")
            f.write("-" * 60 + "\n")
            for label, widget in self.metric_widgets.items():
                f.write(f"{label}: {widget.cget('text')}\n")
            
            f.write("\n" + "=" * 60 + "\n")
        
        self._show_success(f"Report saved to:\n{filepath}")
    
    def export_json(self):
        conn = db.get_connection()
        cursor = conn.cursor()
        
        data = {
            "generated": datetime.now().isoformat(),
            "attacks": [],
            "phishing_checks": [],
            "domain_checks": [],
            "quiz_results": []
        }
        
        cursor.execute("SELECT * FROM attacks")
        data["attacks"] = [dict(row) for row in cursor.fetchall()]
        
        cursor.execute("SELECT * FROM phishing_checks")
        data["phishing_checks"] = [dict(row) for row in cursor.fetchall()]
        
        cursor.execute("SELECT * FROM domain_checks")
        data["domain_checks"] = [dict(row) for row in cursor.fetchall()]
        
        cursor.execute("SELECT * FROM quiz_results")
        data["quiz_results"] = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        downloads = os.path.expanduser("~/Downloads")
        filename = f"securenetra_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(downloads, filename)
        
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        
        self._show_success(f"Data exported to:\n{filepath}")
    
    def clear_data(self):
        confirm = ctk.CTkToplevel(self)
        confirm.title("Confirm Clear Data")
        confirm.geometry("400x200")
        confirm.configure(fg_color=CARD)
        confirm.resizable(False, False)
        
        ctk.CTkLabel(confirm, text="⚠", font=("Courier New", 32), text_color=RED).pack(pady=(30, 10))
        ctk.CTkLabel(confirm, text="Delete all data?\nThis cannot be undone.",
                    font=("Courier New", 12), text_color=TEXT).pack(pady=(0, 20))
        
        btn_frame = ctk.CTkFrame(confirm, fg_color="transparent")
        btn_frame.pack()
        
        def do_clear():
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM attacks")
            cursor.execute("DELETE FROM phishing_checks")
            cursor.execute("DELETE FROM domain_checks")
            cursor.execute("DELETE FROM quiz_results")
            conn.commit()
            conn.close()
            confirm.destroy()
            self.destroy()
            self.__init__(self.master)
        
        ctk.CTkButton(btn_frame, text="Cancel", fg_color=CARD, hover_color=BORDER,
                     command=confirm.destroy).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Delete All", fg_color=RED, hover_color="#c62e3a",
                     command=do_clear).pack(side="left", padx=5)
    
    def _show_success(self, message):
        msg = ctk.CTkToplevel(self)
        msg.title("Success")
        msg.geometry("400x150")
        msg.configure(fg_color=CARD)
        msg.resizable(False, False)
        
        ctk.CTkLabel(msg, text="✓", font=("Courier New", 32), text_color=GREEN).pack(pady=(20, 10))
        ctk.CTkLabel(msg, text=message, font=("Courier New", 10),
                    text_color=TEXT_MID).pack(pady=(0, 20))
        ctk.CTkButton(msg, text="OK", fg_color=GREEN, command=msg.destroy).pack()

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    root = ctk.CTk()
    root.withdraw()
    app = DashboardWindow(root)
    app.mainloop()
