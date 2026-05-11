import pygame
import random
import asyncio
import edge_tts
import os
from dotenv import dotenv_values

# Get the current directory (where the script is located)
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Ensure required directories exist
os.makedirs(os.path.join(current_dir, "Data"), exist_ok=True)
os.makedirs(os.path.join(current_dir, "Frontend", "Files"), exist_ok=True)

# Load environment variables
env_vars = dotenv_values(os.path.join(current_dir, ".env"))
AssistantVoice = env_vars.get("AssistantVoice", "en-CA-LiamNeural")  # Default voice if not found

async def TextToAudioFile(text) -> None:
    try:
        file_path = os.path.join(current_dir, "Data", "speech.mp3")

        # Ensure the directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Remove existing file if it exists
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Warning: Could not remove existing speech file: {e}")

        # Generate speech
        communicate = edge_tts.Communicate(text, AssistantVoice, pitch='+5Hz', rate='+13%')
        await communicate.save(file_path)
        
        # Verify file was created
        if not os.path.exists(file_path):
            raise Exception("Speech file was not created successfully")
            
    except Exception as e:
        print(f"Error in TextToAudioFile: {e}")
        raise

def TTS(Text, func=lambda r=None: True):
    try:
        # Generate audio file
        asyncio.run(TextToAudioFile(Text))
        
        # Initialize pygame mixer
        try:
            pygame.mixer.quit()  # Clean up any existing pygame mixer
        except:
            pass
            
        pygame.mixer.init(frequency=44100)
        
        # Load and play audio
        file_path = os.path.join(current_dir, "Data", "speech.mp3")
        pygame.mixer_music.load(file_path)
        pygame.mixer_music.play()

        # Wait for playback to complete
        while pygame.mixer.music.get_busy():
            if func() == False:
                break
            pygame.time.Clock().tick(10)

        return True

    except Exception as e:
        print(f"Error in TTS: {e}")
        return False

    finally:
        try:
            func(False)
            pygame.mixer.music.stop()
            pygame.mixer.quit()
        except Exception as e:
            print(f"Error in cleanup: {e}")

def TextToSpeech(Text, func=lambda r=None: True):
    if not Text or not isinstance(Text, str):
        print("Warning: Invalid text input")
        return False

    try:
        Data = Text.split(".")
        
        # Handle long text
        if len(Data) > 4 and len(Text) > 250:
            short_text = " ".join(Text.split(".")[0:2]) + ". "
            response = random.choice([
                "The rest of the result has been printed to the chat screen.",
                "You can find the complete text on the chat screen.",
                "Please check the chat screen for the full response.",
                "The remaining information is available on your screen."
            ])
            return TTS(short_text + response, func)
        else:
            return TTS(Text, func)
            
    except Exception as e:
        print(f"Error in TextToSpeech: {e}")
        return False

if __name__ == "__main__":
    while True:
        try:
            text = input("Enter the text: ")
            if text.lower() in ['exit', 'quit']:
                break
            TextToSpeech(text)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")