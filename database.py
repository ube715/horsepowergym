"""
Database module for Horsepower Gym Management System
Handles all SQLite database operations
"""

import sqlite3
import os
import sys
from datetime import datetime, date
import hashlib


def get_app_directory():
    """
    Get the directory where the application EXE or main.py is located.
    Database must be stored alongside the .exe, NOT in PyInstaller temp folder.
    """
    if getattr(sys, 'frozen', False):
        # Running as compiled .exe - use the folder containing the .exe
        return os.path.dirname(sys.executable)
    else:
        # Running as script - use the script directory
        return os.path.dirname(os.path.abspath(__file__))


DATABASE_PATH = os.path.join(get_app_directory(), 'horsepower_gym.db')


def get_connection():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Initialize database with all required tables"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Members table with enhanced payment tracking
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL UNIQUE,
            address TEXT,
            age INTEGER,
            gender TEXT,
            membership_type TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            fees REAL NOT NULL,
            payment_status TEXT NOT NULL DEFAULT 'Pending',
            last_payment_date TEXT,
            amount_paid REAL DEFAULT 0,
            pending_amount REAL DEFAULT 0,
            status TEXT DEFAULT 'Active',
            photo_path TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Add new columns to existing members table if they don't exist
    try:
        cursor.execute("ALTER TABLE members ADD COLUMN last_payment_date TEXT")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE members ADD COLUMN amount_paid REAL DEFAULT 0")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE members ADD COLUMN pending_amount REAL DEFAULT 0")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE members ADD COLUMN status TEXT DEFAULT 'Active'")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE members ADD COLUMN photo_path TEXT")
    except:
        pass
    
    # Payments table for tracking all payment transactions
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id INTEGER NOT NULL,
            phone TEXT NOT NULL,
            amount REAL NOT NULL,
            payment_date TEXT NOT NULL,
            payment_type TEXT NOT NULL,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (member_id) REFERENCES members(id) ON DELETE CASCADE
        )
    ''')
    
    # Personal Training table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS personal_training (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id INTEGER NOT NULL,
            trainer_name TEXT NOT NULL,
            plan_duration INTEGER NOT NULL,
            fee REAL NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            status TEXT DEFAULT 'Active',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (member_id) REFERENCES members(id) ON DELETE CASCADE
        )
    ''')
    
    # Attendance table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id INTEGER NOT NULL,
            check_in_time TEXT NOT NULL,
            date TEXT NOT NULL,
            trainer_name TEXT,
            FOREIGN KEY (member_id) REFERENCES members(id) ON DELETE CASCADE
        )
    ''')
    
    # Admin table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create default admin if not exists
    cursor.execute("SELECT COUNT(*) FROM admin")
    if cursor.fetchone()[0] == 0:
        default_password = hashlib.sha256("admin123".encode()).hexdigest()
        cursor.execute("INSERT INTO admin (username, password_hash) VALUES (?, ?)", 
                      ("admin", default_password))
    
    conn.commit()
    conn.close()


# ============ MEMBER OPERATIONS ============

def add_member(name, phone, address, age, gender, membership_type, start_date, end_date, fees, payment_status):
    """Add a new member"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO members (name, phone, address, age, gender, membership_type, 
                           start_date, end_date, fees, payment_status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (name, phone, address, age, gender, membership_type, start_date, end_date, fees, payment_status))
    member_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return member_id


def update_member(member_id, name, phone, address, age, gender, membership_type, 
                  start_date, end_date, fees, payment_status):
    """Update member details"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE members SET name=?, phone=?, address=?, age=?, gender=?, 
               membership_type=?, start_date=?, end_date=?, fees=?, payment_status=?
        WHERE id=?
    ''', (name, phone, address, age, gender, membership_type, start_date, end_date, 
          fees, payment_status, member_id))
    conn.commit()
    conn.close()


def delete_member(member_id):
    """Delete a member"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM members WHERE id=?", (member_id,))
    conn.commit()
    conn.close()


def get_all_members():
    """Get all members"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM members ORDER BY name")
    members = cursor.fetchall()
    conn.close()
    return members


def get_member_by_id(member_id):
    """Get member by ID"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM members WHERE id=?", (member_id,))
    member = cursor.fetchone()
    conn.close()
    return member


def search_members(query):
    """Search members by name or phone"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM members 
        WHERE name LIKE ? OR phone LIKE ?
        ORDER BY name
    ''', (f'%{query}%', f'%{query}%'))
    members = cursor.fetchall()
    conn.close()
    return members


def get_active_members_count():
    """Get count of active members"""
    conn = get_connection()
    cursor = conn.cursor()
    today = date.today().strftime('%Y-%m-%d')
    cursor.execute("SELECT COUNT(*) FROM members WHERE end_date >= ?", (today,))
    count = cursor.fetchone()[0]
    conn.close()
    return count


def get_expired_members_count():
    """Get count of expired members"""
    conn = get_connection()
    cursor = conn.cursor()
    today = date.today().strftime('%Y-%m-%d')
    cursor.execute("SELECT COUNT(*) FROM members WHERE end_date < ?", (today,))
    count = cursor.fetchone()[0]
    conn.close()
    return count


def get_total_members_count():
    """Get total members count"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM members")
    count = cursor.fetchone()[0]
    conn.close()
    return count


# ============ PERSONAL TRAINING OPERATIONS ============

def add_personal_training(member_id, trainer_name, plan_duration, fee, start_date, end_date):
    """Add personal training for a member"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO personal_training (member_id, trainer_name, plan_duration, fee, start_date, end_date)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (member_id, trainer_name, plan_duration, fee, start_date, end_date))
    training_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return training_id


def update_personal_training(training_id, trainer_name, plan_duration, fee, start_date, end_date, status):
    """Update personal training details"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE personal_training 
        SET trainer_name=?, plan_duration=?, fee=?, start_date=?, end_date=?, status=?
        WHERE id=?
    ''', (trainer_name, plan_duration, fee, start_date, end_date, status, training_id))
    conn.commit()
    conn.close()


def delete_personal_training(training_id):
    """Delete personal training record"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM personal_training WHERE id=?", (training_id,))
    conn.commit()
    conn.close()


def get_member_training(member_id):
    """Get personal training for a member"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM personal_training WHERE member_id=? ORDER BY start_date DESC
    ''', (member_id,))
    training = cursor.fetchall()
    conn.close()
    return training


def get_active_training(member_id):
    """Get active personal training for a member"""
    conn = get_connection()
    cursor = conn.cursor()
    today = date.today().strftime('%Y-%m-%d')
    cursor.execute('''
        SELECT * FROM personal_training 
        WHERE member_id=? AND end_date >= ? AND status='Active'
        ORDER BY end_date DESC LIMIT 1
    ''', (member_id, today))
    training = cursor.fetchone()
    conn.close()
    return training


def get_all_training():
    """Get all personal training records with member names"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT pt.*, m.name as member_name, m.phone as member_phone
        FROM personal_training pt
        JOIN members m ON pt.member_id = m.id
        ORDER BY pt.end_date DESC
    ''')
    training = cursor.fetchall()
    conn.close()
    return training


# ============ ATTENDANCE OPERATIONS ============

def add_attendance(member_id, trainer_name=None):
    """Add attendance record"""
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now()
    cursor.execute('''
        INSERT INTO attendance (member_id, check_in_time, date, trainer_name)
        VALUES (?, ?, ?, ?)
    ''', (member_id, now.strftime('%H:%M:%S'), now.strftime('%Y-%m-%d'), trainer_name))
    conn.commit()
    conn.close()


def get_today_attendance():
    """Get today's attendance"""
    conn = get_connection()
    cursor = conn.cursor()
    today = date.today().strftime('%Y-%m-%d')
    cursor.execute('''
        SELECT a.*, m.name as member_name, m.phone as member_phone
        FROM attendance a
        JOIN members m ON a.member_id = m.id
        WHERE a.date = ?
        ORDER BY a.check_in_time DESC
    ''', (today,))
    attendance = cursor.fetchall()
    conn.close()
    return attendance


def get_member_attendance(member_id):
    """Get attendance history for a member"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM attendance WHERE member_id=? ORDER BY date DESC, check_in_time DESC
    ''', (member_id,))
    attendance = cursor.fetchall()
    conn.close()
    return attendance


def get_attendance_by_trainer(trainer_name):
    """Get attendance by trainer"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT a.*, m.name as member_name
        FROM attendance a
        JOIN members m ON a.member_id = m.id
        WHERE a.trainer_name = ?
        ORDER BY a.date DESC, a.check_in_time DESC
    ''', (trainer_name,))
    attendance = cursor.fetchall()
    conn.close()
    return attendance


def get_today_attendance_count():
    """Get today's attendance count"""
    conn = get_connection()
    cursor = conn.cursor()
    today = date.today().strftime('%Y-%m-%d')
    cursor.execute("SELECT COUNT(*) FROM attendance WHERE date=?", (today,))
    count = cursor.fetchone()[0]
    conn.close()
    return count


def check_already_checked_in(member_id):
    """Check if member already checked in today"""
    conn = get_connection()
    cursor = conn.cursor()
    today = date.today().strftime('%Y-%m-%d')
    cursor.execute("SELECT COUNT(*) FROM attendance WHERE member_id=? AND date=?", (member_id, today))
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0


# ============ REVENUE OPERATIONS ============

def get_monthly_revenue():
    """Get current month's revenue from membership fees"""
    conn = get_connection()
    cursor = conn.cursor()
    first_day = date.today().replace(day=1).strftime('%Y-%m-%d')
    cursor.execute('''
        SELECT COALESCE(SUM(fees), 0) FROM members 
        WHERE payment_status='Paid' AND start_date >= ?
    ''', (first_day,))
    membership_revenue = cursor.fetchone()[0]
    
    cursor.execute('''
        SELECT COALESCE(SUM(fee), 0) FROM personal_training 
        WHERE start_date >= ?
    ''', (first_day,))
    training_revenue = cursor.fetchone()[0]
    
    conn.close()
    return membership_revenue + training_revenue


# ============ ADMIN OPERATIONS ============

def verify_admin(username, password):
    """Verify admin credentials"""
    conn = get_connection()
    cursor = conn.cursor()
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute("SELECT * FROM admin WHERE username=? AND password_hash=?", 
                  (username, password_hash))
    admin = cursor.fetchone()
    conn.close()
    return admin is not None


def change_admin_password(username, new_password):
    """Change admin password"""
    conn = get_connection()
    cursor = conn.cursor()
    password_hash = hashlib.sha256(new_password.encode()).hexdigest()
    cursor.execute("UPDATE admin SET password_hash=? WHERE username=?", 
                  (password_hash, username))
    conn.commit()
    conn.close()


# Initialize database on import
init_database()


# ============ PHONE VERIFICATION OPERATIONS ============

def get_member_by_phone(phone):
    """Get member by phone number - PRIMARY verification method"""
    conn = get_connection()
    cursor = conn.cursor()
    phone = phone.strip().replace(" ", "").replace("-", "")
    cursor.execute("SELECT * FROM members WHERE phone=?", (phone,))
    member = cursor.fetchone()
    conn.close()
    return member


def check_phone_exists(phone, exclude_member_id=None):
    """Check if phone number already exists (for uniqueness validation)"""
    conn = get_connection()
    cursor = conn.cursor()
    phone = phone.strip().replace(" ", "").replace("-", "")
    if exclude_member_id:
        cursor.execute("SELECT COUNT(*) FROM members WHERE phone=? AND id!=?", (phone, exclude_member_id))
    else:
        cursor.execute("SELECT COUNT(*) FROM members WHERE phone=?", (phone,))
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0


def get_member_fee_details(phone):
    """Get complete fee details for a member by phone"""
    conn = get_connection()
    cursor = conn.cursor()
    phone = phone.strip().replace(" ", "").replace("-", "")
    cursor.execute('''
        SELECT m.*, 
               (SELECT pt.trainer_name FROM personal_training pt 
                WHERE pt.member_id = m.id AND pt.status = 'Active' 
                AND pt.end_date >= date('now') LIMIT 1) as current_trainer,
               (SELECT pt.fee FROM personal_training pt 
                WHERE pt.member_id = m.id AND pt.status = 'Active' 
                AND pt.end_date >= date('now') LIMIT 1) as pt_fee,
               (SELECT pt.end_date FROM personal_training pt 
                WHERE pt.member_id = m.id AND pt.status = 'Active' 
                AND pt.end_date >= date('now') LIMIT 1) as pt_end_date
        FROM members m WHERE m.phone=?
    ''', (phone,))
    member = cursor.fetchone()
    conn.close()
    return member


def update_member_status():
    """Update membership status based on end_date (Active/Expired)"""
    conn = get_connection()
    cursor = conn.cursor()
    today = date.today().strftime('%Y-%m-%d')
    cursor.execute("UPDATE members SET status='Expired' WHERE end_date < ?", (today,))
    cursor.execute("UPDATE members SET status='Active' WHERE end_date >= ?", (today,))
    conn.commit()
    conn.close()


# ============ PAYMENT OPERATIONS ============

def add_payment(member_id, phone, amount, payment_type, notes=""):
    """Add a payment record"""
    conn = get_connection()
    cursor = conn.cursor()
    today = date.today().strftime('%Y-%m-%d')
    cursor.execute('''
        INSERT INTO payments (member_id, phone, amount, payment_date, payment_type, notes)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (member_id, phone, amount, today, payment_type, notes))
    payment_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return payment_id


def update_member_payment(member_id, amount_paid, pending_amount, new_end_date=None):
    """Update member's payment information after payment"""
    conn = get_connection()
    cursor = conn.cursor()
    today = date.today().strftime('%Y-%m-%d')
    
    if new_end_date:
        cursor.execute('''
            UPDATE members SET 
                amount_paid = amount_paid + ?,
                pending_amount = ?,
                last_payment_date = ?,
                payment_status = 'Paid',
                end_date = ?,
                status = 'Active'
            WHERE id = ?
        ''', (amount_paid, pending_amount, today, new_end_date, member_id))
    else:
        cursor.execute('''
            UPDATE members SET 
                amount_paid = amount_paid + ?,
                pending_amount = ?,
                last_payment_date = ?,
                payment_status = CASE WHEN ? = 0 THEN 'Paid' ELSE 'Pending' END
            WHERE id = ?
        ''', (amount_paid, pending_amount, today, pending_amount, member_id))
    
    conn.commit()
    conn.close()


def get_member_payments(member_id):
    """Get all payments for a member"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM payments WHERE member_id=? ORDER BY payment_date DESC
    ''', (member_id,))
    payments = cursor.fetchall()
    conn.close()
    return payments


def get_all_payments():
    """Get all payment records with member names"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT p.*, m.name as member_name 
        FROM payments p
        JOIN members m ON p.member_id = m.id
        ORDER BY p.payment_date DESC, p.created_at DESC
    ''')
    payments = cursor.fetchall()
    conn.close()
    return payments


def get_pending_payments():
    """Get members with pending payments"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM members 
        WHERE payment_status = 'Pending' OR pending_amount > 0
        ORDER BY name
    ''')
    members = cursor.fetchall()
    conn.close()
    return members


def get_today_collections():
    """Get total collections for today"""
    conn = get_connection()
    cursor = conn.cursor()
    today = date.today().strftime('%Y-%m-%d')
    cursor.execute('''
        SELECT COALESCE(SUM(amount), 0) FROM payments WHERE payment_date = ?
    ''', (today,))
    total = cursor.fetchone()[0]
    conn.close()
    return total


def get_monthly_collections():
    """Get total collections for current month"""
    conn = get_connection()
    cursor = conn.cursor()
    first_day = date.today().replace(day=1).strftime('%Y-%m-%d')
    cursor.execute('''
        SELECT COALESCE(SUM(amount), 0) FROM payments WHERE payment_date >= ?
    ''', (first_day,))
    total = cursor.fetchone()[0]
    conn.close()
    return total


def update_member_photo(member_id, photo_path):
    """Update member's photo path"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE members SET photo_path = ? WHERE id = ?', (photo_path, member_id))
    conn.commit()
    conn.close()


def get_member_photo(member_id):
    """Get member's photo path"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT photo_path FROM members WHERE id = ?', (member_id,))
    result = cursor.fetchone()
    conn.close()
    return result['photo_path'] if result else None
