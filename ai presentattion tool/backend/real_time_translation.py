import threading
import tkinter as tk
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from tkinter import messagebox

import speech_recognition as sr
from deep_translator import GoogleTranslator


class SpeechTranslatorWithSubtitles:
    def __init__(self, recognizer_language="en", target_language="hi", parent=None):
        """Initialize the translator, recognizer, and GUI."""
        self.recognizer_language = recognizer_language
        translator_source = "hi" if recognizer_language.lower().startswith("hi") else recognizer_language

        # Create and pre-warm the translator
        self.translator = GoogleTranslator(source=translator_source, target=target_language)
        try:
            self.translator.translate("hello")
        except Exception as e:
            print("Translator warmup failed:", e)

        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

        # Cache for translations
        self.translation_cache = {}

        # Thread pool for processing tasks
        self.executor = ThreadPoolExecutor(max_workers=4)

        # Set up the subtitle window
        self.root = tk.Tk() if parent is None else tk.Toplevel(parent)
        self.root.title("Live Subtitles")
        self.root.attributes("-topmost", True)
        self.root.attributes('-alpha', 0.7)
        self.root.overrideredirect(True)
        self.root.configure(bg="black")

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"{screen_width}x100+0+{screen_height - 120}")

        self.subtitle_label = tk.Label(
            self.root, text="Waiting for speech...",
            font=("Arial", 32), fg="white", bg="black",
            wraplength=screen_width, anchor="s", pady=10
        )
        self.subtitle_label.pack(expand=True, fill="both")

        self.translation_active = False
        self.stop_listening = None

    def callback(self, recognizer, audio):
        """Called in the background; submit audio processing to the executor."""
        self.executor.submit(self.process_audio, recognizer, audio)

    def process_audio(self, recognizer, audio):
        """Recognize speech and submit translation to the executor."""
        try:
            text = recognizer.recognize_google(audio, language=self.recognizer_language)
            print(f"🔹 Recognized: {text}")
            self.executor.submit(self.translate_and_update, text)
        except sr.UnknownValueError:
            self.display_subtitle("Could not understand audio")
        except sr.RequestError:
            self.display_subtitle("Speech Recognition service unavailable")
        except Exception as e:
            print(f"⚠️ Recognition error: {e}")

    def translate_and_update(self, text):
        """Translate text using a timeout and update the subtitle."""
        if text in self.translation_cache:
            translated_text = self.translation_cache[text]
            print(f"🌍 Cached translation: {translated_text}")
            self.display_subtitle(translated_text)
            return

        # Use the executor to run the translator with a timeout
        future = self.executor.submit(self.translator.translate, text)
        try:
            translated_text = future.result(timeout=3)
        except TimeoutError:
            translated_text = "Translation timed out"
        except Exception as e:
            print(f"⚠️ Translation error: {e}")
            translated_text = "Translation error"

        self.translation_cache[text] = translated_text
        print(f"🌍 Translated: {translated_text}")
        self.display_subtitle(translated_text)

    def display_subtitle(self, text):
        """Safely update the subtitle label on the main thread."""
        self.root.after(0, lambda: self.subtitle_label.config(text=text))

    def start_translation(self):
        """Begin background listening for speech."""
        if self.translation_active:
            messagebox.showinfo("Translation", "Translation is already running!")
            return

        self.translation_active = True
        # Set phrase_time_limit to 3 seconds for faster turnaround
        self.stop_listening = self.recognizer.listen_in_background(
            self.microphone, self.callback, phrase_time_limit=3
        )
        messagebox.showinfo("Translation", "Translation started! Speak now.")

    def stop_translation(self):
        """Stop listening and shut down the translator."""
        if self.translation_active and self.stop_listening is not None:
            self.stop_listening(wait_for_stop=False)
            self.translation_active = False
            self.executor.shutdown(wait=False)
            self.root.after(100, self.root.destroy)

    def run(self):
        """Run the main GUI event loop."""
        self.root.mainloop()

def start_real_time_translation(recognizer_language, target_language, parent=None):
    translator_instance = SpeechTranslatorWithSubtitles(recognizer_language, target_language, parent)
    translator_instance.start_translation()
    if parent is None:
        translator_instance.run()

def stop_real_time_translation():
    # Implementation depends on how you manage the instance globally.
    pass

if __name__ == "__main__":
    rec_lang = "en"
    target_lang = "hi"
    translator = SpeechTranslatorWithSubtitles(rec_lang, target_lang)
    translator.run()
