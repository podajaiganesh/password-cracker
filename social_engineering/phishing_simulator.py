"""
social_engineering/phishing_simulator.py

Generates realistic phishing email simulations for TRAINING purposes only.
No real emails are sent. All output is local and fictional.

FOR EDUCATIONAL / CYBERSECURITY AWARENESS USE ONLY.
"""

import random
import datetime

# ── Scenario templates ────────────────────────────────────────────────────────
# Each scenario has subject variants, opener variants, body blocks, and CTAs.

_SCENARIOS = {

    "Bank Alert": {
        "subjects": [
            "URGENT: Suspicious Activity Detected on Your Account",
            "Action Required: Your Account Has Been Temporarily Suspended",
            "Security Alert: Unauthorized Login Attempt",
            "IMPORTANT: Verify Your Banking Details Immediately",
            "Your Account Will Be Closed — Immediate Action Needed",
        ],
        "openers": [
            "We have detected unusual activity on your account.",
            "Our security systems flagged a suspicious login attempt on your account.",
            "Your account has been temporarily restricted due to multiple failed login attempts.",
            "A transaction of $1,249.00 was initiated from an unrecognized device.",
        ],
        "bodies": [
            "To protect your funds, we have placed a temporary hold on your account. "
            "You must verify your identity within 24 hours to restore full access.",
            "Our fraud detection system has identified potentially unauthorized access. "
            "Failure to verify within 24 hours will result in permanent account suspension.",
            "We require immediate verification of your personal details to continue "
            "providing you with uninterrupted banking services.",
        ],
        "ctas": [
            "Click here to verify your account: http://secure-bank-verify.example.com/login",
            "Restore your account immediately: http://bank-account-restore.example.com",
            "Confirm your identity now: http://banking-secure-portal.example.com/verify",
        ],
        "traits": [
            "Your account number: ****{acct}",
            "Reference ID: TXN-{ref}",
            "Transaction flagged: ${amount} on {date}",
        ],
    },

    "Password Reset": {
        "subjects": [
            "Password Reset Required — Your Account Is at Risk",
            "Action Required: Reset Your Password Immediately",
            "Your Password Has Expired — Update Now to Avoid Lockout",
            "Security Notice: Unusual Password Activity Detected",
            "FINAL NOTICE: Update Your Password Before Midnight Tonight",
        ],
        "openers": [
            "Our system has detected that your password has been compromised.",
            "Your current password no longer meets our updated security requirements.",
            "We detected your credentials in a recent data breach. Immediate action is required.",
            "Your account password has not been changed in over 90 days and has now expired.",
        ],
        "bodies": [
            "To maintain the security of your account, you must reset your password "
            "immediately. Accounts that are not updated within 24 hours will be locked.",
            "We have temporarily restricted access to your account. Reset your password "
            "now to regain full access and protect your data.",
            "Our records show your password was recently exposed. Secure your account by "
            "creating a new strong password through our verification portal.",
        ],
        "ctas": [
            "Reset your password now: http://account-password-reset.example.com",
            "Click to secure your account: http://secure-reset-portal.example.com/reset",
            "Update your credentials here: http://password-update.example.com/verify",
        ],
        "traits": [
            "Account: {name}@company.com",
            "Last login: {date}",
            "Reset token expires in: 2 hours",
        ],
    },

    "Prize Win": {
        "subjects": [
            "Congratulations! You Have Been Selected as Our Lucky Winner!",
            "WINNER ALERT: You Have Won $5,000 — Claim Now!",
            "You Are Our Grand Prize Winner — Unclaimed Reward Inside",
            "Your Name Was Selected in Our Monthly Draw — Claim Your Prize",
            "LAST CHANCE: Claim Your $10,000 Reward Before It Expires!",
        ],
        "openers": [
            "Congratulations! Your email address was randomly selected as our grand prize winner.",
            "We are thrilled to inform you that you have won our exclusive monthly giveaway!",
            "Your account has been identified as the winner of our annual customer appreciation draw.",
            "You have been selected to receive an exclusive reward worth $5,000!",
        ],
        "bodies": [
            "You have won a cash prize of $5,000. To claim your reward, you must verify "
            "your identity and provide your delivery details within 48 hours.",
            "Your unclaimed prize of $10,000 is waiting. Winners who do not claim within "
            "72 hours will forfeit their reward. Act now to secure your winnings.",
            "As our valued customer, you have been awarded an exclusive prize package. "
            "Complete your claim form now — this offer expires at midnight tonight.",
        ],
        "ctas": [
            "Claim your prize here: http://prize-claim-winner.example.com",
            "Click to receive your reward: http://exclusive-winner-portal.example.com/claim",
            "Verify and collect now: http://grand-prize-winner.example.com/verify",
        ],
        "traits": [
            "Prize amount: ${amount}",
            "Winner ID: WIN-{ref}",
            "Claim deadline: {deadline}",
        ],
    },

    "Job Offer": {
        "subjects": [
            "Exclusive Remote Job Opportunity — $5,000/Week — Apply Now",
            "You Have Been Shortlisted for a High-Paying Remote Position",
            "Urgent Hiring: Work From Home — No Experience Needed",
            "Your LinkedIn Profile Caught Our Attention — Job Offer Inside",
            "Special Recruitment: Earn Up to $8,000/Month From Home",
        ],
        "openers": [
            "We came across your profile and believe you are an excellent candidate for our position.",
            "Our recruitment team has shortlisted you for an exclusive remote work opportunity.",
            "Based on your background, we would like to offer you a position at our company.",
            "We are urgently hiring for a remote role that matches your skill set perfectly.",
        ],
        "bodies": [
            "This is a fully remote position offering $5,000 per week with flexible hours. "
            "No prior experience is required. Training is provided. Apply within 24 hours "
            "as only a limited number of positions are available.",
            "We are expanding our team and need motivated individuals immediately. "
            "This role pays $8,000/month and requires only a few hours daily. "
            "Complete your application today to secure your position.",
            "Your skills align perfectly with our requirements. This offer includes a "
            "signing bonus and full benefits. Positions fill quickly — apply now.",
        ],
        "ctas": [
            "Apply for this position: http://job-offer-apply.example.com",
            "Submit your application now: http://remote-jobs-portal.example.com/apply",
            "Secure your spot here: http://career-opportunity.example.com/register",
        ],
        "traits": [
            "Position: Remote Data Entry Specialist",
            "Salary: ${amount}/week",
            "Application deadline: {deadline}",
        ],
    },

    "IT Support": {
        "subjects": [
            "IT Security Alert: Your Device Has Been Compromised",
            "Action Required: Critical Security Update for Your Account",
            "Mandatory: Update Your VPN Credentials Before Tomorrow",
            "IT Department: Your System Access Will Be Revoked in 24 Hours",
            "URGENT: Malware Detected on Your Company Device",
        ],
        "openers": [
            "This is an automated alert from the IT Security Department.",
            "Our monitoring systems have detected a security issue with your account.",
            "The IT team has identified a critical vulnerability affecting your system.",
            "Your corporate credentials are scheduled to expire and require immediate renewal.",
        ],
        "bodies": [
            "A mandatory security patch must be applied to your account within 24 hours. "
            "Failure to comply will result in automatic account suspension as per company policy.",
            "Our endpoint protection system has flagged unusual activity on your device. "
            "Please verify your credentials immediately to prevent data loss.",
            "All employees must update their VPN access credentials by end of business today. "
            "Non-compliance may result in temporary loss of remote access privileges.",
        ],
        "ctas": [
            "Update credentials now: http://it-secure-portal.example.com/update",
            "Apply security patch: http://company-it-support.example.com/patch",
            "Verify your account: http://internal-security.example.com/verify",
        ],
        "traits": [
            "Ticket ID: INC-{ref}",
            "System flagged: {date} at {time}",
            "Required action by: {deadline}",
        ],
    },
}

# ── Urgency modifiers ─────────────────────────────────────────────────────────

_URGENCY_OPENERS = {
    "Low": [
        "Please take a moment to",
        "When you have a chance,",
        "We kindly request that you",
        "We would appreciate it if you could",
    ],
    "Medium": [
        "Please act soon to",
        "We strongly encourage you to",
        "Time-sensitive: please",
        "This requires your prompt attention to",
    ],
    "High": [
        "IMMEDIATE ACTION REQUIRED:",
        "WARNING — You must",
        "CRITICAL ALERT: You must immediately",
        "FINAL NOTICE — Failure to act will result in permanent consequences unless you",
    ],
}

_URGENCY_CLOSINGS = {
    "Low":    "Thank you for your cooperation. We appreciate your attention to this matter.",
    "Medium": "Please do not delay. Timely action is required to avoid any inconvenience.",
    "High":   "DO NOT IGNORE THIS MESSAGE. Failure to act within 24 hours will result "
              "in PERMANENT account closure. This is your FINAL warning.",
}

_SIGN_OFFS = [
    "Security Team", "Account Services", "Customer Support",
    "IT Department", "Fraud Prevention Unit", "Compliance Team",
    "Automated Security System", "Account Protection Division",
]

# ── Phishing traits (educational annotation) ─────────────────────────────────

_PHISHING_TRAIT_LABELS = [
    "⚠  Urgency pressure tactic",
    "⚠  Suspicious link (not a real domain)",
    "⚠  Threatens negative consequences",
    "⚠  Requests sensitive information",
    "⚠  Generic greeting (not personalised)",
    "⚠  Short deadline to force quick action",
    "⚠  Unsolicited contact",
    "⚠  Emotional manipulation",
]


def _rand(lst: list) -> str:
    return random.choice(lst)


def _fake_ref() -> str:
    return str(random.randint(100000, 999999))


def _fake_amount() -> str:
    return str(random.choice([499, 999, 1249, 2500, 5000, 10000]))


def _fake_date() -> str:
    d = datetime.date.today()
    return d.strftime("%d %B %Y")


def _fake_deadline() -> str:
    d = datetime.date.today() + datetime.timedelta(hours=random.choice([24, 48, 72]))
    return d.strftime("%d %B %Y %H:%M")


def _fake_time() -> str:
    h = random.randint(0, 23)
    m = random.randint(0, 59)
    return f"{h:02d}:{m:02d} UTC"


def generate_phishing_email(
    target_name: str,
    scenario: str,
    urgency: str,
) -> dict:
    """
    Generate a simulated phishing email for training purposes.

    Args:
        target_name: Recipient name (e.g. "Employee" or "John").
        scenario:    One of the keys in _SCENARIOS.
        urgency:     "Low" | "Medium" | "High"

    Returns:
        dict with keys:
            subject      – email subject line
            body         – full email body text
            traits       – list of phishing trait annotations
            scenario     – echo of the input scenario
            urgency      – echo of the input urgency
            disclaimer   – mandatory simulation notice
    """
    if scenario not in _SCENARIOS:
        scenario = "Bank Alert"
    if urgency not in _URGENCY_OPENERS:
        urgency = "Medium"

    tmpl   = _SCENARIOS[scenario]
    name   = target_name.strip() or "User"

    subject = _rand(tmpl["subjects"])
    opener  = _rand(tmpl["openers"])
    body    = _rand(tmpl["bodies"])
    cta     = _rand(tmpl["ctas"])
    closing = _URGENCY_CLOSINGS[urgency]
    urg_pfx = _rand(_URGENCY_OPENERS[urgency])
    signoff = _rand(_SIGN_OFFS)

    # Fill trait placeholders
    raw_trait = _rand(tmpl["traits"])
    trait_line = (raw_trait
                  .replace("{name}",     name)
                  .replace("{acct}",     str(random.randint(1000, 9999)))
                  .replace("{ref}",      _fake_ref())
                  .replace("{amount}",   _fake_amount())
                  .replace("{date}",     _fake_date())
                  .replace("{time}",     _fake_time())
                  .replace("{deadline}", _fake_deadline()))

    body_text = (
        f"Dear {name},\n\n"
        f"{opener}\n\n"
        f"{urg_pfx} {body}\n\n"
        f"{trait_line}\n\n"
        f"{cta}\n\n"
        f"{closing}\n\n"
        f"Regards,\n"
        f"{signoff}\n"
        f"security-noreply@example.com"
    )

    # Select a random subset of phishing traits to annotate
    num_traits = {"Low": 3, "Medium": 4, "High": 5}[urgency]
    traits = random.sample(_PHISHING_TRAIT_LABELS, num_traits)

    disclaimer = (
        "\n" + "─" * 60 + "\n"
        "⚠  SIMULATION NOTICE\n"
        "This email is a SIMULATED phishing example generated\n"
        "for cybersecurity awareness training ONLY.\n"
        "No real email was sent. No real link is functional.\n"
        "─" * 60
    )

    return {
        "subject":    subject,
        "body":       body_text,
        "traits":     traits,
        "scenario":   scenario,
        "urgency":    urgency,
        "disclaimer": disclaimer,
    }


def get_scenarios() -> list[str]:
    return list(_SCENARIOS.keys())


def get_urgency_levels() -> list[str]:
    return ["Low", "Medium", "High"]