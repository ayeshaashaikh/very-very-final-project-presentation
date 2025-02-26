import re
import threading
import time

import pyautogui
import pygetwindow as gw
import speech_recognition as sr
import win32com.client  # For COM automation with PowerPoint

# Initialize the speech recognizer
recognizer = sr.Recognizer()
recognizer.energy_threshold = 300  # Adjust based on your environment
recognizer.dynamic_energy_threshold = True

def focus_powerpoint():
    """
    Attempts to bring a PowerPoint window to the foreground.
    Adjust the window title search as needed if your PowerPoint window title is different.
    """
    ppt_windows = gw.getWindowsWithTitle('PowerPoint')
    if ppt_windows:
        ppt_window = ppt_windows[0]
        try:
            ppt_window.activate()
            print("Focused on PowerPoint window.")
        except Exception as e:
            print(f"Could not focus on PowerPoint: {e}")
    else:
        print("PowerPoint window not found.")

def goto_slide(slide_number):
    """
    Uses COM automation to instruct PowerPoint to jump directly to the given slide number.
    """
    try:
        ppt_app = win32com.client.GetActiveObject("PowerPoint.Application")
    except Exception as e:
        print("PowerPoint application not found via COM. Is PowerPoint running?")
        return

    try:
        slide_number = int(slide_number)
        if ppt_app.SlideShowWindows.Count > 0:
            slideshow = ppt_app.SlideShowWindows(1)
            slideshow.View.GotoSlide(slide_number)
            print(f"Navigated to slide {slide_number} via COM automation.")
        else:
            print("No active slideshow window found. Make sure you're in slideshow mode.")
    except Exception as e:
        print("Error navigating slide:", e)

def goto_slide_by_title(title_text):
    """
    Uses COM automation to navigate to a slide by its title.
    Searches the active presentation for a slide whose title matches title_text.
    """
    try:
        ppt_app = win32com.client.GetActiveObject("PowerPoint.Application")
    except Exception as e:
        print("PowerPoint application not found via COM. Is PowerPoint running?")
        return

    try:
        pres = ppt_app.ActivePresentation
        found_slide = None
        for slide in pres.Slides:
            try:
                # Try to access the slide's title
                slide_title = slide.Shapes.Title.TextFrame.TextRange.Text
            except Exception:
                slide_title = ""
            if slide_title.lower().strip() == title_text.lower().strip():
                found_slide = slide.SlideIndex
                break
        if found_slide:
            if ppt_app.SlideShowWindows.Count > 0:
                slideshow = ppt_app.SlideShowWindows(1)
                slideshow.View.GotoSlide(found_slide)
                print(f"Navigated to slide {found_slide} with title '{title_text}'.")
            else:
                print("No active slideshow window found. Make sure you're in slideshow mode.")
        else:
            print(f"No slide found with title '{title_text}'.")
    except Exception as e:
        print("Error navigating to slide by title:", e)

def listen_for_voice_command(voice_active):
    """
    Continuously listens for voice commands and processes them.
    Supported commands:
      - "next" (moves to the next slide)
      - "previous" (moves to the previous slide)
      - "go to slide [number]" (jumps to the specified slide by number)
      - "go to [title]" (jumps to the slide whose title matches the spoken phrase)
      - "start presentation" (simulates F5 to start the slideshow)
      - "stop presentation" (simulates Esc to exit the slideshow)
      - "stop listening" (exits the loop)
    """
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print("Listening for voice commands...")

        while voice_active[0]:
            try:
                # Attempt to listen; if no phrase is detected, catch the timeout and continue silently
                try:
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
                except sr.WaitTimeoutError:
                    continue

                try:
                    command = recognizer.recognize_google(audio).lower()
                    print(f"Voice command received: {command}")
                except sr.UnknownValueError:
                    print("Didn't catch that, please try again...")
                    continue
                except sr.RequestError as e:
                    print(f"Request error: {e}. Check your internet connection.")
                    break

                # Bring PowerPoint to focus
                focus_powerpoint()

                if "next" in command:
                    threading.Thread(target=pyautogui.press, args=('right',)).start()
                    print("Moving to next slide")
                elif "previous" in command:
                    threading.Thread(target=pyautogui.press, args=('left',)).start()
                    print("Moving to previous slide")
                elif "go to" in command:
                    match = re.search(r"(?:go to )?slide(?: number)? (\d+)", command)
                    if match:
                        slide_number = match.group(1)
                        print(f"Navigating to slide {slide_number}")
                        goto_slide(slide_number)
                    else:
                        # Assume navigation by title if no number found.
                        title_command = command
                        if title_command.startswith("go to slide"):
                            title_command = title_command[len("go to slide"):].strip()
                        elif title_command.startswith("go to"):
                            title_command = title_command[len("go to"):].strip()
                        print(f"Navigating to slide with title: '{title_command}'")
                        goto_slide_by_title(title_command)
                elif "start presentation" in command:
                    threading.Thread(target=pyautogui.press, args=('f5',)).start()
                    print("Starting presentation")
                elif "stop presentation" in command:
                    threading.Thread(target=pyautogui.press, args=('esc',)).start()
                    print("Ending presentation")
                elif "stop listening" in command:
                    voice_active[0] = False
                    print("Voice command deactivation requested. Stopping listening.")
                else:
                    print("Command not recognized. Please try again.")
            except Exception as e:
                print(f"Unexpected error: {e}")

if __name__ == "__main__":
    # For standalone testing:
    voice_active = [True]
    try:
        listen_for_voice_command(voice_active)
    except KeyboardInterrupt:
        print("Listening stopped by user")
