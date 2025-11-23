import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import pyttsx3
import speech_recognition as sr
import googletrans
from googletrans import Translator
import threading
import os
from PIL import Image, ImageTk
import requests
import webbrowser

# Gemini API configuration
GEMINI_API_KEY = "AIzaSyCU8_L43XMChklCbKsRYzr8DzRD2LIhjmw"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-pro:generateContent"

class AILanguagePartner:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Language Partner")
        self.root.geometry("950x750")
        self.root.configure(bg="#f0f2f5")
        
        # Initialize components
        self.translator = Translator()
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        
        # Set default values
        self.source_lang = "en"
        self.target_lang = "hi"
        self.is_listening = False
        self.chat_history = []
        
        # Load languages
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
        
        # Create UI
        self.create_widgets()
        
    def create_widgets(self):
        # Header with gradient background
        header_frame = tk.Frame(self.root, bg="#2d88ff", height=80)
        header_frame.pack(fill="x")
        
        title_label = tk.Label(header_frame, text="AI Language Partner", 
                             font=("Helvetica", 20, "bold"), 
                             fg="white", bg="#2d88ff")
        title_label.pack(pady=20)
        
        # Main content frame
        main_frame = tk.Frame(self.root, bg="#f0f2f5", padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        # Left panel - Input and controls
        left_panel = tk.Frame(main_frame, bg="#ffffff", bd=2, relief="groove", padx=10, pady=10)
        left_panel.pack(side="left", fill="both", expand=True)
        
        # Language selection
        lang_frame = tk.Frame(left_panel, bg="#ffffff")
        lang_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(lang_frame, text="From:", bg="#ffffff").pack(side="left", padx=(0, 5))
        self.source_lang_var = tk.StringVar(value="English")
        self.source_lang_menu = ttk.Combobox(lang_frame, textvariable=self.source_lang_var, 
                                           values=list(self.languages.keys()), state="readonly")
        self.source_lang_menu.pack(side="left", padx=(0, 20))
        
        tk.Label(lang_frame, text="To:", bg="#ffffff").pack(side="left", padx=(0, 5))
        self.target_lang_var = tk.StringVar(value="Hindi")
        self.target_lang_menu = ttk.Combobox(lang_frame, textvariable=self.target_lang_var, 
                                           values=list(self.languages.keys()), state="readonly")
        self.target_lang_menu.pack(side="left")
        
        # Input text area
        tk.Label(left_panel, text="Enter your text:", bg="#ffffff", anchor="w").pack(fill="x", pady=(10, 5))
        self.input_text = scrolledtext.ScrolledText(left_panel, height=8, font=("Helvetica", 12), wrap="word")
        self.input_text.pack(fill="x")
        
        # Button frame with hover effects
        button_frame = tk.Frame(left_panel, bg="#ffffff")
        button_frame.pack(fill="x", pady=10)
        
        # Voice input button with animation
        self.mic_img = ImageTk.PhotoImage(Image.open("mic.png").resize((20, 20))) if os.path.exists("mic.png") else None
        self.voice_btn = tk.Button(button_frame, text=" Speak", image=self.mic_img if self.mic_img else None, 
                                  compound="left", command=self.toggle_listening, 
                                  bg="#2d88ff", fg="white", font=("Helvetica", 12, "bold"),
                                  activebackground="#1a73e8", cursor="hand2")
        self.voice_btn.pack(side="left", padx=(0, 10))
        
        # Translate button with hover effect
        self.translate_btn = tk.Button(button_frame, text="Translate", command=self.translate_text, 
                                     bg="#42b72a", fg="white", font=("Helvetica", 12, "bold"),
                                     activebackground="#36a420", cursor="hand2")
        self.translate_btn.pack(side="left", padx=(0, 10))
        
        # Ask AI button with hover effect
        self.ai_btn = tk.Button(button_frame, text="Ask AI", command=self.ask_ai, 
                               bg="#ff7b00", fg="white", font=("Helvetica", 12, "bold"),
                               activebackground="#e66400", cursor="hand2")
        self.ai_btn.pack(side="left")
        
        # Right panel - Output and chat
        right_panel = tk.Frame(main_frame, bg="#ffffff", bd=2, relief="groove", padx=10, pady=10)
        right_panel.pack(side="right", fill="both", expand=True)
        
        # Output text area
        tk.Label(right_panel, text="Translation:", bg="#ffffff", anchor="w").pack(fill="x", pady=(0, 5))
        self.output_text = scrolledtext.ScrolledText(right_panel, height=8, font=("Helvetica", 12), wrap="word")
        self.output_text.pack(fill="x")
        
        # Speak translation button with hover effect
        self.speak_btn = tk.Button(right_panel, text="🔊 Speak Translation", command=self.speak_translation, 
                                 bg="#2d88ff", fg="white", font=("Helvetica", 10, "bold"),
                                 activebackground="#1a73e8", cursor="hand2")
        self.speak_btn.pack(pady=5)
        
        # Chat history
        tk.Label(right_panel, text="Chat History:", bg="#ffffff", anchor="w").pack(fill="x", pady=(10, 5))
        self.chat_display = scrolledtext.ScrolledText(right_panel, height=12, font=("Helvetica", 11), wrap="word")
        self.chat_display.pack(fill="both", expand=True)
        self.chat_display.config(state="disabled")
        
        # Gemini API connection
        api_frame = tk.Frame(self.root, bg="#f0f2f5", padx=20, pady=10)
        api_frame.pack(fill="x")
        
        self.api_key_var = tk.StringVar(value=GEMINI_API_KEY)
        tk.Label(api_frame, text="Gemini API Key:", bg="#f0f2f5").pack(side="left")
        self.api_key_entry = tk.Entry(api_frame, textvariable=self.api_key_var, width=50, show="*")
        self.api_key_entry.pack(side="left", padx=5)
        self.api_connect_btn = tk.Button(api_frame, text="🔌 Connect", command=self.connect_gemini, 
                                       bg="#333333", fg="white", font=("Helvetica", 10, "bold"),
                                       activebackground="#222222", cursor="hand2")
        self.api_connect_btn.pack(side="left")
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = tk.Label(self.root, textvariable=self.status_var, bd=1, relief="sunken", anchor="w")
        status_bar.pack(side="bottom", fill="x")
        
        # Creator credit text box with enhanced styling
        creator_frame = tk.Frame(self.root, bg="#2d88ff", bd=1, relief="solid")
        creator_frame.pack(side="bottom", fill="x", padx=10, pady=(0, 5))
        
        creator_text = tk.Text(creator_frame, height=1, font=("Helvetica", 12, "bold"), 
                             bg="#2d88ff", fg="white", wrap="word", padx=10, pady=5,
                             bd=0, highlightthickness=0)
        creator_text.insert("1.0", "🌟 This chatbot is created by Abhijeet Kumar (Registration No: 12303503) 🌟")
        creator_text.config(state="disabled")
        creator_text.pack(fill="x")
        
        # Make creator text interactive
        creator_text.bind("<Enter>", lambda e: creator_text.config(bg="#1a73e8"))
        creator_text.bind("<Leave>", lambda e: creator_text.config(bg="#2d88ff"))
        creator_text.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/abhijeetkumar"))
        creator_text.config(cursor="hand2")
    
    def toggle_listening(self):
        if not self.is_listening:
            self.is_listening = True
            self.voice_btn.config(text=" Listening...", bg="#ff0000")
            self.status_var.set("Listening... Speak now")
            threading.Thread(target=self.listen_for_speech, daemon=True).start()
        else:
            self.is_listening = False
            self.voice_btn.config(text=" Speak", bg="#2d88ff")
            self.status_var.set("Ready")
    
    def listen_for_speech(self):
        with sr.Microphone() as source:
            try:
                audio = self.recognizer.listen(source, timeout=5)
                text = self.recognizer.recognize_google(audio)
                self.input_text.insert("end", text + " ")
                self.status_var.set("Speech recognized")
            except sr.UnknownValueError:
                self.status_var.set("Could not understand audio")
            except sr.RequestError as e:
                self.status_var.set(f"Error: {str(e)}")
            except Exception as e:
                self.status_var.set(f"Error: {str(e)}")
        
        self.is_listening = False
        self.voice_btn.config(text=" Speak", bg="#2d88ff")
    
    def translate_text(self):
        text = self.input_text.get("1.0", "end").strip()
        if not text:
            messagebox.showwarning("Warning", "Please enter some text to translate")
            return
        
        try:
            source = self.languages[self.source_lang_var.get()]
            target = self.languages[self.target_lang_var.get()]
            
            translated = self.translator.translate(text, src=source, dest=target)
            self.output_text.delete("1.0", "end")
            self.output_text.insert("end", translated.text)
            
            # Add to chat history
            self.add_to_chat(f"You ({self.source_lang_var.get()}): {text}")
            self.add_to_chat(f"Translation ({self.target_lang_var.get()}): {translated.text}")
            
            self.status_var.set("Translation complete")
        except Exception as e:
            messagebox.showerror("Error", f"Translation failed: {str(e)}")
            self.status_var.set("Translation failed")
    
    def ask_ai(self):
        text = self.input_text.get("1.0", "end").strip()
        if not text:
            messagebox.showwarning("Warning", "Please enter a question or message")
            return
        
        # Add user message to chat
        self.add_to_chat(f"You: {text}")
        
        # Check if Gemini API is connected
        if not self.api_key_var.get() or self.api_key_var.get() == "YOUR_GEMINI_API_KEY":
            messagebox.showwarning("Warning", "Please connect to Gemini API first")
            return
        
        try:
            self.status_var.set("Asking AI...")
            
            # Call Gemini API
            headers = {"Content-Type": "application/json"}
            data = {
                "contents": [{
                    "parts": [{
                        "text": text
                    }]
                }]
            }
            
            response = requests.post(
                f"{GEMINI_API_URL}?key={self.api_key_var.get()}",
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and result['candidates']:
                    ai_response = result['candidates'][0]['content']['parts'][0]['text']
                    self.output_text.delete("1.0", "end")
                    self.output_text.insert("end", ai_response)
                    self.add_to_chat(f"AI: {ai_response}")
                    self.status_var.set("AI response received")
                else:
                    messagebox.showerror("Error", "No response from AI")
                    self.status_var.set("AI response error")
            else:
                messagebox.showerror("Error", f"API request failed: {response.text}")
                self.status_var.set("API request failed")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get AI response: {str(e)}")
            self.status_var.set("AI request failed")
    
    def speak_translation(self):
        text = self.output_text.get("1.0", "end").strip()
        if text:
            try:
                self.engine.say(text)
                self.engine.runAndWait()
                self.status_var.set("Speaking translation")
            except Exception as e:
                messagebox.showerror("Error", f"Text-to-speech failed: {str(e)}")
                self.status_var.set("Speech failed")
    
    def add_to_chat(self, message):
        self.chat_display.config(state="normal")
        self.chat_display.insert("end", message + "\n\n")
        self.chat_display.config(state="disabled")
        self.chat_display.see("end")
        self.chat_history.append(message)
    
    def connect_gemini(self):
        api_key = self.api_key_var.get().strip()
        if not api_key or api_key == "YOUR_GEMINI_API_KEY":
            messagebox.showwarning("Warning", "Please enter a valid Gemini API key")
            return
        
        # Simple test connection
        try:
            self.status_var.set("Connecting to Gemini API...")
            headers = {"Content-Type": "application/json"}
            data = {"contents": [{"parts": [{"text": "test"}]}]}
            
            response = requests.post(
                f"{GEMINI_API_URL}?key={api_key}",
                headers=headers,
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                messagebox.showinfo("Success", "Successfully connected to Gemini API")
                self.status_var.set("Connected to Gemini API")
                self.api_key_entry.config(show="")
            else:
                messagebox.showerror("Error", f"Connection failed: {response.text}")
                self.status_var.set("Connection failed")
        except Exception as e:
            messagebox.showerror("Error", f"Connection failed: {str(e)}")
            self.status_var.set("Connection failed")

if __name__ == "__main__":
    root = tk.Tk()
    app = AILanguagePartner(root)

    root.mainloop()
