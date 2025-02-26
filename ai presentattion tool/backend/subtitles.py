import json
import threading
import time
import tkinter as tk

import pyaudio
import vosk
import win32com.client as win32

# Initialize PowerPoint and ensure it’s visible.
powerpoint = win32.Dispatch("PowerPoint.Application")
powerpoint.Visible = True  

# Global flag and overlay instance for subtitles.
subtitle_active = False
overlay_instance = None
audio_thread = None
status_thread = None

def create_overlay(parent=None):
    """
    Create an overlay window.
    If a parent is provided, use a Toplevel so that the overlay
    is managed by the main application’s mainloop.
    """
    if parent:
        overlay = tk.Toplevel(parent)
    else:
        overlay = tk.Tk()
    overlay.title("Subtitles")
    overlay.geometry("800x50")
    overlay.attributes("-topmost", True)
    overlay.configure(bg="black")
    overlay.overrideredirect(True)
    overlay.attributes("-alpha", 0.8)
    
    # Create a label that fills the overlay.
    label = tk.Label(overlay, text="", font=("Helvetica", 24), fg="white", bg="black", anchor="center")
    label.pack(expand=True, fill='both')
    return overlay, label

def listen_and_display_subtitles(label):
    model = vosk.Model(r"C:\Users\Acer\Documents\VOS\model\vosk-model-small-en-us-0.15")
    recognizer = vosk.KaldiRecognizer(model, 16000)

    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000,
                    input=True, frames_per_buffer=8000)
    stream.start_stream()

    print("Listening for voice input...")
    while subtitle_active:
        try:
            # Read a chunk from the stream; using exception_on_overflow=False
            data = stream.read(4000, exception_on_overflow=False)
        except Exception as e:
            print("Error reading audio stream:", e)
            break
        if recognizer.AcceptWaveform(data):
            result = recognizer.Result()
            try:
                text = json.loads(result).get('text', '').capitalize()
            except Exception as e:
                text = ""
            if text:
                print(f"Recognized Text: {text}")
                # Update the label in a thread-safe manner using after().
                label.after(0, lambda: label.config(text=text))
        # A very short sleep yields CPU time.
        time.sleep(0.01)
    stream.stop_stream()
    stream.close()
    p.terminate()
    print("Stopped listening for subtitles.")

def check_presentation_status(overlay):
    while subtitle_active:
        try:
            if powerpoint.SlideShowWindows.Count > 0:
                overlay.after(0, overlay.deiconify)
            else:
                overlay.after(0, overlay.withdraw)
        except Exception as e:
            print("Error checking presentation status:", e)
        time.sleep(1)
    print("Stopped checking presentation status.")

def start_subtitle(parent=None):
    """
    Start the subtitle functionality.
    If a parent is provided, create a Toplevel attached to it.
    Do not call a separate mainloop if the parent exists.
    """
    global subtitle_active, overlay_instance, audio_thread, status_thread
    subtitle_active = True

    # Create the overlay in the main thread.
    overlay, label = create_overlay(parent)
    overlay_instance = overlay
    overlay.update_idletasks()

    # Position the overlay to span the full width of the screen and increased height.
    screen_width = overlay.winfo_screenwidth()
    screen_height = overlay.winfo_screenheight()
    overlay_height = 100        # Increased height
    overlay_width = screen_width  # Full screen width
    x_position = 0                # Start at the left edge.
    y_position = screen_height - overlay_height - 50
    overlay.geometry(f"{overlay_width}x{overlay_height}+{x_position}+{y_position}")
    
    # Update label wrap length so that long text wraps within the screen width.
    label.config(wraplength=screen_width)

    # Start background threads for audio listening and presentation status.
    audio_thread = threading.Thread(target=listen_and_display_subtitles, args=(label,), daemon=True)
    audio_thread.start()

    status_thread = threading.Thread(target=check_presentation_status, args=(overlay,), daemon=True)
    status_thread.start()

    # Only call mainloop if no parent is provided (i.e. standalone use).
    if not parent:
        overlay.mainloop()

def stop_subtitle():
    global subtitle_active, overlay_instance
    subtitle_active = False
    if overlay_instance:
        # Schedule destruction of the overlay on the main thread.
        overlay_instance.after(0, overlay_instance.destroy)
        overlay_instance = None

# For testing purposes, you could uncomment the following lines:
# start_subtitle()
