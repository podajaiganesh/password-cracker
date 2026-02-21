"""
social_engineering/email_analyzer.py

Rule-based phishing email analyser.
No ML libraries required — pure Python pattern matching.

Returns a risk score, label, matched reasons, and awareness tips.

FOR EDUCATIONAL / CYBERSECURITY AWARENESS USE ONLY.
"""

import re
from dataclasses import dataclass, field

# ── Detection rule sets ───────────────────────────────────────────────────────

_URGENCY_WORDS = [
    "urgent", "immediately", "asap", "right away", "right now",
    "act now", "action required", "immediate action", "do not delay",
    "final notice", "last chance", "warning", "alert", "critical",
    "expire", "expires", "expiring", "deadline", "time-sensitive",
    "limited time", "24 hours", "48 hours", "today only", "tonight",
]

_THREAT_WORDS = [
    "suspend", "suspended", "suspension", "terminate", "terminated",
    "close", "closed", "closure", "delete", "deleted", "block",
    "blocked", "restrict", "restricted", "locked", "penalty",
    "legal action", "prosecute", "consequence", "permanently",
]

_LURE_WORDS = [
    "verify", "confirm", "validate", "update", "click here", "click now",
    "click the link", "follow the link", "login", "log in", "sign in",
    "enter your", "provide your", "submit your", "fill in", "fill out",
    "your credentials", "your password", "your details", "your information",
    "reset your password", "update your payment", "billing information",
]

_PRIZE_WORDS = [
    "winner", "won", "winning", "congratulations", "prize",
    "reward", "free gift", "gift card", "cash prize", "lottery",
    "selected", "chosen", "lucky", "claim now", "claim your",
]

_FINANCIAL_WORDS = [
    "bank account", "credit card", "debit card", "payment", "invoice",
    "transfer", "wire", "bitcoin", "crypto", "paypal", "your funds",
    "charged", "transaction", "refund", "fee required", "customs fee",
]

_SENSITIVE_REQUEST = [
    "social security", "ssn", "date of birth", "dob", "mother's maiden",
    "account number", "card number", "cvv", "pin number", "bank details",
    "passport number", "driver's licence", "national id",
]

_SUSPICIOUS_DOMAINS = [
    r"http[s]?://(?!www\.(google|microsoft|apple|amazon|paypal|linkedin|gov)\.)[\w\-]+\.(tk|ml|ga|cf|gq|xyz|top|club|online|site|website|info|biz|ru|cn|pw|cc|ws)[\w/\-?=&#%]*",
    r"http[s]?://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}",   # IP-based URL
    r"http[s]?://[\w\-]+\.[\w\-]+\.[\w\-]+\.(com|net|org)/",  # triple subdomain
    r"http[s]?://[\w\-]*(secure|login|verify|account|update|confirm|reset|bank|pay)[\w\-]*\.(com|net|org|io)",
]

_URL_PATTERN = re.compile(r"http[s]?://[^\s<>\"]+", re.IGNORECASE)

# Weights for each category (points added to risk score)
_WEIGHTS = {
    "urgency":           18,
    "threat":            16,
    "lure":              14,
    "prize":             15,
    "financial":         13,
    "sensitive_request": 20,
    "link_present":       8,
    "suspicious_domain": 18,
    "ip_url":            22,
    "generic_greeting":   6,
    "misspelling":        8,
    "all_caps_subject":   7,
    "exclamation":        5,
    "no_plaintext_from":  4,
}

_COMMON_MISSPELLINGS = [
    "recieve", "occured", "occurance", "seperately", "untill",
    "recieved", "definately", "refrence", "adress", "accomodation",
    "inmediately", "verfiy", "verifiy", "suspicous", "acount",
    "pasword", "passord", "compromized", "unauthorised",
]

# ── Result dataclass ──────────────────────────────────────────────────────────

@dataclass
class AnalysisResult:
    risk_score:  int         = 0
    label:       str         = "SAFE"
    reasons:     list        = field(default_factory=list)
    tips:        list        = field(default_factory=list)
    urls_found:  list        = field(default_factory=list)
    word_hits:   dict        = field(default_factory=dict)

    def summary(self) -> dict:
        return {
            "risk_score": self.risk_score,
            "label":      self.label,
            "reasons":    self.reasons,
            "tips":       self.tips,
            "urls_found": self.urls_found,
        }


# ── Core analyser ─────────────────────────────────────────────────────────────

def analyze_email(text: str, subject: str = "") -> AnalysisResult:
    """
    Analyse email text (and optional subject) for phishing indicators.

    Args:
        text:    Full email body text.
        subject: Email subject line (optional, improves accuracy).

    Returns:
        AnalysisResult with score, label, reasons, tips, and matched URLs.
    """
    result    = AnalysisResult()
    full_text = (subject + " " + text).lower()
    score     = 0

    # ── 1. Urgency language ───────────────────────────────────────────────────
    urgency_hits = [w for w in _URGENCY_WORDS if w in full_text]
    if urgency_hits:
        score += _WEIGHTS["urgency"]
        result.reasons.append(
            f"Urgency language detected: {', '.join(urgency_hits[:4])}")
        result.word_hits["urgency"] = urgency_hits[:4]

    # ── 2. Threats & consequences ─────────────────────────────────────────────
    threat_hits = [w for w in _THREAT_WORDS if w in full_text]
    if threat_hits:
        score += _WEIGHTS["threat"]
        result.reasons.append(
            f"Threatening language found: {', '.join(threat_hits[:3])}")
        result.word_hits["threats"] = threat_hits[:3]

    # ── 3. Credential / action lures ──────────────────────────────────────────
    lure_hits = [w for w in _LURE_WORDS if w in full_text]
    if lure_hits:
        score += _WEIGHTS["lure"]
        result.reasons.append(
            f"Credential lure phrases: {', '.join(lure_hits[:3])}")
        result.word_hits["lures"] = lure_hits[:3]

    # ── 4. Prize / lottery bait ───────────────────────────────────────────────
    prize_hits = [w for w in _PRIZE_WORDS if w in full_text]
    if prize_hits:
        score += _WEIGHTS["prize"]
        result.reasons.append(
            f"Prize / lottery bait detected: {', '.join(prize_hits[:3])}")

    # ── 5. Financial references ───────────────────────────────────────────────
    fin_hits = [w for w in _FINANCIAL_WORDS if w in full_text]
    if fin_hits:
        score += _WEIGHTS["financial"]
        result.reasons.append(
            f"Financial references found: {', '.join(fin_hits[:3])}")

    # ── 6. Sensitive information requests ─────────────────────────────────────
    sens_hits = [w for w in _SENSITIVE_REQUEST if w in full_text]
    if sens_hits:
        score += _WEIGHTS["sensitive_request"]
        result.reasons.append(
            f"Requests sensitive information: {', '.join(sens_hits[:2])}")

    # ── 7. URL analysis ───────────────────────────────────────────────────────
    urls = _URL_PATTERN.findall(text)
    result.urls_found = urls

    if urls:
        score += _WEIGHTS["link_present"]
        result.reasons.append(f"{len(urls)} link(s) found in email body")

        for url in urls:
            url_lower = url.lower()

            # IP-based URL
            if re.search(r"http[s]?://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", url_lower):
                score += _WEIGHTS["ip_url"]
                result.reasons.append(f"IP-address URL detected: {url}")
                break

            # Suspicious domain patterns
            for pattern in _SUSPICIOUS_DOMAINS:
                if re.search(pattern, url_lower, re.IGNORECASE):
                    score += _WEIGHTS["suspicious_domain"]
                    result.reasons.append(f"Suspicious domain pattern: {url}")
                    break

    # ── 8. Generic greeting ───────────────────────────────────────────────────
    generic_greetings = ["dear user", "dear customer", "dear account holder",
                         "dear member", "hello user", "valued customer"]
    if any(g in full_text for g in generic_greetings):
        score += _WEIGHTS["generic_greeting"]
        result.reasons.append("Generic greeting used (not personalised)")

    # ── 9. Common misspellings ────────────────────────────────────────────────
    misspell_hits = [w for w in _COMMON_MISSPELLINGS if w in full_text]
    if misspell_hits:
        score += _WEIGHTS["misspelling"]
        result.reasons.append(
            f"Spelling errors detected: {', '.join(misspell_hits[:3])}")

    # ── 10. ALL-CAPS subject ──────────────────────────────────────────────────
    if subject:
        caps_words = [w for w in subject.split()
                      if w.isupper() and len(w) > 2]
        if len(caps_words) >= 2:
            score += _WEIGHTS["all_caps_subject"]
            result.reasons.append(
                "Subject line uses excessive capitalisation (pressure tactic)")

    # ── 11. Excessive exclamation marks ───────────────────────────────────────
    if text.count("!") >= 3:
        score += _WEIGHTS["exclamation"]
        result.reasons.append(
            f"Excessive exclamation marks ({text.count('!')} found) — emotional manipulation")

    # ── Cap score at 100 ──────────────────────────────────────────────────────
    result.risk_score = min(score, 100)

    # ── Label ─────────────────────────────────────────────────────────────────
    if result.risk_score >= 65:
        result.label = "PHISHING"
    elif result.risk_score >= 35:
        result.label = "SUSPICIOUS"
    else:
        result.label = "SAFE"

    # ── Awareness tips ────────────────────────────────────────────────────────
    result.tips = _generate_tips(result)

    return result


def _generate_tips(result: AnalysisResult) -> list[str]:
    tips = []

    if result.label == "PHISHING":
        tips += [
            "🚫  Do NOT click any links in this email.",
            "🔍  Verify the sender's email address independently.",
            "📧  Report this email to your IT / security team.",
            "🗑   Move it to spam and delete without replying.",
            "📞  Contact the organisation directly using a trusted phone number.",
        ]
    elif result.label == "SUSPICIOUS":
        tips += [
            "⚠   Treat this email with caution.",
            "🔍  Verify the sender before taking any action.",
            "🔗  Do not click links — navigate to the site directly via browser.",
            "📞  Confirm the request through an official channel.",
        ]
    else:
        tips += [
            "✅  No major threats detected in this email.",
            "💡  Always remain vigilant — phishing emails can be sophisticated.",
            "🔍  When in doubt, verify the sender's address independently.",
        ]

    if result.urls_found:
        tips.append(
            f"🔗  {len(result.urls_found)} link(s) found — hover before clicking "
            "to check the real destination.")

    if "word_hits" in dir(result) and result.word_hits.get("urgency"):
        tips.append(
            "⏱   Urgency pressure is a common phishing tactic — "
            "slow down and verify before acting.")

    return tips