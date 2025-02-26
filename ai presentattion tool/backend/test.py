import time

import win32com.client as win32


def check_presentation_status():
    # Initialize PowerPoint application
    powerpoint = win32.Dispatch("PowerPoint.Application")
    print("PowerPoint application connected.")

    while True:
        try:
            print("Checking PowerPoint slideshow status...")  # Debugging line
            if powerpoint.SlideShowWindows.Count > 0:  # If there is an active slideshow
                print("Slideshow detected!")
            else:
                print("No slideshow detected.")
        except Exception as e:
            print(f"Error accessing PowerPoint: {e}")  # Print any errors that occur
        time.sleep(1)  # Check every second

# Start checking PowerPoint status
check_presentation_status()
