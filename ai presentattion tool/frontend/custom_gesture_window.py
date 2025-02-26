import json
import os
import time
from tkinter import messagebox

import customtkinter as ctk
import cv2
import mediapipe as mp
import mysql.connector
import numpy as np
from PIL import Image, ImageTk

# Set appearance mode for CustomTkinter
ctk.set_appearance_mode("dark")

# ---------------------------
# UI STYLE CONSTANTS
# ---------------------------
BACKGROUND_COLOR = "#000000"    # Black background
SIDEBAR_COLOR = "#1a1a1a"       # Dark grey for secondary panels
ACCENT_COLOR = "#b3004f"        # Dark pink accent
HOVER_COLOR = "#e91e63"         # Neon pink for hover effects
TEXT_COLOR = "#ffffff"          # White text
FONT_FAMILY = "Segoe UI"        # Modern, clean font

# ---------------------------
# DATABASE CONFIGURATION
# ---------------------------
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',   # Set your MySQL password
    'database': 'gesture_db'
}

# ---------------------------
# INITIALIZE MEDIAPIPE
# ---------------------------
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_drawing = mp.solutions.drawing_utils

# ---------------------------
# UTILITY FUNCTIONS
# ---------------------------
def calculate_angle(a, b, c):
    """Calculate the angle (in degrees) at point b formed by points a, b, and c."""
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    ba = a - b
    bc = c - b
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-6)
    angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
    return np.degrees(angle)

def compute_angles(landmarks):
    """
    Given a dictionary of landmarks (index -> (x, y, z)), compute an angle vector.
    Returns a list of 5 angles: thumb, index, middle, ring, and pinky.
    """
    def get_xy(idx):
        return (landmarks[idx][0], landmarks[idx][1])
    angles = []
    try:
        angles.append(calculate_angle(get_xy(1), get_xy(2), get_xy(3)))
        angles.append(calculate_angle(get_xy(5), get_xy(6), get_xy(7)))
        angles.append(calculate_angle(get_xy(9), get_xy(10), get_xy(11)))
        angles.append(calculate_angle(get_xy(13), get_xy(14), get_xy(15)))
        angles.append(calculate_angle(get_xy(17), get_xy(18), get_xy(19)))
    except Exception as e:
        print("Error computing angles:", e)
    return angles

def store_gesture_in_db(action, angle_vector, image_path):
    """Store the gesture angle vector with its action and image path in the database."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        query = "INSERT INTO gestures (action, gesture_data, image_path) VALUES (%s, %s, %s)"
        cursor.execute(query, (action, json.dumps(angle_vector), image_path))
        conn.commit()
        cursor.close()
        conn.close()
        messagebox.showinfo("Success", f"Gesture for '{action}' saved successfully!")
    except Exception as e:
        messagebox.showerror("Database Error", str(e))

def record_and_save_gesture(action):
    """
    Record a gesture from the webcam, compute its angle vector, capture a snapshot,
    and store the gesture in the database.
    """
    cap = cv2.VideoCapture(0)
    recorded_angles = None
    captured_frame = None
    messagebox.showinfo("Recording", f"Recording gesture for '{action}'.\nPerform your gesture and press 'q' to capture.")
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(image)
        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                raw_landmarks = {i: (lm.x, lm.y, lm.z) for i, lm in enumerate(hand_landmarks.landmark)}
                computed_angles = compute_angles(raw_landmarks)
                recorded_angles = computed_angles
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                cv2.putText(frame, "Gesture Captured! Press 'q' to save.", (50, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2, cv2.LINE_AA)
                captured_frame = frame.copy()
        cv2.imshow("Record Gesture", frame)
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
    if recorded_angles and captured_frame is not None:
        os.makedirs("gesture_images", exist_ok=True)
        image_path = f"gesture_images/{action}_{int(time.time())}.png"
        cv2.imwrite(image_path, captured_frame)
        store_gesture_in_db(action, recorded_angles, image_path)
    else:
        messagebox.showerror("Error", "No gesture data captured.")

def record_and_save_gesture_for_update(action):
    """
    Record a new gesture for updating an existing record.
    Returns the new angle vector and snapshot image path.
    """
    cap = cv2.VideoCapture(0)
    recorded_angles = None
    captured_frame = None
    messagebox.showinfo("Recording", f"Recording gesture for '{action}' update.\nPerform your gesture and press 'q' to capture.")
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(image)
        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                raw_landmarks = {i: (lm.x, lm.y, lm.z) for i, lm in enumerate(hand_landmarks.landmark)}
                computed_angles = compute_angles(raw_landmarks)
                recorded_angles = computed_angles
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                cv2.putText(frame, "Gesture Captured! Press 'q' to save.", (50, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2, cv2.LINE_AA)
                captured_frame = frame.copy()
        cv2.imshow("Record Gesture for Update", frame)
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
    if recorded_angles and captured_frame is not None:
        os.makedirs("gesture_images", exist_ok=True)
        image_path = f"gesture_images/{action}_update_{int(time.time())}.png"
        cv2.imwrite(image_path, captured_frame)
        return recorded_angles, image_path
    else:
        messagebox.showerror("Error", "No gesture data captured for update.")
        return None, None

# ---------------------------
# CUSTOMTKINTER UI WINDOWS
# ---------------------------
def open_customize_gesture_window(main_window):
    """Open the Customize Gestures window with a modern, sleek dark UI."""
    window = ctk.CTkToplevel(main_window)
    window.title("Customize Gestures")
    window.geometry("400x450")
    window.configure(fg_color=BACKGROUND_COLOR)
    
    header = ctk.CTkLabel(window, text="Customize Gestures", 
                          font=ctk.CTkFont(family=FONT_FAMILY, size=20, weight="bold"),
                          fg_color=BACKGROUND_COLOR, text_color=ACCENT_COLOR)
    header.pack(pady=20)
    
    subheader = ctk.CTkLabel(window, text="Select an action to record a new gesture:", 
                             font=ctk.CTkFont(family=FONT_FAMILY, size=14),
                             fg_color=BACKGROUND_COLOR, text_color=TEXT_COLOR)
    subheader.pack(pady=10)
    
    btn_params = {
        "font": ctk.CTkFont(family=FONT_FAMILY, size=14, weight="bold"),
        "fg_color": ACCENT_COLOR,
        "hover_color": HOVER_COLOR,
        "text_color": TEXT_COLOR,
        "width": 200,
        "corner_radius": 8,
        "cursor": "hand2"
    }
    
    ctk.CTkButton(window, text="Next Slide", command=lambda: record_and_save_gesture("next"), **btn_params).pack(pady=5)
    ctk.CTkButton(window, text="Previous Slide", command=lambda: record_and_save_gesture("previous"), **btn_params).pack(pady=5)
    ctk.CTkButton(window, text="Start Presentation", command=lambda: record_and_save_gesture("start"), **btn_params).pack(pady=5)
    ctk.CTkButton(window, text="End Presentation", command=lambda: record_and_save_gesture("end"), **btn_params).pack(pady=5)
    ctk.CTkButton(window, text="Manage Gestures", command=lambda: manage_custom_gestures(main_window), **btn_params).pack(pady=20)
    
    window.mainloop()

def manage_custom_gestures(main_window):
    """
    Open the Manage Gestures window which displays stored custom gestures with images,
    and allows deletion or updating.
    """
    from backend.backend_customized_gesture import (delete_custom_gesture,
                                                    get_all_custom_gestures,
                                                    update_custom_gesture)
    manage_window = ctk.CTkToplevel(main_window)
    manage_window.title("Manage Custom Gestures")
    manage_window.geometry("600x550")
    manage_window.configure(fg_color=BACKGROUND_COLOR)
    
    header = ctk.CTkLabel(manage_window, text="Manage Custom Gestures", 
                          font=ctk.CTkFont(family=FONT_FAMILY, size=20, weight="bold"),
                          fg_color=BACKGROUND_COLOR, text_color=ACCENT_COLOR)
    header.pack(pady=20)
    
    gestures = get_all_custom_gestures()
    
    if not gestures:
        ctk.CTkLabel(manage_window, text="No custom gestures stored.", 
                     font=ctk.CTkFont(family=FONT_FAMILY, size=14),
                     fg_color=BACKGROUND_COLOR, text_color=TEXT_COLOR).pack(pady=20)
        return
    
    scroll_frame = ctk.CTkScrollableFrame(manage_window, fg_color=BACKGROUND_COLOR, corner_radius=8)
    scroll_frame.pack(padx=20, pady=10, fill="both", expand=True)
    
    for gesture in gestures:
        frame = ctk.CTkFrame(scroll_frame, fg_color=SIDEBAR_COLOR, corner_radius=8)
        frame.pack(padx=10, pady=5, fill="x")
        
        action_label = ctk.CTkLabel(frame, text=f"Action: {gesture['action']}", 
                                    font=ctk.CTkFont(family=FONT_FAMILY, size=14, weight="bold"),
                                    fg_color=SIDEBAR_COLOR, text_color=TEXT_COLOR)
        action_label.pack(side="left", padx=10)
        
        try:
            img = Image.open(gesture["image_path"])
            img = img.resize((100, 100))
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(100, 100))
            img_label = ctk.CTkLabel(frame, image=ctk_img, text="", fg_color=SIDEBAR_COLOR)
            img_label.image = ctk_img  # Keep a reference
            img_label.pack(side="left", padx=10)
        except Exception as e:
            ctk.CTkLabel(frame, text="No image available", 
                         font=ctk.CTkFont(family=FONT_FAMILY, size=12),
                         fg_color=SIDEBAR_COLOR, text_color=TEXT_COLOR).pack(side="left", padx=10)
        
        def delete_callback(gesture_id=gesture["id"]):
            delete_custom_gesture(gesture_id)
            messagebox.showinfo("Deleted", "Gesture deleted successfully!")
            manage_window.destroy()
            manage_custom_gestures(main_window)
        
        delete_button = ctk.CTkButton(frame, text="Delete", command=delete_callback,
                                      font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
                                      fg_color=ACCENT_COLOR, hover_color=HOVER_COLOR, text_color=TEXT_COLOR,
                                      width=80, corner_radius=8, cursor="hand2")
        delete_button.pack(side="right", padx=10)
        
        def update_callback(gesture_id=gesture["id"], action=gesture["action"]):
            new_angles, new_image_path = record_and_save_gesture_for_update(action)
            if new_angles and new_image_path:
                update_custom_gesture(gesture_id, new_angles, new_image_path)
                messagebox.showinfo("Updated", "Gesture updated successfully!")
                manage_window.destroy()
                manage_custom_gestures(main_window)
        
        update_button = ctk.CTkButton(frame, text="Update", command=update_callback,
                                      font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
                                      fg_color=ACCENT_COLOR, hover_color=HOVER_COLOR, text_color=TEXT_COLOR,
                                      width=80, corner_radius=8, cursor="hand2")
        update_button.pack(side="right", padx=10)
    
    manage_window.mainloop()
