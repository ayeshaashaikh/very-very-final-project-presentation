import threading

from backend.gesture_control import detect_gesture
from backend.voice_command import listen_for_voice_command

if __name__ == "__main__":
    # Start gesture detection in a separate thread
    gesture_thread = threading.Thread(target=detect_gesture)
    gesture_thread.start()

    # Start listening for voice commands
    while True:
        listen_for_voice_command()
