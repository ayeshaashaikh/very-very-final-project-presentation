import sys
from tkinter import messagebox

import bcrypt  # For hashing passwords
import customtkinter as ctk
import mysql.connector
from PIL import Image

# Database connection parameters – change these to match your setup!
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = ''
DB_NAME = 'gesture_db'

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        return connection
    except mysql.connector.Error as err:
        print("Database connection error:", err)
        return None

def open_main_window(welcome_window):
    # Import main_control_window (must be in the same folder) and open the main window.
    import main_control_window
    main_control_window.open_main_window(welcome_window)

def login_user(username, password):
    connection = get_db_connection()
    if connection is None:
        return False, "Could not connect to the database."
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()
        if result is None:
            return False, "User not found."
        db_password = result[0]
        # Compare provided password with hashed password in the database
        if bcrypt.checkpw(password.encode('utf-8'), db_password.encode('utf-8')):
            return True, "Logged in successfully."
        else:
            return False, "Incorrect password."
    except mysql.connector.Error as err:
        return False, f"Database error: {err}"
    finally:
        cursor.close()
        connection.close()

def register_user(username, password):
    connection = get_db_connection()
    if connection is None:
        return False, "Could not connect to the database."
    try:
        cursor = connection.cursor()
        # Check if the username already exists
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            return False, "Username already exists."
        # Hash the password using bcrypt
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        # Insert new user into the database (store hashed password)
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s)",
            (username, hashed_password.decode('utf-8'))
        )
        connection.commit()
        return True, "Registered successfully."
    except mysql.connector.Error as err:
        return False, f"Database error: {err}"
    finally:
        cursor.close()
        connection.close()

# Configure CustomTkinter appearance and scaling
ctk.set_appearance_mode("dark")
ctk.set_widget_scaling(1.0)
ctk.set_window_scaling(1.0)

# Define color scheme
BACKGROUND_COLOR = "#000000"
ACCENT_COLOR     = "#d81b60"
HOVER_COLOR      = "#b2184c"
TEXT_COLOR       = "white"

def open_login_window(parent):
    login_window = ctk.CTkToplevel(parent, fg_color=BACKGROUND_COLOR)
    login_window.title("Login")
    login_window.geometry("400x300")

    username_label = ctk.CTkLabel(
        master=login_window,
        text="Username:",
        text_color=TEXT_COLOR,
        font=ctk.CTkFont("Segoe UI", 14),
        bg_color=BACKGROUND_COLOR
    )
    username_label.pack(pady=(20, 5))

    username_entry = ctk.CTkEntry(login_window, font=ctk.CTkFont("Segoe UI", 14), width=300)
    username_entry.pack(pady=5)

    password_label = ctk.CTkLabel(
        master=login_window,
        text="Password:",
        text_color=TEXT_COLOR,
        font=ctk.CTkFont("Segoe UI", 14),
        bg_color=BACKGROUND_COLOR
    )
    password_label.pack(pady=(10, 5))

    password_entry = ctk.CTkEntry(login_window, font=ctk.CTkFont("Segoe UI", 14), width=300, show="*")
    password_entry.pack(pady=5)

    def perform_login():
        username = username_entry.get().strip()
        password = password_entry.get().strip()
        if not username or not password:
            messagebox.showerror("Error", "Both fields are required.", parent=login_window)
            return
        success, msg = login_user(username, password)
        if success:
            messagebox.showinfo("Success", msg, parent=login_window)
            login_window.destroy()  # Close the login window
            open_main_window(parent)
        else:
            messagebox.showerror("Login Failed", msg, parent=login_window)

    login_btn = ctk.CTkButton(
        master=login_window,
        text="Login",
        font=ctk.CTkFont("Segoe UI", 16, "bold"),
        fg_color=ACCENT_COLOR,
        hover_color=HOVER_COLOR,
        command=perform_login
    )
    login_btn.pack(pady=20, ipadx=20, ipady=10)

def open_register_window(parent):
    register_window = ctk.CTkToplevel(parent, fg_color=BACKGROUND_COLOR)
    register_window.title("Register")
    register_window.geometry("400x350")

    username_label = ctk.CTkLabel(
        master=register_window,
        text="Username:",
        text_color=TEXT_COLOR,
        font=ctk.CTkFont("Segoe UI", 14),
        bg_color=BACKGROUND_COLOR
    )
    username_label.pack(pady=(20, 5))

    username_entry = ctk.CTkEntry(register_window, font=ctk.CTkFont("Segoe UI", 14), width=300)
    username_entry.pack(pady=5)

    password_label = ctk.CTkLabel(
        master=register_window,
        text="Password:",
        text_color=TEXT_COLOR,
        font=ctk.CTkFont("Segoe UI", 14),
        bg_color=BACKGROUND_COLOR
    )
    password_label.pack(pady=(10, 5))

    password_entry = ctk.CTkEntry(register_window, font=ctk.CTkFont("Segoe UI", 14), width=300, show="*")
    password_entry.pack(pady=5)

    confirm_label = ctk.CTkLabel(
        master=register_window,
        text="Confirm Password:",
        text_color=TEXT_COLOR,
        font=ctk.CTkFont("Segoe UI", 14),
        bg_color=BACKGROUND_COLOR
    )
    confirm_label.pack(pady=(10, 5))

    confirm_entry = ctk.CTkEntry(register_window, font=ctk.CTkFont("Segoe UI", 14), width=300, show="*")
    confirm_entry.pack(pady=5)

    def perform_registration():
        username = username_entry.get().strip()
        password = password_entry.get().strip()
        confirm = confirm_entry.get().strip()
        if not username or not password or not confirm:
            messagebox.showerror("Error", "All fields are required.", parent=register_window)
            return
        if password != confirm:
            messagebox.showerror("Error", "Passwords do not match.", parent=register_window)
            return
        success, msg = register_user(username, password)
        if success:
            messagebox.showinfo("Success", msg, parent=register_window)
            register_window.destroy()  # Close the register window
            open_main_window(parent)
        else:
            messagebox.showerror("Registration Failed", msg, parent=register_window)

    register_btn = ctk.CTkButton(
        master=register_window,
        text="Register",
        font=ctk.CTkFont("Segoe UI", 16, "bold"),
        fg_color=ACCENT_COLOR,
        hover_color=HOVER_COLOR,
        command=perform_registration
    )
    register_btn.pack(pady=20, ipadx=20, ipady=10)

def show_welcome_window():
    # Create the root window with a pure black background
    root = ctk.CTk(fg_color=BACKGROUND_COLOR)
    root.title("Welcome to AIRSWIPE")
    
    # Maximize window or set full screen dimensions
    if sys.platform.startswith("win"):
        root.state("zoomed")
    else:
        root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}+0+0")

    card_width = 1700
    card_height = 2000
    main_frame = ctk.CTkFrame(
        master=root,
        width=card_width,
        height=card_height,
        fg_color=BACKGROUND_COLOR
    )
    main_frame.place(relx=0.5, rely=0.5, anchor="center")

    try:
        logo_img = Image.open("air.png")
        logo_img = logo_img.resize((200, 150), Image.LANCZOS)
        logo_photo = ctk.CTkImage(logo_img, size=(200, 150))
        logo_label = ctk.CTkLabel(
            master=main_frame,
            image=logo_photo,
            text="",
            fg_color=BACKGROUND_COLOR
        )
        logo_label.image = logo_photo
        logo_label.pack(pady=(40, 20))
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load logo image: {e}")

    header = ctk.CTkLabel(
        master=main_frame,
        text="Welcome to AIRSWIPE",
        text_color=ACCENT_COLOR,
        font=ctk.CTkFont("Segoe UI", 36, "bold"),
        bg_color=BACKGROUND_COLOR
    )
    header.pack(pady=(20, 40))

    button_frame = ctk.CTkFrame(
        master=main_frame,
        fg_color=BACKGROUND_COLOR,
        corner_radius=0,
        border_width=0
    )
    button_frame.pack(pady=20)

    login_button = ctk.CTkButton(
        master=button_frame,
        text="LOGIN",
        font=ctk.CTkFont("Segoe UI", 18, "bold"),
        fg_color=ACCENT_COLOR,
        hover_color=HOVER_COLOR,
        command=lambda: open_login_window(root)
    )
    login_button.pack(pady=10, ipadx=20, ipady=10)

    register_button = ctk.CTkButton(
        master=button_frame,
        text="REGISTER",
        font=ctk.CTkFont("Segoe UI", 18, "bold"),
        fg_color=ACCENT_COLOR,
        hover_color=HOVER_COLOR,
        command=lambda: open_register_window(root)
    )
    register_button.pack(pady=10, ipadx=20, ipady=10)

    root.mainloop()

if __name__ == "__main__":
    show_welcome_window()
