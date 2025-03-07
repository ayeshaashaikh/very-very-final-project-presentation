import subprocess
import sys

# List of packages required by the project
packages = [
    "opencv-python",           # For cv2
    "mediapipe",               # For mediapipe
    "mysql-connector-python",  # For mysql.connector
    "numpy",                   # For numpy
    "pyautogui",               # For pyautogui
    "SpeechRecognition",       # For speech_recognition
    "deep-translator",         # For deep_translator
    "pyaudio",                 # For pyaudio
    "vosk",                    # For vosk
    "pywin32",                 # For win32com.client
    "pygetwindow",             # For pygetwindow
    "customtkinter",           # For customtkinter
    "pillow",                  # For PIL (Pillow)
    "ttkthemes",               # For ttkthemes
    "playsound",               # For playsound
    "bcrypt"                   # For bcrypt
]

def install_packages(packages_list):
    for package in packages_list:
        try:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        except subprocess.CalledProcessError:
            print(f"Error installing package: {package}")

if __name__ == '__main__':
    install_packages(packages)
    print("All packages installed!")
