import json
import time

import cv2
import mediapipe as mp
import mysql.connector

from database_utils import create_gestures_table  # Import database methods
from database_utils import save_custom_gesture_to_db

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

# Ensure the database table exists
create_gestures_table()

def display_message_on_camera(cap, message):
    """
    Display a message on the webcam feed.
    """
    ret, frame = cap.read()
    if ret:
        cv2.putText(frame, message, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        cv2.imshow("Gesture Recorder", frame)

def record_gesture():
    """
    Record a new gesture with advanced feedback, including a countdown timer and live preview.
    """
    print("Recording gesture... A countdown will begin shortly.")
    gesture_data = []  # List to store recorded frames

    # Open webcam
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Unable to access the camera.")
        return None

    # Countdown before starting recording
    for i in range(3, 0, -1):
        print(f"Get ready! Recording starts in {i} seconds...")
        display_message_on_camera(cap, f"Get ready! Recording starts in {i} seconds...")
        time.sleep(1)

    # Start recording
    print("Recording started. Perform your gesture now!")
    display_message_on_camera(cap, "Recording... Perform your gesture now!")

    start_time = time.time()
    RECORD_DURATION = 5  # Record for 5 seconds

    while cap.isOpened() and time.time() - start_time < RECORD_DURATION:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame. Exiting.")
            break

        # Flip the frame for a mirror view
        frame = cv2.flip(frame, 1)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process the frame with MediaPipe
        results = hands.process(frame_rgb)

        # Draw hand landmarks on the frame and collect data
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # Extract landmark positions
                frame_landmarks = [{"x": lm.x, "y": lm.y, "z": lm.z} for lm in hand_landmarks.landmark]
                gesture_data.append(frame_landmarks)

        # Display the frame
        cv2.putText(frame, "Recording in Progress...", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.imshow("Record Gesture", frame)

        # Stop recording if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Recording interrupted.")
            break

    print("Recording finished. Processing gesture data...")

    cap.release()
    cv2.destroyAllWindows()

    if gesture_data:
        print("Gesture recorded successfully.")
        return gesture_data
    else:
        print("No gesture data recorded.")
        return None

def save_custom_gesture(name, data):
    """
    Save the custom gesture to the database.
    """
    save_custom_gesture_to_db(name, data)  # Save to MySQL database

if __name__ == "__main__":
    gesture_name = input("Enter the name of the gesture: ").strip()
    if not gesture_name:
        print("Gesture name cannot be empty.")
        exit(1)

    recorded_gesture = record_gesture()
    if recorded_gesture:
        save_custom_gesture(gesture_name, recorded_gesture)
