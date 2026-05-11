# Running Jarvis

This document covers two run modes:

1. **Real desktop run** — the way the project is designed to be used.
2. **Headless sanity check** — what's possible in a container/CI with no display, mic, or speakers. Useful for verifying imports and the missing-file fixes, not for actually talking to Jarvis.

## What we fixed in this branch

The upstream zip at `Thechallangers/Jarvis` ships broken in two ways:

1. **`Main.py` imports `Backend.EmailIntegration`, which is not in the zip.**  Without it the assistant crashes on first import. This branch adds a stdlib-only `Backend/EmailIntegration.py` that matches the interface Main.py expects (`EmailClient.check_emails`, `summarize_emails`, `send_email`). It reads IMAP/SMTP creds from `.env`; if they are missing it returns a friendly "not configured" message instead of crashing.
2. **`Requirements.txt` says `pyQt5`, but `Frontend/GUI.py` actually imports `PyQt6`.**  Switched the requirement to `PyQt6`.

We also created `Data/ChatLog.json` (empty list), which `Chatbot.py` and `Main.py` open at startup.

## 1) Real desktop run

You need a machine with a screen, a working microphone, and a working audio output. Linux/macOS/Windows all work; the upstream is developed on macOS (the zip ships `.DS_Store` and `__MACOSX/` sidecars).

```bash
git clone <this repo>
cd llama2_local/jarvis
python -m venv .venv
source .venv/bin/activate           # Windows: .venv\Scripts\activate
pip install -r Requirements.txt
```

Fill in `.env`:

```env
username=YourName
Assistantname=Jarvis
GroqAPIKey=gsk_...                  # https://console.groq.com
CO_API_KEY=...                      # https://dashboard.cohere.com
HuggingFaceAPIKey=hf_...            # https://huggingface.co/settings/tokens (image generation)
AssistantVoice=en-CA-LiamNeural     # any edge-tts voice
InputLanguage=en-US

# Optional, only needed for /email commands
EmailAddress=you@gmail.com
EmailPassword=<app password, not your account password>
ImapHost=imap.gmail.com
ImapPort=993
SmtpHost=smtp.gmail.com
SmtpPort=587
```

You also need **Chrome (or Chromium) installed system-wide** — `Backend/SpeechToText.py` drives Chrome via Selenium and uses the browser's Web Speech API for transcription. `webdriver-manager` will download a matching chromedriver on first run.

```bash
python Main.py
```

A PyQt6 window opens. Click the microphone to start listening.

## 2) Headless sanity check (container / CI)

A container has no display, no microphone, and no speakers, so the *full* assistant cannot run. But you can verify the install and exercise the text path:

### Install

```bash
pip install -r Requirements.txt
```

### Smoke tests that work in a container

These exercise the modules we can without a display:

```bash
# Module-import smoke test (no API calls)
python smoke_test.py

# Text-only chatbot loop (requires GroqAPIKey)
python -m Backend.Chatbot
```

### Booting the GUI under a virtual display (best-effort)

```bash
# 1) Start a virtual X server
Xvfb :99 -screen 0 1280x720x24 &
export DISPLAY=:99

# 2) PyQt6 will refuse to start without an audio output; if you want to bypass
#    pulseaudio entirely you can also set:
export QT_QPA_PLATFORM=offscreen

# 3) Launch Jarvis (will not be able to record speech — no audio device)
python Main.py
```

`QT_QPA_PLATFORM=offscreen` lets PyQt6 render to an off-screen buffer, which is enough to confirm the UI initializes without crashing. You won't see the window, and any speech-recognition call will fail because there is no microphone.

## What still needs real hardware/services

| Component | Needs | Why |
|-----------|-------|-----|
| `Frontend/GUI.py` | Display server (X11/Wayland/Cocoa/Win32) | PyQt6 widgets |
| `Backend/SpeechToText.py` | Chrome + microphone | Web Speech API in Chrome via Selenium |
| `Backend/TextToSpeech.py` | Audio output device | pygame.mixer playback of edge-tts output |
| `Backend/RealtimeSearchEngine.py` | Internet + Cohere/Groq keys + Chrome | Selenium-driven Google results scrape |
| `Backend/ImageGeneration.py` | Hugging Face API key | calls a HF inference endpoint |
| `Backend/EmailIntegration.py` (new) | IMAP/SMTP creds in `.env` | optional; returns a friendly error if absent |
| `Backend/Automation.py` | Desktop OS APIs (AppOpener, pywhatkit) | opens applications and websites |

## Security reminder

The upstream zip ships a real Hugging Face token in its `.env`. We blanked it in our import commit. **Rotate the token at <https://huggingface.co/settings/tokens>** if it belongs to you.
