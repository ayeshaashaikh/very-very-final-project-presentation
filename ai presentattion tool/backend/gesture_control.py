import math
import threading
import time
import tkinter as tk
import warnings

import cv2
import mediapipe as mp
import pyautogui
import speech_recognition as sr

warnings.filterwarnings("ignore", category=UserWarning, module=r'google\.protobuf\.symbol_database')

# Use two-hand detection so we can distinguish left/right.
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2)
mp_drawing = mp.solutions.drawing_utils

# Cooldown values for slide actions
cooldown_time = 2  
last_action_time = 0

gestures_locked = False
status_message = "Gestures Active"  

# Global flag to control gesture threads
gesture_control_active = False

# THUMBS GESTURE COOLDOWN
thumb_cooldown = 2.0
last_thumb_time = 0

# Timestamp to avoid conflicts with swipe detection when laser pointer is active.
last_laser_time = 0

# Global variables for laser pointer overlay
laser_active = False
laser_x = 0
laser_y = 0

def fingers_folded(hand_landmarks):
    """Check if fingers (middle, ring, pinky) are folded."""
    for tip_id, pip_id in zip([8, 12, 16, 20], [6, 10, 14, 18]):
        if hand_landmarks.landmark[tip_id].y < hand_landmarks.landmark[pip_id].y:
            return False
    return True

def is_only_index_extended(hand_landmarks):
    """Return True if only the index finger is extended and the others are folded."""
    index_extended = hand_landmarks.landmark[8].y < hand_landmarks.landmark[6].y
    middle_folded = hand_landmarks.landmark[12].y > hand_landmarks.landmark[10].y
    ring_folded = hand_landmarks.landmark[16].y > hand_landmarks.landmark[14].y
    pinky_folded = hand_landmarks.landmark[20].y > hand_landmarks.landmark[18].y
    return index_extended and middle_folded and ring_folded and pinky_folded

def show_status_message(message):
    window = tk.Tk()
    window.overrideredirect(True)
    window.attributes('-topmost', True)
    # Use white as transparent color (adjust as needed)
    window.attributes('-transparentcolor', 'white')
    window.configure(bg='white')

    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    window.geometry(f"{screen_width}x{screen_height}+0+0")

    label = tk.Label(
        window,
        text=message,
        font=("Helvetica", 48),
        fg="red" if gestures_locked else "green",
        bg="white"
    )
    label.pack(expand=True)

    window.after(2000, lambda: window.destroy())
    window.mainloop()

def navigate_ppt(slide_action):
    global last_action_time
    current_time = time.time()
    if current_time - last_action_time >= cooldown_time:
        if slide_action == "next":
            pyautogui.press('right')
        elif slide_action == "previous":
            pyautogui.press('left')
        last_action_time = current_time

def laser_overlay():
    """
    Create a transparent, always-on-top overlay window that draws the laser pointer effect.
    The window uses white as its transparent color.
    """
    global laser_active, laser_x, laser_y
    root = tk.Tk()
    root.overrideredirect(True)
    root.attributes("-topmost", True)
    # Set white as transparent (make sure no drawn item uses white as fill)
    root.attributes("-transparentcolor", "white")
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.geometry(f"{screen_width}x{screen_height}+0+0")
    
    # Create a canvas with a white background (which will be transparent)
    canvas = tk.Canvas(root, width=screen_width, height=screen_height, bg="white", highlightthickness=0)
    canvas.pack()
    
    pointer_tag = "laser"

    def update_overlay():
        nonlocal canvas
        canvas.delete(pointer_tag)
        if laser_active:
            # Draw a red circle with an outer glow effect.
            r_inner = 15
            r_outer = 30
            # Inner solid circle.
            canvas.create_oval(laser_x - r_inner, laser_y - r_inner, laser_x + r_inner, laser_y + r_inner,
                               fill="red", outline="red", tag=pointer_tag)
            # Outer ring (glow effect).
            canvas.create_oval(laser_x - r_outer, laser_y - r_outer, laser_x + r_outer, laser_y + r_outer,
                               outline="red", width=3, tag=pointer_tag)
        root.after(30, update_overlay)
    
    update_overlay()
    root.mainloop()

def detect_gesture():
    global gestures_locked, gesture_control_active, last_action_time, last_thumb_time, last_laser_time
    global laser_active, laser_x, laser_y
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    action = None
    right_baseline = None
    left_baseline = None
    last_pinch_end_time = 0
    pinch_in_progress = False  
    swipe_cooldown = 1.5   # seconds
    post_pinch_delay = 0.7 # seconds delay after pinch ends before swipe is re-enabled
    thumb_action = None  # "start_presentation" or "end_presentation"

    while cap.isOpened() and gesture_control_active:
        ret, frame = cap.read()
        if not ret:
            break

        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(image)
        current_time = time.time()
        thumb_action = None  # Reset per frame

        if result.multi_hand_landmarks and result.multi_handedness:
            for hand_landmarks, handedness in zip(result.multi_hand_landmarks, result.multi_handedness):
                # Draw landmarks on the camera feed for debugging (optional)
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                hand_label = handedness.classification[0].label  # "Left" or "Right"
                wrist = hand_landmarks.landmark[0]
                index_finger = hand_landmarks.landmark[8]

                # --- Laser Pointer Mode Detection ---
                if is_only_index_extended(hand_landmarks):
                    last_laser_time = current_time
                    laser_active = True
                    # Map the normalized index finger coordinates to screen coordinates.
                    screen_width, screen_height = pyautogui.size()
                    laser_x = int(index_finger.x * screen_width)
                    laser_y = int(index_finger.y * screen_height)
                    # Optionally, move the system pointer as well.
                    pyautogui.moveTo(laser_x, laser_y)
                    # Skip further processing for this hand.
                    continue
                else:
                    # If the gesture isn't active, turn off the laser after a short delay.
                    if current_time - last_laser_time > 0.5:
                        laser_active = False

                # --- Pinch detection to suppress swipe ---
                thumb_tip = hand_landmarks.landmark[4]
                index_tip = hand_landmarks.landmark[8]
                current_pinch_distance = math.sqrt((thumb_tip.x - index_tip.x)**2 +
                                                   (thumb_tip.y - index_tip.y)**2)
                if current_pinch_distance < 0.05:
                    pinch_in_progress = True
                    if hand_label == "Right":
                        if right_baseline is None:
                            right_baseline = current_pinch_distance
                    elif hand_label == "Left":
                        if left_baseline is None:
                            left_baseline = current_pinch_distance
                else:
                    if current_pinch_distance >= 0.05:
                        if hand_label == "Right" and right_baseline is not None:
                            last_pinch_end_time = current_time
                            right_baseline = None
                        elif hand_label == "Left" and left_baseline is not None:
                            last_pinch_end_time = current_time
                            left_baseline = None
                    pinch_in_progress = False

                # --- Swipe detection (only if no pinch, no recent laser, and delay passed) ---
                if ((current_time - last_pinch_end_time) > post_pinch_delay and 
                    (current_time - last_laser_time) > 1.0):
                    if not pinch_in_progress:
                        if (current_time - last_action_time) >= swipe_cooldown:
                            if wrist.x < index_finger.x:
                                action = "next"
                            elif wrist.x > index_finger.x:
                                action = "previous"
                            last_action_time = current_time

                # --- THUMBS GESTURE DETECTION ---
                if (current_time - last_thumb_time) >= thumb_cooldown:
                    if fingers_folded(hand_landmarks):
                        thumb_tip_y = hand_landmarks.landmark[4].y
                        thumb_ip_y = hand_landmarks.landmark[3].y
                        wrist_y = wrist.y
                        if thumb_tip_y < thumb_ip_y and thumb_tip_y < wrist_y:
                            thumb_action = "start_presentation"
                            last_thumb_time = current_time
                        elif thumb_tip_y > thumb_ip_y and thumb_tip_y > wrist_y:
                            thumb_action = "end_presentation"
                            last_thumb_time = current_time

        if thumb_action is not None:
            if not gestures_locked:
                print(f"Detected thumb gesture: {thumb_action}")
                if thumb_action == "start_presentation":
                    pyautogui.press('f5')
                elif thumb_action == "end_presentation":
                    pyautogui.press('esc')
            else:
                print("Thumb gesture ignored because gestures are locked.")
            thumb_action = None

        if not gestures_locked and action:
            print(f"Detected swipe gesture: {action}")
            if action == "next":
                pyautogui.press('right')
            elif action == "previous":
                pyautogui.press('left')
            action = None

        # Optionally show the camera feed for debugging
        cv2.imshow("Hand Gesture Control", frame)
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def voice_command_listener():
    global gestures_locked, status_message, gesture_control_active
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 400  
    recognizer.dynamic_energy_threshold = False
    mic = sr.Microphone()

    with mic as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print("Calibrated energy threshold:", recognizer.energy_threshold)
        while gesture_control_active:
            try:
                print("Listening for voice commands...")
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
                command = recognizer.recognize_google(audio).lower()
                print(f"Voice command received: {command}")

                if "lock" in command:
                    gestures_locked = True
                    status_message = "Gestures Locked"
                    show_status_message(status_message)
                    print("Gestures locked.")
                elif "resume" in command:
                    gestures_locked = False
                    status_message = "Gestures Active"
                    show_status_message(status_message)
                    print("Gestures unlocked.")
                elif "next" in command:
                    navigate_ppt("next")
                    print("Navigated to next slide.")
                elif "previous" in command:
                    navigate_ppt("previous")
                    print("Navigated to previous slide.")
            except sr.UnknownValueError:
                print("Voice command not recognized, retrying...")
                continue
            except sr.WaitTimeoutError:
                print("Listening timed out, retrying...")
                continue
            except sr.RequestError as e:
                print(f"Could not request results; {e}")
                time.sleep(1)
                continue
            except Exception as e:
                print(f"Unexpected error: {e}")
                continue

if __name__ == "__main__":
    # Start the laser overlay thread.
    overlay_thread = threading.Thread(target=laser_overlay, daemon=True)
    overlay_thread.start()

    # Start the gesture and voice control threads.
    gesture_control_active = True
    gesture_thread = threading.Thread(target=detect_gesture)
    voice_thread = threading.Thread(target=voice_command_listener)

    gesture_thread.start()
    voice_thread.start()

    gesture_thread.join()
    voice_thread.join()
