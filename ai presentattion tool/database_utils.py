import json

import mysql.connector


# Function to get database connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",        # MySQL host
        user="root",             # Default user in XAMPP
        password="",             # No password by default (unless you've set one in XAMPP)
        database="gesture_db"    # Your database name
    )

# Create the gestures table (if it doesn't exist)
def create_gestures_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gestures (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            gesture_data JSON NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    conn.commit()
    cursor.close()
    conn.close()

# Save custom gesture to MySQL database
def save_custom_gesture_to_db(name, gesture_data):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO gestures (name, gesture_data)
        VALUES (%s, %s)
    ''', (name, json.dumps(gesture_data)))  # Store the gesture data as JSON
    conn.commit()
    cursor.close()
    conn.close()

# Retrieve all gestures from the database
def get_all_gestures():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM gestures')
    gestures = cursor.fetchall()
    cursor.close()
    conn.close()
    return gestures

# Retrieve a specific gesture by name
def get_gesture_by_name(name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM gestures WHERE name = %s', (name,))
    gesture = cursor.fetchone()
    cursor.close()
    conn.close()
    return gesture
