import json
import time

import cv2
import mediapipe as mp
import mysql.connector
import numpy as np
import pyautogui

# MySQL database connection parameters (adjust as needed)
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',   # Set your MySQL password
    'database': 'gesture_db'
}

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_drawing = mp.solutions.drawing_utils

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
        # Thumb: use landmarks 1,2,3; compute angle at landmark 2.
        angle_thumb = calculate_angle(get_xy(1), get_xy(2), get_xy(3))
        angles.append(angle_thumb)
        # Index finger: use landmarks 5,6,7; compute angle at landmark 6.
        angle_index = calculate_angle(get_xy(5), get_xy(6), get_xy(7))
        angles.append(angle_index)
        # Middle finger: use landmarks 9,10,11; compute angle at landmark 10.
        angle_middle = calculate_angle(get_xy(9), get_xy(10), get_xy(11))
        angles.append(angle_middle)
        # Ring finger: use landmarks 13,14,15; compute angle at landmark 14.
        angle_ring = calculate_angle(get_xy(13), get_xy(14), get_xy(15))
        angles.append(angle_ring)
        # Pinky: use landmarks 17,18,19; compute angle at landmark 18.
        angle_pinky = calculate_angle(get_xy(17), get_xy(18), get_xy(19))
        angles.append(angle_pinky)
    except Exception as e:
        print("Error computing angles:", e)
    return angles

def store_gesture_in_db(action, angle_vector, image_path):
    """Store the gesture angle vector with its action and image path in the MySQL database."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        query = "INSERT INTO gestures (action, gesture_data, image_path) VALUES (%s, %s, %s)"
        cursor.execute(query, (action, json.dumps(angle_vector), image_path))
        conn.commit()
        cursor.close()
        conn.close()
        print(f"Gesture for '{action}' saved successfully!")
    except Exception as e:
        print("Database Error:", e)

def get_custom_gestures_from_db():
    """
    Retrieve custom gestures from the database as a dictionary: action -> (angle_vector, image_path).
    (This function is useful for gesture matching.)
    """
    gestures = {}
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        query = "SELECT action, gesture_data, image_path FROM gestures"
        cursor.execute(query)
        for (action, gesture_data, image_path) in cursor:
            gestures[action] = {
                "angles": json.loads(gesture_data),
                "image_path": image_path
            }
        cursor.close()
        conn.close()
    except Exception as e:
        print("Database Error:", e)
    return gestures

def get_all_custom_gestures():
    """Retrieve all custom gestures with their ID, action, angle vector, and image path."""
    gestures = []
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        query = "SELECT id, action, gesture_data, image_path FROM gestures"
        cursor.execute(query)
        for (gid, action, gesture_data, image_path) in cursor:
            gestures.append({
                "id": gid,
                "action": action,
                "gesture_data": json.loads(gesture_data),
                "image_path": image_path
            })
        cursor.close()
        conn.close()
    except Exception as e:
        print("Database Error:", e)
    return gestures

def delete_custom_gesture(gesture_id):
    """Delete a custom gesture from the database by its ID."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        query = "DELETE FROM gestures WHERE id = %s"
        cursor.execute(query, (gesture_id,))
        conn.commit()
        cursor.close()
        conn.close()
        print(f"Gesture with id {gesture_id} deleted successfully!")
    except Exception as e:
        print("Database Error:", e)

def update_custom_gesture(gesture_id, new_angle_vector, new_image_path):
    """Update a custom gesture (angle vector and image path) in the database by its ID."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        query = "UPDATE gestures SET gesture_data = %s, image_path = %s WHERE id = %s"
        cursor.execute(query, (json.dumps(new_angle_vector), new_image_path, gesture_id))
        conn.commit()
        cursor.close()
        conn.close()
        print(f"Gesture with id {gesture_id} updated successfully!")
    except Exception as e:
        print("Database Error:", e)

def compare_angle_vectors(detected_angles, stored_angles):
    """Compare two angle vectors using Euclidean distance."""
    if len(detected_angles) != len(stored_angles):
        return False
    diff = np.linalg.norm(np.array(detected_angles) - np.array(stored_angles))
    threshold = 15.0  # Adjust this threshold as needed
    print(f"[DEBUG] Angle vector difference: {diff:.2f} (Threshold: {threshold})")
    return diff < threshold

def execute_action(action):
    """Execute the presentation action based on the detected gesture."""
    print(f"[DEBUG] Executing action: {action}")
    if action == "next":
        pyautogui.press('right')
    elif action == "previous":
        pyautogui.press('left')
    elif action == "start":
        pyautogui.press('f5')
    elif action == "end":
        pyautogui.press('esc')
    else:
        print(f"No action defined for: {action}")

def use_customized_gesture():
    """Continuously capture webcam input and trigger actions for matching custom gestures using angle vectors."""
    custom_gestures = get_custom_gestures_from_db()
    if not custom_gestures:
        print("No custom gestures found in the database.")
        return

    cap = cv2.VideoCapture(0)
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(image)
        
        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                raw_landmarks = {i: (lm.x, lm.y, lm.z) for i, lm in enumerate(hand_landmarks.landmark)}
                detected_angles = compute_angles(raw_landmarks)
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                
                for action, data in custom_gestures.items():
                    stored_angles = data["angles"]
                    if compare_angle_vectors(detected_angles, stored_angles):
                        print(f"Detected custom gesture for action: {action}")
                        execute_action(action)
                        # Pause briefly to avoid triggering the same gesture repeatedly
                        time.sleep(2)
                        break
        
        cv2.imshow("Customized Gesture Control", frame)
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    use_customized_gesture()