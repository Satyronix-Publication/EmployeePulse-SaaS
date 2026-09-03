# database.py
# Employee Management SaaS System - Resilient MySQL & SQLite Database Layer

import os
import sqlite3
import datetime
import config

USE_MYSQL = False
db_conn = None

def get_connection():
    """Returns an active database connection (MySQL if available, else SQLite)."""
    global USE_MYSQL, db_conn
    
    # Try MySQL first
    try:
        import mysql.connector
        conn = mysql.connector.connect(
            host=config.MYSQL_HOST,
            user=config.MYSQL_USER,
            password=config.MYSQL_PASSWORD,
            autocommit=True
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {config.MYSQL_DB}")
        cursor.execute(f"USE {config.MYSQL_DB}")
        cursor.close()
        USE_MYSQL = True
        return conn
    except Exception as e:
        # Fall back to SQLite
        USE_MYSQL = False
        db_path = os.path.join(os.path.dirname(__file__), config.SQLITE_DB)
        conn = sqlite3.connect(db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

def execute_query(query, params=(), fetchone=False, fetchall=False, commit=True):
    """
    Executes a query seamlessly converting SQL placeholder formats (%s for MySQL, ? for SQLite).
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        if not USE_MYSQL:
            # Convert %s placeholders to ? for SQLite
            query = query.replace("%s", "?")
            # Convert AUTO_INCREMENT to AUTOINCREMENT for SQLite if creating table
            query = query.replace("AUTO_INCREMENT", "AUTOINCREMENT")
            query = query.replace("INT PRIMARY KEY AUTOINCREMENT", "INTEGER PRIMARY KEY AUTOINCREMENT")
        
        cursor.execute(query, params)
        
        result = None
        if fetchone:
            res = cursor.fetchone()
            if res and not USE_MYSQL:
                result = dict(res)
            elif res and USE_MYSQL:
                # Convert tuple to dict if column names available
                if cursor.description:
                    cols = [col[0] for col in cursor.description]
                    result = dict(zip(cols, res))
                else:
                    result = res
        elif fetchall:
            res = cursor.fetchall()
            if res and not USE_MYSQL:
                result = [dict(r) for r in res]
            elif res and USE_MYSQL:
                if cursor.description:
                    cols = [col[0] for col in cursor.description]
                    result = [dict(zip(cols, r)) for r in res]
                else:
                    result = res
        else:
            if not USE_MYSQL and commit:
                conn.commit()
            result = cursor.lastrowid
            
        return result
    except Exception as err:
        print(f"Database Query Error: {err} | Query: {query}")
        return None
    finally:
        try:
            cursor.close()
            conn.close()
        except:
            pass

def init_database():
    """Initializes schema and seeds demo data."""
    print("Initializing Database Schema...")

    # 1. Users Table
    execute_query("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            role VARCHAR(20) NOT NULL,
            employee_id VARCHAR(20),
            status VARCHAR(20) DEFAULT 'Active'
        );
    """)

    # 2. Departments Table
    execute_query("""
        CREATE TABLE IF NOT EXISTS departments (
            dept_id INTEGER PRIMARY KEY AUTOINCREMENT,
            dept_name VARCHAR(100) NOT NULL,
            hod VARCHAR(100),
            budget DOUBLE DEFAULT 0.0,
            location VARCHAR(100)
        );
    """)

    # 3. Employees Table
    execute_query("""
        CREATE TABLE IF NOT EXISTS employees (
            emp_id VARCHAR(20) PRIMARY KEY,
            first_name VARCHAR(50) NOT NULL,
            last_name VARCHAR(50) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            phone VARCHAR(20),
            dept_id INTEGER,
            designation VARCHAR(50),
            salary DOUBLE DEFAULT 0.0,
            join_date DATE,
            status VARCHAR(20) DEFAULT 'Active'
        );
    """)

    # 4. Payroll Table
    execute_query("""
        CREATE TABLE IF NOT EXISTS payroll (
            pay_id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_id VARCHAR(20) NOT NULL,
            month VARCHAR(20) NOT NULL,
            year INTEGER NOT NULL,
            base_salary DOUBLE DEFAULT 0.0,
            hra DOUBLE DEFAULT 0.0,
            da DOUBLE DEFAULT 0.0,
            pf_deduction DOUBLE DEFAULT 0.0,
            tax_deduction DOUBLE DEFAULT 0.0,
            net_salary DOUBLE DEFAULT 0.0,
            status VARCHAR(20) DEFAULT 'Processed'
        );
    """)

    # 5. Attendance Table
    execute_query("""
        CREATE TABLE IF NOT EXISTS attendance (
            att_id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_id VARCHAR(20) NOT NULL,
            date DATE NOT NULL,
            status VARCHAR(20) NOT NULL,
            check_in VARCHAR(20),
            check_out VARCHAR(20)
        );
    """)

    # 6. Leaves Table
    execute_query("""
        CREATE TABLE IF NOT EXISTS leaves (
            leave_id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_id VARCHAR(20) NOT NULL,
            leave_type VARCHAR(50) NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            days INTEGER NOT NULL,
            reason TEXT,
            status VARCHAR(20) DEFAULT 'Pending',
            applied_on DATE
        );
    """)

    # 7. Performance Table
    execute_query("""
        CREATE TABLE IF NOT EXISTS performance (
            review_id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_id VARCHAR(20) NOT NULL,
            rating DOUBLE DEFAULT 5.0,
            kpi_score DOUBLE DEFAULT 90.0,
            reviewer_feedback TEXT,
            review_date DATE
        );
    """)

    # 8. Shifts Table
    execute_query("""
        CREATE TABLE IF NOT EXISTS shifts (
            shift_id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_id VARCHAR(20) NOT NULL,
            shift_type VARCHAR(50) NOT NULL,
            start_time VARCHAR(20),
            end_time VARCHAR(20),
            assigned_date DATE
        );
    """)

    # 9. Tasks Table
    execute_query("""
        CREATE TABLE IF NOT EXISTS tasks (
            task_id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_id VARCHAR(20) NOT NULL,
            task_title VARCHAR(150) NOT NULL,
            description TEXT,
            priority VARCHAR(20) DEFAULT 'Medium',
            deadline DATE,
            status VARCHAR(20) DEFAULT 'Pending'
        );
    """)

    # 10. Audit Logs Table
    execute_query("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(50) NOT NULL,
            action VARCHAR(255) NOT NULL,
            timestamp VARCHAR(50) NOT NULL
        );
    """)

    # 11. Kudos & Rewards Table
    execute_query("""
        CREATE TABLE IF NOT EXISTS kudos (
            kudo_id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id VARCHAR(20) NOT NULL,
            receiver_id VARCHAR(20) NOT NULL,
            message TEXT NOT NULL,
            points INTEGER DEFAULT 10,
            date DATE NOT NULL
        );
    """)

    # 12. Desk Bookings Table
    execute_query("""
        CREATE TABLE IF NOT EXISTS desk_bookings (
            booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_id VARCHAR(20) NOT NULL,
            desk_id VARCHAR(20) NOT NULL,
            date DATE NOT NULL,
            status VARCHAR(20) DEFAULT 'Booked'
        );
    """)

    seed_default_data()

def seed_default_data():
    """Seeds sample data for testing if database is empty."""
    users_count = execute_query("SELECT COUNT(*) as cnt FROM users", fetchone=True)
    if users_count and (users_count.get('cnt') or users_count.get('COUNT(*)', 0)) > 0:
        return

    print("Seeding initial SaaS demo data...")
    # Default Users
    execute_query("INSERT INTO users (username, password, role, employee_id) VALUES (%s, %s, %s, %s)", ("admin", "admin123", "Admin", "EMP001"))
    execute_query("INSERT INTO users (username, password, role, employee_id) VALUES (%s, %s, %s, %s)", ("hr_manager", "hr123", "HR", "EMP002"))
    execute_query("INSERT INTO users (username, password, role, employee_id) VALUES (%s, %s, %s, %s)", ("emp001", "emp123", "Employee", "EMP003"))

    # Departments
    execute_query("INSERT INTO departments (dept_name, hod, budget, location) VALUES (%s, %s, %s, %s)", ("Engineering", "Alex Rivera", 250000.0, "Floor 4"))
    execute_query("INSERT INTO departments (dept_name, hod, budget, location) VALUES (%s, %s, %s, %s)", ("Human Resources", "Sarah Jenkins", 80000.0, "Floor 2"))
    execute_query("INSERT INTO departments (dept_name, hod, budget, location) VALUES (%s, %s, %s, %s)", ("Sales & Marketing", "David Chen", 150000.0, "Floor 3"))
    execute_query("INSERT INTO departments (dept_name, hod, budget, location) VALUES (%s, %s, %s, %s)", ("Finance", "Elena Rostova", 120000.0, "Floor 2"))

    # Employees
    today = datetime.date.today().strftime("%Y-%m-%d")
    execute_query("""INSERT INTO employees (emp_id, first_name, last_name, email, phone, dept_id, designation, salary, join_date, status) 
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", 
                  ("EMP001", "Alex", "Rivera", "alex.rivera@saas.com", "9876543210", 1, "VP of Engineering", 120000.0, "2022-01-15", "Active"))
    execute_query("""INSERT INTO employees (emp_id, first_name, last_name, email, phone, dept_id, designation, salary, join_date, status) 
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", 
                  ("EMP002", "Sarah", "Jenkins", "sarah.j@saas.com", "9876543211", 2, "HR Director", 95000.0, "2022-03-01", "Active"))
    execute_query("""INSERT INTO employees (emp_id, first_name, last_name, email, phone, dept_id, designation, salary, join_date, status) 
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", 
                  ("EMP003", "Michael", "Chang", "michael.c@saas.com", "9876543212", 1, "Senior Lead Developer", 85000.0, "2023-05-10", "Active"))
    execute_query("""INSERT INTO employees (emp_id, first_name, last_name, email, phone, dept_id, designation, salary, join_date, status) 
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", 
                  ("EMP004", "Emma", "Watson", "emma.w@saas.com", "9876543213", 3, "Account Executive", 70000.0, "2023-08-20", "Active"))

    # Payroll
    execute_query("INSERT INTO payroll (emp_id, month, year, base_salary, hra, da, pf_deduction, tax_deduction, net_salary) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                  ("EMP001", "August", 2026, 120000.0, 24000.0, 12000.0, 14400.0, 18000.0, 123600.0))
    execute_query("INSERT INTO payroll (emp_id, month, year, base_salary, hra, da, pf_deduction, tax_deduction, net_salary) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                  ("EMP002", "August", 2026, 95000.0, 19000.0, 9500.0, 11400.0, 14250.0, 97850.0))

    # Attendance
    execute_query("INSERT INTO attendance (emp_id, date, status, check_in, check_out) VALUES (%s, %s, %s, %s, %s)", ("EMP001", today, "Present", "09:00 AM", "06:00 PM"))
    execute_query("INSERT INTO attendance (emp_id, date, status, check_in, check_out) VALUES (%s, %s, %s, %s, %s)", ("EMP002", today, "Present", "09:15 AM", "06:10 PM"))
    execute_query("INSERT INTO attendance (emp_id, date, status, check_in, check_out) VALUES (%s, %s, %s, %s, %s)", ("EMP003", today, "Late", "09:45 AM", "06:30 PM"))

    # Leaves
    execute_query("INSERT INTO leaves (emp_id, leave_type, start_date, end_date, days, reason, status, applied_on) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                  ("EMP003", "Casual Leave", "2026-09-10", "2026-09-12", 3, "Family function", "Pending", today))

    # Performance
    execute_query("INSERT INTO performance (emp_id, rating, kpi_score, reviewer_feedback, review_date) VALUES (%s, %s, %s, %s, %s)",
                  ("EMP001", 4.9, 98.0, "Exceeded all technical and team goals.", today))

    # Shifts
    execute_query("INSERT INTO shifts (emp_id, shift_type, start_time, end_time, assigned_date) VALUES (%s, %s, %s, %s, %s)",
                  ("EMP001", "General Shift", "09:00 AM", "06:00 PM", today))
    execute_query("INSERT INTO shifts (emp_id, shift_type, start_time, end_time, assigned_date) VALUES (%s, %s, %s, %s, %s)",
                  ("EMP002", "General Shift", "09:00 AM", "06:00 PM", today))

    # Tasks
    execute_query("INSERT INTO tasks (emp_id, task_title, description, priority, deadline, status) VALUES (%s, %s, %s, %s, %s, %s)",
                  ("EMP003", "Upgrade Security Protocols", "Implement JWT token refresh mechanism.", "High", "2026-09-15", "In Progress"))

    # Kudos
    execute_query("INSERT INTO kudos (sender_id, receiver_id, message, points, date) VALUES (%s, %s, %s, %s, %s)",
                  ("EMP001", "EMP003", "Amazing work on the security upgrade! Very fast delivery.", 50, today))
    execute_query("INSERT INTO kudos (sender_id, receiver_id, message, points, date) VALUES (%s, %s, %s, %s, %s)",
                  ("EMP002", "EMP003", "Thanks for helping the HR team with the portal bug.", 20, today))
    execute_query("INSERT INTO kudos (sender_id, receiver_id, message, points, date) VALUES (%s, %s, %s, %s, %s)",
                  ("EMP003", "EMP001", "Great leadership during the sprint planning.", 30, today))
    execute_query("INSERT INTO kudos (sender_id, receiver_id, message, points, date) VALUES (%s, %s, %s, %s, %s)",
                  ("EMP001", "EMP004", "Closed the Q3 enterprise deal perfectly!", 100, today))

    # Desk Bookings
    execute_query("INSERT INTO desk_bookings (emp_id, desk_id, date, status) VALUES (%s, %s, %s, %s)",
                  ("EMP001", "Desk_A1", today, "Booked"))
    execute_query("INSERT INTO desk_bookings (emp_id, desk_id, date, status) VALUES (%s, %s, %s, %s)",
                  ("EMP002", "Desk_B3", today, "Booked"))

    # Audit Logs
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    execute_query("INSERT INTO audit_logs (username, action, timestamp) VALUES (%s, %s, %s)", ("System", "Database initialized & seeded successfully.", now_str))

    print("Demo Data Seeded Successfully!")
