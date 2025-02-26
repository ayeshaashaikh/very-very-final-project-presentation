import tkinter as tk
from tkinter import ttk

from main_control_window import open_main_window
from PIL import Image, ImageTk
from ttkthemes import ThemedTk

import database


def show_login_window(welcome_window):
    # Initialize the themed login window
    login_window = ThemedTk()
    login_window.title("Login to AIRSWIPE")
    login_window.geometry("600x400")
    login_window.resizable(True, True)

    # Set the theme
    login_window.set_theme("arc")

    # Create a canvas for background image
    canvas = tk.Canvas(login_window, highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    # Load background image
    try:
        bg_image = Image.open("./IMG/bgpr1.jpeg")

        # Function to update background image on resize
        def update_background(event):
            resized_bg_image = bg_image.resize((event.width, event.height), Image.LANCZOS)
            resized_bg_image_tk = ImageTk.PhotoImage(resized_bg_image)
            canvas.delete("bg_image")
            canvas.create_image(0, 0, anchor="nw", image=resized_bg_image_tk, tags="bg_image")
            canvas.image = resized_bg_image_tk

        # Bind the resize event
        canvas.bind("<Configure>", update_background)

        # Initial drawing of the background using the initial size
        bg_image_resized = bg_image.resize((600, 400), Image.LANCZOS)
        bg_image_tk = ImageTk.PhotoImage(bg_image_resized)
        canvas.create_image(0, 0, anchor="nw", image=bg_image_tk, tags="bg_image")
        canvas.image = bg_image_tk

    except Exception as e:
        print(f"Error loading background image: {e}")

    # Main frame for login form (increased height)
    frame = tk.Frame(login_window, bg="#1e1e2f", bd=2, relief="groove")
    frame.place(relx=0.5, rely=0.5, anchor="center", width=450, height=350)  # Increased height

    # Username Label and Entry
    username_label = tk.Label(frame, text="Username:", font=("Helvetica", 12), fg="white", bg="#1e1e2f")
    username_label.pack(pady=(20, 5))
    username_entry = tk.Entry(frame, font=("Helvetica", 12))
    username_entry.pack(pady=(0, 10))

    # Password Label and Entry
    password_label = tk.Label(frame, text="Password:", font=("Helvetica", 12), fg="white", bg="#1e1e2f")
    password_label.pack(pady=(10, 5))
    password_entry = tk.Entry(frame, show="*", font=("Helvetica", 12))
    password_entry.pack(pady=(0, 20))

    # Login Button
    login_button = tk.Button(
        frame, text="Login", font=("Helvetica", 14, "bold"),
        command=lambda: login(username_entry.get(), password_entry.get(), login_window),
        bg="#0C4C58", fg="white", activebackground="#0C4C58", activeforeground="white",
        relief="flat", padx=10, pady=5
    )
    login_button.pack(pady=(10, 5))

    # Register option
    register_label = tk.Label(frame, text="Don't have an account? Register here.", font=("Helvetica", 10), fg="white", bg="#1e1e2f")
    register_label.pack(pady=(10, 5))
    
    # Register Button (increased padding)
    register_button = tk.Button(
        frame, text="Register", font=("Helvetica", 12, "bold"),
        command=lambda: show_registration_window(login_window),
        bg="#0C4C58", fg="white", activebackground="#0C4C58", activeforeground="white",
        relief="flat", padx=20, pady=10  # Increased pady for more space
    )
    register_button.pack(pady=(5, 20))  # Increased padding below button

    # Run the Tkinter event loop
    login_window.mainloop()


def login(username, password, login_window):
    user = database.get_user(username)
    if user and user[2] == password:  # user[2] is the password field
        print("Login successful!")
        login_window.destroy()
        open_main_window()
    else:
        print("Invalid credentials")


def show_registration_window(login_window):
    # Close the login window
    login_window.destroy()

    # Create a new window for registration
    registration_window = ThemedTk()
    registration_window.title("Register to AIRSWIPE")
    registration_window.geometry("600x400")
    registration_window.resizable(True, True)

    # Set the theme
    registration_window.set_theme("arc")

    # Create a canvas for background image
    canvas = tk.Canvas(registration_window, highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    # Load background image
    try:
        bg_image = Image.open("./IMG/bgpr1.jpeg")
        bg_image_resized = bg_image.resize((600, 400), Image.LANCZOS)
        bg_image_tk = ImageTk.PhotoImage(bg_image_resized)
        canvas.create_image(0, 0, anchor="nw", image=bg_image_tk, tags="bg_image")
        canvas.image = bg_image_tk
    except Exception as e:
        print(f"Error loading background image: {e}")

    # Main frame for registration form
    frame = tk.Frame(registration_window, bg="#1e1e2f", bd=2, relief="groove")
    frame.place(relx=0.5, rely=0.5, anchor="center", width=450, height=300)

    # Username Label and Entry
    reg_username_label = tk.Label(frame, text="Username:", font=("Helvetica", 12), fg="white", bg="#1e1e2f")
    reg_username_label.pack(pady=(20, 5))
    reg_username_entry = tk.Entry(frame, font=("Helvetica", 12))
    reg_username_entry.pack(pady=(0, 10))

    # Password Label and Entry
    reg_password_label = tk.Label(frame, text="Password:", font=("Helvetica", 12), fg="white", bg="#1e1e2f")
    reg_password_label.pack(pady=(10, 5))
    reg_password_entry = tk.Entry(frame, show="*", font=("Helvetica", 12))
    reg_password_entry.pack(pady=(0, 20))

    # Confirm Password Label and Entry
    reg_confirm_password_label = tk.Label(frame, text="Confirm Password:", font=("Helvetica", 12), fg="white", bg="#1e1e2f")
    reg_confirm_password_label.pack(pady=(10, 5))
    reg_confirm_password_entry = tk.Entry(frame, show="*", font=("Helvetica", 12))
    reg_confirm_password_entry.pack(pady=(0, 20))

    # Register Button
    register_button = tk.Button(
        frame, text="Register", font=("Helvetica", 14, "bold"),
        command=lambda: register_user(reg_username_entry.get(), reg_password_entry.get(), reg_confirm_password_entry.get(), registration_window),
        bg="#0C4C58", fg="white", activebackground="#0C4C58", activeforeground="white",
        relief="flat", padx=10, pady=5
    )
    register_button.pack(pady=(10, 5))

    # Run the Tkinter event loop for registration window
    registration_window.mainloop()


def register_user(username, password, confirm_password, registration_window):
    if password == confirm_password:
        if database.add_user(username, password):
            print(f"User registered with username: {username}")
            registration_window.destroy()
            show_login_window(None)
        else:
            print("Username already exists!")
    else:
        print("Passwords do not match!")

def logout(main_window):
    # Close the main window
    main_window.destroy()
    # Optionally, you could clear any user session data here
    # Open the welcome window again
    from welcome_window import open_welcome_window
          # Import the welcome window function
    open_welcome_window()  # Call the function to open the welcome window
if __name__ == "__main__":
    database.create_table()  # Create the database table if it doesn't exist
    show_login_window(None)
