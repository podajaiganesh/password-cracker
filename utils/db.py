import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "securenetra.db")

def get_connection():
    """Returns a connection to the securenetra database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Creates all required tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Attacks table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attacks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            mode TEXT,
            algorithm TEXT,
            hash_value TEXT,
            result TEXT,
            attempts INTEGER,
            time_taken REAL,
            speed REAL,
            cracked_password TEXT
        )
    """)
    
    # Phishing checks table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS phishing_checks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            message_type TEXT,
            risk_score INTEGER,
            label TEXT,
            reasons TEXT,
            sender TEXT,
            subject TEXT
        )
    """)
    
    # Domain checks table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS domain_checks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            domain TEXT,
            ssl_valid TEXT,
            ip_address TEXT,
            spoof_score INTEGER,
            verdict TEXT
        )
    """)
    
    # Quiz results table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS quiz_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            score INTEGER,
            total INTEGER,
            percentage REAL,
            weak_areas TEXT
        )
    """)
    
    # Users table for authentication
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL,
            is_verified INTEGER DEFAULT 0,
            otp_code TEXT,
            otp_expiry TEXT
        )
    """)
    
    conn.commit()
    conn.close()

def log_attack(mode, algorithm, hash_value, result, attempts, time_taken, speed, cracked_password=None):
    """Log an attack result to the database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO attacks (timestamp, mode, algorithm, hash_value, result, attempts, time_taken, speed, cracked_password)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (datetime.now().isoformat(), mode, algorithm, hash_value, result, attempts, time_taken, speed, cracked_password))
    conn.commit()
    conn.close()

def log_phishing_check(message_type, risk_score, label, reasons, sender, subject):
    """Log a phishing check to the database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO phishing_checks (timestamp, message_type, risk_score, label, reasons, sender, subject)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (datetime.now().isoformat(), message_type, risk_score, label, reasons, sender, subject))
    conn.commit()
    conn.close()

def log_domain_check(domain, ssl_valid, ip_address, spoof_score, verdict):
    """Log a domain check to the database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO domain_checks (timestamp, domain, ssl_valid, ip_address, spoof_score, verdict)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (datetime.now().isoformat(), domain, ssl_valid, ip_address, spoof_score, verdict))
    conn.commit()
    conn.close()

def log_quiz_result(score, total, percentage, weak_areas):
    """Log a quiz result to the database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO quiz_results (timestamp, score, total, percentage, weak_areas)
        VALUES (?, ?, ?, ?, ?)
    """, (datetime.now().isoformat(), score, total, percentage, weak_areas))
    conn.commit()
    conn.close()
