import os
import sys
import threading
import tkinter as tk
import tkinter.simpledialog as simpledialog
from tkinter import messagebox

import customtkinter as ctk
from PIL import Image  # For loading icons
from playsound import playsound  # Make sure to install playsound via pip

# Append parent directory if needed
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import backend functions (adjust these imports as per your project structure)
from backend.backend_customized_gesture import use_customized_gesture
from backend.gesture_control import detect_gesture, voice_command_listener
from backend.real_time_translation import SpeechTranslatorWithSubtitles
from backend.subtitles import start_subtitle, stop_subtitle
from backend.voice_command import listen_for_voice_command
from frontend.custom_gesture_window import open_customize_gesture_window

# Global threads/flags
voice_thread = None
voice_active = [False]
translation_active = [False]
gesture_active = [False]  # New flag for gesture control
subtitles_active = [False]  # New flag for subtitles toggle

# Global main control window variable
main_control_window = None

# Color Constants
BACKGROUND_COLOR = "#000000"  # Pure Black
SIDEBAR_COLOR = "#1a1a1a"     # Very dark grey for sidebar
ACCENT_COLOR = "#b3004f"      # Darker pink accent
HOVER_COLOR = "#e91e63"       # Lighter neon pink for hover effects

# Choose a professional looking font
PRO_FONT = "Segoe UI"  # Change to your preferred font

# ---------------------------
# POP‑IN ANIMATION FUNCTION
# ---------------------------
def animate_label_font(label, start_size, target_size, steps, delay, weight="bold"):
    def step_animation(current_step):
        if current_step > steps:
            label.configure(font=ctk.CTkFont(family=PRO_FONT, size=target_size, weight=weight))
            return
        new_size = int(start_size + (target_size - start_size) * (current_step / steps))
        label.configure(font=ctk.CTkFont(family=PRO_FONT, size=new_size, weight=weight))
        label.after(delay, lambda: step_animation(current_step + 1))
    step_animation(0)

# ---------------------------
# TOOLTIP CLASS DEFINITION
# ---------------------------
class CreateToolTip(object):
    def __init__(self, widget, text='widget info'):
        self.waittime = 500     # milliseconds
        self.wraplength = 200   # pixels
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id = None
        self.tw = None
    def enter(self, event=None):
        self.schedule()
    def leave(self, event=None):
        self.unschedule()
        self.hidetip()
    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)
    def unschedule(self):
        id_ = self.id
        self.id = None
        if id_:
            self.widget.after_cancel(id_)
    def showtip(self, event=None):
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        self.tw = tk.Toplevel(self.widget)
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(
            self.tw,
            text=self.text,
            justify='left',
            background="#ffffe0",
            relief='solid',
            borderwidth=1,
            wraplength=self.wraplength,
            font=(PRO_FONT, 10)
        )
        label.pack(ipadx=1)
    def hidetip(self):
        if self.tw:
            self.tw.destroy()
        self.tw = None

# ---------------------------
# ICON LOADING (Optional)
# ---------------------------
def load_icon(image_name, size=(40, 40)):
    try:
        icon_path = os.path.join(os.path.dirname(__file__), "icons", image_name)
        img = Image.open(icon_path)
        return ctk.CTkImage(img, size=size)
    except Exception as e:
        print(f"Error loading icon {image_name}: {e}")
        return None

# Load icons for each feature (ensure these files exist in an "icons" folder)
gesture_icon = load_icon("gesture.png")
voice_icon = load_icon("voice2.png")
subtitles_icon = load_icon("subtitles.png")
customize_icon = load_icon("customize.png")
# Load the air logo for the sidebar at the top
air_logo = load_icon("air.png", size=(200, 100))  # Adjust size as needed

# ---------------------------
# TRANSLATION OPTIONS WINDOW
# ---------------------------
def open_translation_options(parent):
    options_window = tk.Toplevel(parent)
    options_window.title("Select Translation Pair")
    options_window.geometry("300x250")
    options_window.configure(bg=BACKGROUND_COLOR)
    
    label = tk.Label(options_window, text="Select a Translation Option", font=(PRO_FONT, 12, "bold"), bg=BACKGROUND_COLOR, fg="white")
    label.pack(pady=10)
    
    def select_option(recognizer_lang, target_lang):
        from backend.real_time_translation import start_real_time_translation
        options_window.destroy()
        translation_active[0] = True
        start_real_time_translation(recognizer_lang, target_lang, parent)
        messagebox.showinfo("Real-Time Translation", "Translation Activated! Start Speaking.")
    
    btn_style = {"font": (PRO_FONT, 10, "bold"), "bg": ACCENT_COLOR, "fg": "white", "bd": 0, "activebackground": HOVER_COLOR, "relief": "flat"}
    
    btn1 = tk.Button(options_window, text="English to Hindi", command=lambda: select_option("en", "hi"), **btn_style)
    btn1.pack(pady=5, fill="x", padx=20)
    
    btn2 = tk.Button(options_window, text="Hindi to English", command=lambda: select_option("hi-IN", "en"), **btn_style)
    btn2.pack(pady=5, fill="x", padx=20)
    
    btn3 = tk.Button(options_window, text="English to French", command=lambda: select_option("en", "fr"), **btn_style)
    btn3.pack(pady=5, fill="x", padx=20)
    
    btn4 = tk.Button(options_window, text="English to German", command=lambda: select_option("en", "de"), **btn_style)
    btn4.pack(pady=5, fill="x", padx=20)

# ---------------------------
# SET TIMER FUNCTIONALITY
# ---------------------------
def set_timer():
    # Prompt the user for the timer duration in minutes.
    duration = simpledialog.askinteger("Set Timer", "Enter duration in minutes:", minvalue=1, parent=main_control_window)
    if duration is not None:
        total_time = duration * 60  # Convert minutes to seconds.
        # Create a new window to display the countdown timer.
        timer_window = tk.Toplevel(main_control_window)
        timer_window.title("Timer Countdown")
        timer_window.geometry("300x100")
        
        timer_label = tk.Label(timer_window, text="", font=(PRO_FONT, 20))
        timer_label.pack(expand=True)
        
        def countdown(time_left):
            minutes = time_left // 60
            secs = time_left % 60
            timer_label.config(text=f"{minutes:02}:{secs:02}")
            if time_left > 0:
                timer_label.after(1000, lambda: countdown(time_left - 1))
            else:
                messagebox.showinfo("Time's Up!", "The allotted time has ended!")
                # Play alarm tone. Make sure "alarm.wav" exists in the same directory.
                alarm_path = os.path.join(os.path.dirname(__file__), "alarm.wav")
                try:
                    playsound(alarm_path)
                except Exception as e:
                    print("Error playing alarm tone:", e)
        
        countdown(total_time)

# ---------------------------
# MAIN WINDOW & ANIMATION
# ---------------------------
def open_main_window(welcome_window):
    global main_control_window
    welcome_window.withdraw()
    
    main_window = ctk.CTkToplevel()
    main_window.title("AI Presentation Tool - Main Control")
    main_window.geometry("1920x1080")
    main_window.configure(fg_color=BACKGROUND_COLOR)
    
    main_window.grid_columnconfigure(1, weight=1)
    main_window.grid_rowconfigure(0, weight=1)
    
    # SIDEBAR (Left)
    sidebar = ctk.CTkFrame(main_window, width=250, fg_color=SIDEBAR_COLOR, corner_radius=0)
    sidebar.grid(row=0, column=0, sticky="ns")
    sidebar.grid_propagate(False)
    
    # Display the air logo at the top of the sidebar if available
    if air_logo:
        logo_label = ctk.CTkLabel(sidebar, image=air_logo, text="")  
        logo_label.pack(pady=20, padx=10)
    
    # SIDEBAR BUTTONS
    button_params = {
        "fg_color": ACCENT_COLOR,
        "hover_color": HOVER_COLOR,
        "font": ctk.CTkFont(family=PRO_FONT, size=14, weight="bold"),
        "width": 200,
        "corner_radius": 10
    }
    
    gesture_button = ctk.CTkButton(
        sidebar,
        text="Gesture Control",
        command=toggle_gesture_control,
        **button_params
    )
    gesture_button.pack(pady=10, padx=10)
    CreateToolTip(gesture_button, "Toggle gesture recognition features")
    
    voice_button = ctk.CTkButton(
        sidebar,
        text="Voice Command",
        command=toggle_voice_command,
        **button_params
    )
    voice_button.pack(pady=10, padx=10)
    CreateToolTip(voice_button, "Activate voice commands for controlling the presentation")
    
    subtitle_button = ctk.CTkButton(
        sidebar,
        text="Subtitles",
        command=toggle_subtitles,
        **button_params
    )
    subtitle_button.pack(pady=10, padx=10)
    CreateToolTip(subtitle_button, "Toggle subtitles during the presentation")
    
    translation_button = ctk.CTkButton(
        sidebar,
        text="Real-Time Translation",
        command=toggle_translation,
        **button_params
    )
    translation_button.pack(pady=10, padx=10)
    CreateToolTip(translation_button, "Toggle real-time translation")
    
    customize_gesture_button = ctk.CTkButton(
        sidebar,
        text="Customize Gesture",
        command=lambda: open_customize_gesture_window(main_window),
        **button_params
    )
    customize_gesture_button.pack(pady=10, padx=10)
    CreateToolTip(customize_gesture_button, "Customize gesture controls")
    
    customized_gesture_button = ctk.CTkButton(
        sidebar,
        text="Use Custom Gesture",
        command=activate_customized_gesture,
        **button_params
    )
    customized_gesture_button.pack(pady=10, padx=10)
    CreateToolTip(customized_gesture_button, "Activate your customized gesture")
    
    logout_button = ctk.CTkButton(
        sidebar,
        text="Logout",
        command=lambda: logout(main_window, welcome_window),
        **button_params
    )
    logout_button.pack(pady=10, padx=10)
    CreateToolTip(logout_button, "Logout from the application")
    
    # CONTENT AREA (Right Side)
    content = ctk.CTkFrame(main_window, fg_color=BACKGROUND_COLOR, corner_radius=15)
    content.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
    
    header = ctk.CTkLabel(
        content,
        text="Control Panel",
        text_color=ACCENT_COLOR,
        font=ctk.CTkFont(family=PRO_FONT, size=32, weight="bold"),
        fg_color=BACKGROUND_COLOR
    )
    header.pack(pady=(20, 10))
    
    # STATUS & INFORMATION SECTION in content area
    card = ctk.CTkFrame(content, fg_color=SIDEBAR_COLOR, corner_radius=15, border_width=2)
    card.pack(pady=20, padx=20, fill="both", expand=True)
    
    card_label = ctk.CTkLabel(
        card,
        text="Status and Information",
        text_color="white",
        font=ctk.CTkFont(family=PRO_FONT, size=24, weight="bold"),
        fg_color=SIDEBAR_COLOR
    )
    card_label.pack(pady=(10, 5))
    
    def create_step(parent, number, title, details, icon=None):
        step_frame = ctk.CTkFrame(parent, fg_color=SIDEBAR_COLOR)
        step_frame.pack(fill="x", pady=15, padx=10)
        
        if icon:
            icon_label = ctk.CTkLabel(
                step_frame,
                image=icon,
                text=""
            )
            icon_label.grid(row=0, column=0, rowspan=2, padx=(0, 10), sticky="n")
        else:
            circle_label = ctk.CTkLabel(
                step_frame,
                text=number,
                fg_color=ACCENT_COLOR,
                width=40,
                height=40,
                corner_radius=20,
                text_color="white",
                font=ctk.CTkFont(family=PRO_FONT, size=20, weight="bold")
            )
            circle_label.grid(row=0, column=0, rowspan=2, padx=(0, 10), sticky="n")
            animate_label_font(circle_label, start_size=10, target_size=20, steps=10, delay=30, weight="bold")
        
        title_label = ctk.CTkLabel(
            step_frame,
            text=title,
            text_color="white",
            font=ctk.CTkFont(family=PRO_FONT, size=20, weight="bold")
        )
        title_label.grid(row=0, column=1, sticky="w", pady=(0, 2))
        animate_label_font(title_label, start_size=14, target_size=20, steps=10, delay=30, weight="bold")
        
        details_label = ctk.CTkLabel(
            step_frame,
            text=details,
            text_color="white",
            font=ctk.CTkFont(family=PRO_FONT, size=16),
            justify="left"
        )
        details_label.grid(row=1, column=1, sticky="w")
        animate_label_font(details_label, start_size=10, target_size=16, steps=10, delay=30, weight="normal")
    
    steps = [
        {
            "title": "Gesture Recognition",
            "details": (
                "• Right hand for next slide\n"
                "• Left hand for previous slide\n"
                "• Thumbs up for starting presentation\n"
                "• Thumbs down for ending presentation\n"
                "• Say \"lock gesture\" to lock gestures\n"
                "• Say \"Resume gesture\" to continue using gesture"
            ),
            "icon": gesture_icon
        },
        {
            "title": "Voice Command",
            "details": (
                "• Say \"next\" for next slide\n"
                "• Say \"previous\" to go to previous slide\n"
                "• Say \"start presentation\" to start\n"
                "• Say \"stop presentation\" to stop\n"
                "• To go to a specific slide, say e.g., \"go to slide 2\""
            ),
            "icon": voice_icon
        },
        {
            "title": "Subtitles",
            "details": "• After clicking the button, start speaking and subtitles will be shown",
            "icon": subtitles_icon
        },
        {
            "title": "Customize Gesture",
            "details": (
                "• Select the option and perform the desired gesture in front of the camera\n"
                "• To use the customized gesture, click on \"use customized gesture\" button"
            ),
            "icon": customize_icon
        }
    ]
    
    def animate_steps(card, steps, index=0):
        if index < len(steps):
            step = steps[index]
            create_step(card, str(index+1), step["title"], step["details"], icon=step.get("icon"))
            card.after(300, lambda: animate_steps(card, steps, index+1))
    
    animate_steps(card, steps)
    
    main_control_window = main_window
    main_window.protocol("WM_DELETE_WINDOW", lambda: close_main_window(main_window, welcome_window))

def toggle_gesture_control():
    import backend.gesture_control as gc
    global gesture_active, voice_thread

    if not gesture_active[0]:
        gc.gesture_control_active = True
        gesture_active[0] = True
        messagebox.showinfo(
            "Gesture Control",
            "Gesture Control Activated!\nUse Left Swipe for previous slide\nUse Right Swipe for next slide"
        )
        gesture_thread = threading.Thread(target=gc.detect_gesture)
        gesture_thread.start()
        voice_thread = threading.Thread(target=gc.voice_command_listener)
        voice_thread.start()
    else:
        gc.gesture_control_active = False
        gesture_active[0] = False
        messagebox.showinfo("Gesture Control", "Gesture Control Deactivated!")

def toggle_voice_command():
    global voice_thread
    if voice_active[0]:
        voice_active[0] = False
        messagebox.showinfo("Voice Command", "Voice Command Deactivated!")
    else:
        voice_active[0] = True
        voice_thread = threading.Thread(target=listen_for_voice_command, args=(voice_active,))
        voice_thread.start()
        messagebox.showinfo(
            "Voice Command",
            "Voice Command Activated!\nSay 'next' to go to the next slide and 'previous' to go to the previous slide"
        )

def toggle_subtitles():
    global subtitles_active
    if subtitles_active[0]:
        from backend.subtitles import stop_subtitle
        stop_subtitle()
        subtitles_active[0] = False
        messagebox.showinfo("Subtitles", "Subtitles Deactivated!")
    else:
        subtitles_active[0] = True
        from backend.subtitles import start_subtitle
        start_subtitle(main_control_window)
        messagebox.showinfo("Subtitles", "Subtitles Activated!")

def toggle_translation():
    global translation_active
    if translation_active[0]:
        from backend.real_time_translation import stop_real_time_translation
        stop_real_time_translation()
        translation_active[0] = False
        messagebox.showinfo("Real-Time Translation", "Translation Deactivated!")
    else:
        open_translation_options(main_control_window)

def activate_customized_gesture():
    custom_thread = threading.Thread(target=use_customized_gesture)
    custom_thread.start()

def logout(main_window, welcome_window):
    voice_active[0] = False
    translation_active[0] = False  
    main_window.destroy()
    welcome_window.deiconify()

def close_main_window(main_window, welcome_window):
    voice_active[0] = False
    translation_active[0] = False  
    main_window.destroy()
    welcome_window.deiconify()

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    root = ctk.CTk()  # Dummy welcome window
    root.withdraw()
    open_main_window(root)
    root.mainloop()
