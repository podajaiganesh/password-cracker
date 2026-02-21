import customtkinter as ctk
import ssl
import socket
import threading
import json
from datetime import datetime
from urllib.parse import urlparse
from utils import db
import os

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

KNOWN_BRANDS = [
    "amazon", "google", "paypal", "microsoft", "apple", "facebook", "netflix",
    "twitter", "instagram", "linkedin", "ebay", "walmart", "target", "bestbuy",
    "chase", "bankofamerica", "wellsfargo", "citibank", "usbank", "capitalone",
    "dropbox", "spotify", "adobe", "oracle", "salesforce", "zoom", "slack",
    "github", "gitlab", "stackoverflow", "reddit", "youtube", "twitch", "discord",
    "whatsapp", "telegram", "signal", "skype", "outlook", "yahoo", "gmail",
    "icloud", "onedrive", "googledrive", "box", "mega", "mediafire", "rapidshare"
]

HIGH_RISK_TLDS = [".tk", ".ml", ".ga", ".cf", ".gq"]

HOMOGRAPH_CHARS = {
    "0": "o", "1": "l", "rn": "m", "vv": "w", "cl": "d",
    "i": "l", "l": "i", "o": "0", "s": "5", "5": "s"
}

class DomainSpoof(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Domain Spoof Detector")
        self.geometry("1200x740")
        self.configure(fg_color=BG)
        self.resizable(False, False)
        
        self.history = []
        self.checking = False
        
        self._build()
    
    def _build(self):
        # Top bar with home button
        top = ctk.CTkFrame(self, fg_color=SURFACE, height=50, corner_radius=0)
        top.pack(fill="x")
        top.pack_propagate(False)
        
        home_btn = ctk.CTkButton(top, text="← HOME", width=100, fg_color=CARD,
                                 hover_color=BORDER, font=("Courier New", 11),
                                 command=self.go_home)
        home_btn.pack(side="left", padx=15, pady=10)
        
        ctk.CTkLabel(top, text="DOMAIN SPOOF DETECTOR", font=("Courier New", 16, "bold"),
                    text_color=CYAN).pack(side="left", padx=15)
        
        ctk.CTkFrame(self, fg_color=BORDER, height=1).pack(fill="x")
        
        # Main content
        content = ctk.CTkFrame(self, fg_color=BG)
        content.pack(fill="both", expand=True)
        
        # Left panel
        left = ctk.CTkFrame(content, fg_color=SURFACE, width=350)
        left.pack(side="left", fill="y", padx=(15, 7), pady=15)
        left.pack_propagate(False)
        
        self._build_left(left)
        
        # Right panel
        right = ctk.CTkFrame(content, fg_color=BG)
        right.pack(side="right", fill="both", expand=True, padx=(7, 15), pady=15)
        
        self._build_right(right)
    
    def _build_left(self, parent):
        inner = ctk.CTkFrame(parent, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(inner, text="Domain to Analyze", font=("Courier New", 12, "bold"),
                    text_color=TEXT).pack(anchor="w", pady=(0, 8))
        
        self.domain_entry = ctk.CTkEntry(inner, height=40, fg_color=INPUT_BG, border_color=BORDER,
                                        text_color=TEXT, font=("Courier New", 12),
                                        placeholder_text="e.g. paypa1.com")
        self.domain_entry.pack(fill="x", pady=(0, 15))
        
        self.analyze_btn = ctk.CTkButton(inner, text="ANALYSE DOMAIN", height=45, fg_color=RED,
                                        hover_color="#c62e3a", font=("Courier New", 13, "bold"),
                                        command=self.analyze_domain)
        self.analyze_btn.pack(fill="x", pady=(0, 25))
        
        # Recent checks
        ctk.CTkLabel(inner, text="Recent Checks", font=("Courier New", 11, "bold"),
                    text_color=TEXT_MID).pack(anchor="w", pady=(0, 10))
        
        self.history_frame = ctk.CTkScrollableFrame(inner, fg_color=CARD, height=350)
        self.history_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        clear_btn = ctk.CTkButton(inner, text="Clear History", height=35, fg_color=CARD,
                                 hover_color=BORDER, font=("Courier New", 10),
                                 command=self.clear_history)
        clear_btn.pack(fill="x")
    
    def _build_right(self, parent):
        self.results_container = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        self.results_container.pack(fill="both", expand=True)
        
        # Initial message
        self.initial_msg = ctk.CTkFrame(self.results_container, fg_color=CARD, height=400)
        self.initial_msg.pack(fill="both", expand=True, pady=100)
        
        ctk.CTkLabel(self.initial_msg, text="🔍", font=("Courier New", 48)).pack(pady=(60, 20))
        ctk.CTkLabel(self.initial_msg, text="Enter a domain to analyze",
                    font=("Courier New", 14), text_color=TEXT_MID).pack()
    
    def go_home(self):
        self.destroy()
        import subprocess, sys
        subprocess.Popen([sys.executable, os.path.join(os.path.dirname(__file__), "home.py")])
    
    def analyze_domain(self):
        domain = self.domain_entry.get().strip()
        if not domain or self.checking:
            return
        
        # Clean domain
        if "://" in domain:
            domain = urlparse(domain).netloc or urlparse(domain).path
        domain = domain.split("/")[0].split(":")[0]
        
        if not domain:
            return
        
        self.checking = True
        self.analyze_btn.configure(state="disabled", text="ANALYZING...")
        
        # Clear initial message
        if self.initial_msg:
            self.initial_msg.destroy()
            self.initial_msg = None
        
        # Clear previous results
        for widget in self.results_container.winfo_children():
            widget.destroy()
        
        # Create result cards
        self.ssl_card = self._create_card("SSL CERTIFICATE", "Checking...")
        self.dns_card = self._create_card("DNS & IP LOOKUP", "Checking...")
        self.spoof_card = self._create_card("SPOOF ANALYSIS", "Checking...")
        
        # Run checks in thread
        threading.Thread(target=self._run_checks, args=(domain,), daemon=True).start()
    
    def _create_card(self, title, initial_text):
        card = ctk.CTkFrame(self.results_container, fg_color=CARD, border_color=BORDER, border_width=1)
        card.pack(fill="x", pady=(0, 15))
        
        header = ctk.CTkFrame(card, fg_color=SURFACE, height=40)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        ctk.CTkLabel(header, text=title, font=("Courier New", 12, "bold"),
                    text_color=TEXT).pack(side="left", padx=15, pady=10)
        
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", padx=20, pady=15)
        
        status = ctk.CTkLabel(content, text=initial_text, font=("Courier New", 11),
                             text_color=TEXT_MID, justify="left", anchor="w")
        status.pack(fill="x")
        
        return {"frame": card, "content": content, "status": status}
    
    def _run_checks(self, domain):
        results = {"domain": domain, "timestamp": datetime.now().isoformat()}
        
        # SSL Check
        ssl_result = self._check_ssl(domain)
        self.after(0, lambda: self._update_ssl_card(ssl_result))
        results["ssl"] = ssl_result
        
        # DNS Check
        dns_result = self._check_dns(domain)
        self.after(0, lambda: self._update_dns_card(dns_result))
        results["dns"] = dns_result
        
        # Spoof Check
        spoof_result = self._check_spoof(domain)
        self.after(0, lambda: self._update_spoof_card(spoof_result))
        results["spoof"] = spoof_result
        
        # Log to database
        verdict = spoof_result.get("verdict", "UNKNOWN")
        db.log_domain_check(
            domain=domain,
            ssl_valid=ssl_result.get("status", "UNKNOWN"),
            ip_address=dns_result.get("ip", "N/A"),
            spoof_score=spoof_result.get("score", 0),
            verdict=verdict
        )
        
        # Add to history
        self.history.insert(0, {"domain": domain, "verdict": verdict, "results": results})
        if len(self.history) > 10:
            self.history.pop()
        self.after(0, self._update_history)
        
        # Export option
        self.after(0, lambda: self._add_export_button(results))
        
        self.after(0, lambda: self.analyze_btn.configure(state="normal", text="ANALYSE DOMAIN"))
        self.checking = False
    
    def _check_ssl(self, domain):
        try:
            context = ssl.create_default_context()
            with socket.create_connection((domain, 443), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    not_after = datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z")
                    days_remaining = (not_after - datetime.now()).days
                    
                    issuer = dict(x[0] for x in cert["issuer"])
                    
                    return {
                        "status": "VALID",
                        "issuer": issuer.get("organizationName", "Unknown"),
                        "expiry": not_after.strftime("%Y-%m-%d"),
                        "days_remaining": days_remaining
                    }
        except Exception as e:
            return {"status": "INVALID", "error": str(e)}
    
    def _check_dns(self, domain):
        try:
            start = datetime.now()
            ip = socket.gethostbyname(domain)
            response_time = (datetime.now() - start).total_seconds() * 1000
            
            try:
                hostname = socket.gethostbyaddr(ip)
                reverse = hostname[0]
            except:
                reverse = "N/A"
            
            return {
                "ip": ip,
                "reverse": reverse,
                "response_time": f"{response_time:.2f}"
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _check_spoof(self, domain):
        score = 0
        issues = []
        
        # Check against known brands
        domain_lower = domain.lower().replace("www.", "")
        min_distance = 999
        closest_brand = None
        
        for brand in KNOWN_BRANDS:
            dist = self._levenshtein(domain_lower, brand)
            if dist < min_distance:
                min_distance = dist
                closest_brand = brand
        
        if min_distance <= 2 and min_distance > 0:
            score += 40
            issues.append(f"Similar to '{closest_brand}' (distance: {min_distance})")
        
        # Homograph detection
        for char_pair, replacement in HOMOGRAPH_CHARS.items():
            if char_pair in domain_lower:
                score += 15
                issues.append(f"Contains '{char_pair}' (looks like '{replacement}')")
        
        # TLD risk
        for tld in HIGH_RISK_TLDS:
            if domain_lower.endswith(tld):
                score += 30
                issues.append(f"High-risk TLD: {tld}")
        
        # Unicode/IDN
        if any(ord(c) > 127 for c in domain):
            score += 25
            issues.append("Contains non-ASCII characters (IDN)")
        
        # Determine verdict
        if score >= 50:
            verdict = "HIGH RISK"
            color = RED
        elif score >= 25:
            verdict = "SUSPICIOUS"
            color = AMBER
        else:
            verdict = "SAFE"
            color = GREEN
        
        return {
            "score": score,
            "verdict": verdict,
            "color": color,
            "issues": issues,
            "closest_brand": closest_brand,
            "distance": min_distance
        }
    
    def _levenshtein(self, s1, s2):
        if len(s1) < len(s2):
            return self._levenshtein(s2, s1)
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def _update_ssl_card(self, result):
        content = self.ssl_card["content"]
        for widget in content.winfo_children():
            widget.destroy()
        
        if result["status"] == "VALID":
            days = result["days_remaining"]
            if days > 30:
                color = GREEN
                status_text = "✓ Valid Certificate"
            elif days > 0:
                color = AMBER
                status_text = f"⚠ Expiring Soon ({days} days)"
            else:
                color = RED
                status_text = "✗ Expired"
            
            ctk.CTkLabel(content, text=status_text, font=("Courier New", 12, "bold"),
                        text_color=color).pack(anchor="w", pady=(0, 10))
            
            ctk.CTkLabel(content, text=f"Issuer: {result['issuer']}",
                        font=("Courier New", 10), text_color=TEXT_MID).pack(anchor="w", pady=2)
            ctk.CTkLabel(content, text=f"Expires: {result['expiry']}",
                        font=("Courier New", 10), text_color=TEXT_MID).pack(anchor="w", pady=2)
        else:
            ctk.CTkLabel(content, text="✗ Cannot Verify SSL", font=("Courier New", 12, "bold"),
                        text_color=RED).pack(anchor="w", pady=(0, 10))
            ctk.CTkLabel(content, text=result.get("error", "Connection failed"),
                        font=("Courier New", 10), text_color=TEXT_MID, wraplength=500).pack(anchor="w")
    
    def _update_dns_card(self, result):
        content = self.dns_card["content"]
        for widget in content.winfo_children():
            widget.destroy()
        
        if "error" not in result:
            ctk.CTkLabel(content, text="✓ DNS Resolved", font=("Courier New", 12, "bold"),
                        text_color=GREEN).pack(anchor="w", pady=(0, 10))
            
            ctk.CTkLabel(content, text=f"IP Address: {result['ip']}",
                        font=("Courier New", 10), text_color=TEXT_MID).pack(anchor="w", pady=2)
            ctk.CTkLabel(content, text=f"Reverse DNS: {result['reverse']}",
                        font=("Courier New", 10), text_color=TEXT_MID).pack(anchor="w", pady=2)
            ctk.CTkLabel(content, text=f"Response Time: {result['response_time']} ms",
                        font=("Courier New", 10), text_color=TEXT_MID).pack(anchor="w", pady=2)
        else:
            ctk.CTkLabel(content, text="✗ DNS Lookup Failed", font=("Courier New", 12, "bold"),
                        text_color=RED).pack(anchor="w", pady=(0, 10))
            ctk.CTkLabel(content, text=result["error"],
                        font=("Courier New", 10), text_color=TEXT_MID, wraplength=500).pack(anchor="w")
    
    def _update_spoof_card(self, result):
        content = self.spoof_card["content"]
        for widget in content.winfo_children():
            widget.destroy()
        
        verdict_frame = ctk.CTkFrame(content, fg_color=result["color"], corner_radius=4)
        verdict_frame.pack(anchor="w", pady=(0, 15))
        
        ctk.CTkLabel(verdict_frame, text=result["verdict"], font=("Courier New", 12, "bold"),
                    text_color=BG).pack(padx=12, pady=6)
        
        ctk.CTkLabel(content, text=f"Risk Score: {result['score']}/100",
                    font=("Courier New", 11, "bold"), text_color=TEXT).pack(anchor="w", pady=(0, 10))
        
        if result["closest_brand"]:
            ctk.CTkLabel(content, text=f"Closest brand: {result['closest_brand']} (distance: {result['distance']})",
                        font=("Courier New", 10), text_color=TEXT_MID).pack(anchor="w", pady=2)
        
        if result["issues"]:
            ctk.CTkLabel(content, text="Issues detected:", font=("Courier New", 10, "bold"),
                        text_color=TEXT).pack(anchor="w", pady=(10, 5))
            for issue in result["issues"]:
                ctk.CTkLabel(content, text=f"• {issue}", font=("Courier New", 9),
                            text_color=TEXT_MID).pack(anchor="w", pady=1, padx=(10, 0))
    
    def _add_export_button(self, results):
        export_btn = ctk.CTkButton(self.results_container, text="Export as JSON", height=40,
                                   fg_color=CYAN, hover_color="#0096b8", font=("Courier New", 11),
                                   command=lambda: self._export_json(results))
        export_btn.pack(pady=(10, 0))
    
    def _export_json(self, results):
        downloads = os.path.expanduser("~/Downloads")
        filename = f"domain_check_{results['domain']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(downloads, filename)
        
        with open(filepath, "w") as f:
            json.dump(results, f, indent=2)
        
        # Show confirmation
        msg = ctk.CTkToplevel(self)
        msg.title("Export Complete")
        msg.geometry("400x150")
        msg.configure(fg_color=CARD)
        msg.resizable(False, False)
        
        ctk.CTkLabel(msg, text="✓", font=("Courier New", 32), text_color=GREEN).pack(pady=(20, 10))
        ctk.CTkLabel(msg, text=f"Saved to:\n{filepath}", font=("Courier New", 10),
                    text_color=TEXT_MID).pack(pady=(0, 20))
        ctk.CTkButton(msg, text="OK", fg_color=GREEN, command=msg.destroy).pack()
    
    def _update_history(self):
        for widget in self.history_frame.winfo_children():
            widget.destroy()
        
        for item in self.history:
            card = ctk.CTkFrame(self.history_frame, fg_color=INPUT_BG, cursor="hand2")
            card.pack(fill="x", pady=(0, 8))
            
            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="x", padx=10, pady=8)
            
            ctk.CTkLabel(inner, text=item["domain"], font=("Courier New", 10, "bold"),
                        text_color=TEXT, anchor="w").pack(side="left", fill="x", expand=True)
            
            verdict_colors = {"HIGH RISK": RED, "SUSPICIOUS": AMBER, "SAFE": GREEN}
            color = verdict_colors.get(item["verdict"], TEXT_MID)
            
            badge = ctk.CTkFrame(inner, fg_color=color, corner_radius=3)
            badge.pack(side="right")
            ctk.CTkLabel(badge, text=item["verdict"], font=("Courier New", 8),
                        text_color=BG).pack(padx=6, pady=2)
            
            card.bind("<Button-1>", lambda e, d=item["domain"]: self._recheck(d))
    
    def _recheck(self, domain):
        self.domain_entry.delete(0, "end")
        self.domain_entry.insert(0, domain)
        self.analyze_domain()
    
    def clear_history(self):
        self.history.clear()
        self._update_history()

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    root = ctk.CTk()
    root.withdraw()
    app = DomainSpoof(root)
    app.mainloop()
