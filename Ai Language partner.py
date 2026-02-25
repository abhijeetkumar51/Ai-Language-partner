import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import pyttsx3
from deep_translator import GoogleTranslator
import os
import requests

# ================= CONFIG =================
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-pro:generateContent"
GEMINI_API_KEY = os.getenv("Your api key")

BG = "#f0f2f5"
CARD = "#ffffff"
PRIMARY = "#2d88ff"
SUCCESS = "#42b72a"
WARNING = "#ff7b00"


class AILanguagePartner:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Language Partner (No Mic Version)")
        self.root.geometry("980x760")
        self.root.configure(bg=BG)

        self.engine = pyttsx3.init()

        self.languages = {
            "English": "en",
            "Hindi": "hi",
            "Bengali": "bn",
            "Telugu": "te",
            "French": "fr",
            "Spanish": "es",
            "German": "de",
            "Japanese": "ja"
        }

        self.build_ui()

    # ================= UI =================
    def build_ui(self):
        header = tk.Frame(self.root, bg=PRIMARY, height=70)
        header.pack(fill="x")
        tk.Label(
            header,
            text="🤖 AI Language Partner",
            bg=PRIMARY,
            fg="white",
            font=("Segoe UI", 20, "bold")
        ).pack(pady=15)

        main = tk.Frame(self.root, bg=BG)
        main.pack(fill="both", expand=True, padx=20, pady=20)

        left = self.card(main)
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))

        right = self.card(main)
        right.pack(side="right", fill="both", expand=True, padx=(10, 0))

        self.build_left(left)
        self.build_right(right)

        self.status = tk.StringVar(value="Ready")
        tk.Label(self.root, textvariable=self.status,
                 relief="sunken", anchor="w").pack(fill="x")

    def card(self, parent):
        return tk.Frame(parent, bg=CARD, highlightthickness=1, highlightbackground="#ddd")

    # ================= LEFT =================
    def build_left(self, frame):
        tk.Label(frame, text="📝 Input Text", bg=CARD,
                 font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=10, pady=10)

        lang = tk.Frame(frame, bg=CARD)
        lang.pack(padx=10, pady=5, fill="x")

        self.src_lang = tk.StringVar(value="English")
        self.tgt_lang = tk.StringVar(value="Hindi")

        ttk.Combobox(lang, textvariable=self.src_lang,
                     values=list(self.languages),
                     state="readonly", width=15).pack(side="left", padx=5)

        ttk.Combobox(lang, textvariable=self.tgt_lang,
                     values=list(self.languages),
                     state="readonly", width=15).pack(side="left", padx=5)

        self.input_text = scrolledtext.ScrolledText(
            frame, height=8, font=("Segoe UI", 11))
        self.input_text.pack(fill="x", padx=10, pady=10)

        btns = tk.Frame(frame, bg=CARD)
        btns.pack(pady=10)

        self.make_btn(btns, "🌍 Translate", SUCCESS,
                      self.translate_text).pack(side="left", padx=5)
        self.make_btn(btns, "🧠 Ask AI", WARNING,
                      self.ask_ai).pack(side="left", padx=5)

    # ================= RIGHT =================
    def build_right(self, frame):
        tk.Label(frame, text="💬 Output", bg=CARD,
                 font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=10, pady=10)

        self.output_text = scrolledtext.ScrolledText(
            frame, height=7, font=("Segoe UI", 11))
        self.output_text.pack(fill="x", padx=10)

        self.make_btn(frame, "🔊 Speak Output", PRIMARY,
                      self.speak_output).pack(pady=8)

        tk.Label(frame, text="📜 Chat History", bg=CARD,
                 font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=10)

        self.chat = scrolledtext.ScrolledText(
            frame, height=15, state="disabled", font=("Segoe UI", 10))
        self.chat.pack(fill="both", expand=True, padx=10, pady=5)

    # ================= HELPERS =================
    def make_btn(self, parent, text, color, cmd):
        btn = tk.Button(
            parent, text=text, bg=color, fg="white",
            font=("Segoe UI", 10, "bold"),
            command=cmd, cursor="hand2", relief="flat"
        )
        btn.bind("<Enter>", lambda e: btn.config(bg="#000000"))
        btn.bind("<Leave>", lambda e: btn.config(bg=color))
        return btn

    # ================= FEATURES =================
    def translate_text(self):
        text = self.input_text.get("1.0", "end").strip()
        if not text:
            messagebox.showwarning("Warning", "Please enter text")
            return

        try:
            src = self.languages[self.src_lang.get()]
            tgt = self.languages[self.tgt_lang.get()]
            translated = GoogleTranslator(
                source=src, target=tgt).translate(text)

            self.output_text.delete("1.0", "end")
            self.output_text.insert("end", translated)

            self.add_chat(f"🧑 You: {text}")
            self.add_chat(f"🌍 Translation: {translated}")

        except Exception:
            messagebox.showerror("Error", "Translation failed")

    def ask_ai(self):
        if not GEMINI_API_KEY:
            messagebox.showerror(
                "Error", "Gemini API key not set")
            return

        text = self.input_text.get("1.0", "end").strip()
        if not text:
            return

        self.add_chat(f"🧑 You: {text}")
        self.status.set("Thinking...")

        try:
            res = requests.post(
                f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
                json={"contents": [{"parts": [{"text": text}]}]},
                timeout=10
            ).json()

            ai = res["candidates"][0]["content"]["parts"][0]["text"]

            self.output_text.delete("1.0", "end")
            self.output_text.insert("end", ai)
            self.add_chat(f"🤖 AI: {ai}")

        except Exception:
            messagebox.showerror("Error", "AI failed")
        finally:
            self.status.set("Ready")

    def speak_output(self):
        text = self.output_text.get("1.0", "end").strip()
        if text:
            self.engine.say(text)
            self.engine.runAndWait()

    def add_chat(self, msg):
        self.chat.config(state="normal")
        self.chat.insert("end", msg + "\n\n")
        self.chat.config(state="disabled")
        self.chat.see("end")


# ================= RUN =================
if __name__ == "__main__":
    root = tk.Tk()
    AILanguagePartner(root)
    root.mainloop()
