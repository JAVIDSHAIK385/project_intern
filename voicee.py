#!/usr/bin/env python3
"""
Ammu Voice Assistant in Python
Features:
- Hotword support ("Ammu" optional)
- Tell time/date
- Open websites
- Google search
- Play YouTube videos
- Wikipedia summaries
- Tell jokes
- Basic small talk & exit commands

Setup:
    pip install -r requirements.txt
Notes:
    - For Windows: if "pyaudio" fails, try:
        pip install pipwin && pipwin install pyaudio
    - For Linux: install PortAudio dev headers first (e.g., Ubuntu/Debian):
        sudo apt-get install portaudio19-dev python3-pyaudio
"""

import datetime
import webbrowser
import sys
import os
import re

import pyttsx3
import speech_recognition as sr
import wikipedia
import pywhatkit
import pyjokes

# --------------------- Configuration ---------------------
WAKEWORD_ENABLED = False         # Set to True to require "janu" in the command
WAKEWORD = "Ammu"
LANG = "en-in"                   # ASR language code (e.g., "en-US", "en-IN")
SPEECH_RATE = 180                # TTS rate (words per minute)
VOICE_PREFERENCE = "male"      # "male" or "female" if available

# --------------------- Speech (TTS) ----------------------
engine = pyttsx3.init()
engine.setProperty("rate", SPEECH_RATE)

def _pick_voice(preference: str = "male"):
    """Try to select a male/female voice if present."""
    try:
        voices = engine.getProperty("voices")
        pref = preference.lower().strip()
        for v in voices:
            name = (v.name or "").lower()
            if pref == "female" and ("female" in name or "zira" in name or "female" in str(v)):
                engine.setProperty("voice", v.id)
                return
            if pref == "male" and ("male" in name or "david" in name or "male" in str(v)):
                engine.setProperty("voice", v.id)
                return
        # Fallback: just keep default
    except Exception:
        pass

_pick_voice(VOICE_PREFERENCE)

def speak(text: str):
    print(f"[Janu]: {text}")
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"(TTS error: {e})")

# --------------------- Listen (STT) ----------------------
rec = sr.Recognizer()

def listen(timeout: float = 5.0, phrase_time_limit: float = 8.0) -> str:
    with sr.Microphone() as source:
        print("Listening...")
        rec.adjust_for_ambient_noise(source, duration=0.5)
        audio = rec.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
    try:
        query = rec.recognize_google(audio, language=LANG)
        print(f"[User]: {query}")
        return query.lower().strip()
    except sr.WaitTimeoutError:
        return ""
    except sr.UnknownValueError:
        speak("Sorry, I didn't catch that.")
        return ""
    except sr.RequestError as e:
        speak("Speech service is not available right now.")
        print(f"(ASR RequestError: {e})")
        return ""

# --------------------- Utilities -------------------------
def today_str():
    now = datetime.datetime.now()
    return now.strftime("%A, %d %B %Y")

def time_str():
    now = datetime.datetime.now()
    return now.strftime("%I:%M %p")

def normalize(q: str) -> str:
    q = q.strip()
    if q.startswith(WAKEWORD):
        q = q[len(WAKEWORD):].lstrip(",. ").strip()
    q = re.sub(r"^(hey|hi|hello)\s+", "", q)
    return q

def ensure_http(url: str) -> str:
    if not url.startswith(("http://", "https://")):
        return "https://" + url
    return url

# --------------------- Command Handlers ------------------
def handle_open(q: str) -> bool:
    m = re.search(r"open\s+(.*)", q)
    if not m:
        return False
    target = m.group(1).strip()
    if not target:
        return False

    shortcuts = {
        "youtube": "https://youtube.com",
        "google": "https://google.com",
        "gmail": "https://mail.google.com",
        "github": "https://github.com",
        "stackoverflow": "https://stackoverflow.com",
    }
    if target in shortcuts:
        webbrowser.open(shortcuts[target])
        speak(f"Opening {target}.")
        return True

    target = target.replace(" dot ", ".").replace(" ", "")
    webbrowser.open(ensure_http(target))
    speak(f"Opening {target}.")
    return True

def handle_time_date(q: str) -> bool:
    if any(k in q for k in ["time", "what's the time", "current time"]):
        speak(f"The time is {time_str()}.")
        return True
    if any(k in q for k in ["date", "today", "what's the date"]):
        speak(f"Today is {today_str()}.")
        return True
    return False

def handle_youtube_play(q: str) -> bool:
    if q.startswith("play "):
        query = q[5:].strip()
        if not query:
            return False
        speak(f"Playing {query} on YouTube.")
        try:
            pywhatkit.playonyt(query)
        except Exception as e:
            speak("I couldn't open YouTube for that right now.")
            print(f"(YouTube error: {e})")
        return True
    if q.startswith("youtube "):
        query = q[len("youtube "):].strip()
        if not query:
            return False
        speak(f"Searching YouTube for {query}.")
        try:
            pywhatkit.playonyt(query)
        except Exception as e:
            speak("I couldn't open YouTube for that right now.")
            print(f"(YouTube error: {e})")
        return True
    return False

def handle_wikipedia(q: str) -> bool:
    if q.startswith("wikipedia "):
        topic = q[len("wikipedia "):].strip()
    elif q.startswith(("who is ", "what is ", "tell me about ")):
        topic = re.sub(r"^(who is|what is|tell me about)\s+", "", q).strip()
    else:
        return False

    if not topic:
        return False

    try:
        wikipedia.set_lang("en")
        summary = wikipedia.summary(topic, sentences=2, auto_suggest=True, redirect=True)
        speak(summary)
    except Exception as e:
        speak("I couldn't find a good summary for that.")
        print(f"(Wikipedia error: {e})")
    return True

def handle_google_search(q: str) -> bool:
    m = re.search(r"(search for|google)\s+(.*)", q)
    if not m:
        return False
    query = m.group(2).strip()
    if not query:
        return False
    speak(f"Searching Google for {query}.")
    webbrowser.open(f"https://www.google.com/search?q={query.replace(' ', '+')}")
    return True

def handle_joke(q: str) -> bool:
    if "joke" in q:
        try:
            joke = pyjokes.get_joke()
            speak(joke)
        except Exception:
            speak("Here's one: Why do programmers prefer dark mode? Because light attracts bugs.")
        return True
    return False

def handle_smalltalk(q: str) -> bool:
    if any(k in q for k in ["how are you", "how are you doing"]):
        speak("I'm running at full capacity. Thanks for asking!")
        return True
    if "your name" in q:
        speak("I'm Ammu, your Python assistant.")
        return True
    return False

def is_exit(q: str) -> bool:
    return any(k in q for k in ["exit", "quit", "goodbye", "stop", "sleep", "shutdown"])

# --------------------- Main Loop -------------------------
def main():
    speak("Ammu ready. How can I help you?")
    while True:
        try:
            said = listen()
            if not said:
                continue

            if WAKEWORD_ENABLED and WAKEWORD not in said:
                continue

            said = normalize(said)

            if is_exit(said):
                speak("Goodbye!")
                break

            if handle_time_date(said):     continue
            if handle_open(said):          continue
            if handle_youtube_play(said):  continue
            if handle_wikipedia(said):     continue
            if handle_google_search(said): continue
            if handle_joke(said):          continue
            if handle_smalltalk(said):     continue

            speak("Let me search that on Google.")
            webbrowser.open(f"https://www.google.com/search?q={said.replace(' ', '+')}")

        except KeyboardInterrupt:
            speak("Stopping now. Bye!")
            break
        except Exception as e:
            print(f"(Loop error: {e})")
            speak("I ran into an error with that command.")

if __name__ == "__main__":
    main()
