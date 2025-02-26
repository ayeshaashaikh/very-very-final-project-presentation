# backend/user_management.py

import hashlib

import mysql.connector

# MySQL database connection parameters (adjust as needed)
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',   # Set your MySQL password here
    'database': 'gesture_db'
}

def hash_password(password):
    """Return a SHA-256 hash of the password."""
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password):
    """Register a new user. Returns a tuple (success, message)."""
    hashed = hash_password(password)
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        # Check if username already exists
        query = "SELECT * FROM users WHERE username = %s"
        cursor.execute(query, (username,))
        result = cursor.fetchone()
        if result:
            cursor.close()
            conn.close()
            return False, "Username already exists."
        # Insert new user
        query = "INSERT INTO users (username, password) VALUES (%s, %s)"
        cursor.execute(query, (username, hashed))
        conn.commit()
        cursor.close()
        conn.close()
        return True, "User registered successfully."
    except Exception as e:
        return False, str(e)

def login_user(username, password):
    """Attempt to login a user. Returns a tuple (success, message)."""
    hashed = hash_password(password)
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        query = "SELECT * FROM users WHERE username = %s AND password = %s"
        cursor.execute(query, (username, hashed))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        if result:
            return True, "Login successful."
        else:
            return False, "Invalid username or password."
    except Exception as e:
        return False, str(e)
