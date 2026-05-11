from Frontend.GUI import (
    GraphicalUserInterface,
    SetAssistantStatus,
    ShowTextToScreen,
    get_temp_path,
    SetMicroPhoneStatus,
    AnswerModifier,
    QueryModifier,
    GetMicroPhoneStatus,
    GetAssistantStatus
)
from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation
from Backend.SpeechToText import SpeechRecognition
from Backend.Chatbot import ChatBot
from Backend.TextToSpeech import TextToSpeech
from Backend.EmailIntegration import EmailClient
from dotenv import dotenv_values
from asyncio import run
import subprocess
import threading
import json
import os
import time
import re

env_vars = dotenv_values(".env")
Username = env_vars.get("username", "User")
Assistantname = env_vars.get("Assistantname", "Jarvis")

DefaultMessage = f'''{Username} : Hello {Assistantname}, How are you?
{Assistantname} : Welcome {Username}. I am doing well. How may i help you?'''

subprocesses = []
Functions = ["open", "close", "play", "system", "content", "google search", "youtube search"]

def ShowDefaultChatIfNoChats():
    with open(os.path.join('Data', 'ChatLog.json'), 'r', encoding='utf-8') as file:
        if len(file.read()) <= 5:
            with open(get_temp_path('Database.data'), 'w', encoding='utf-8') as file:
                file.write(DefaultMessage)

            with open(get_temp_path('Responses.data'), 'w', encoding='utf-8') as file:
                file.write("")
                
def ReadChatLogJson():
    with open(os.path.join('Data', 'ChatLog.json'), 'r', encoding='utf-8') as file:
        chatlog_data = json.load(file)
    return chatlog_data

def ChatLogIntegration():
    json_data = ReadChatLogJson()
    formatted_chatlog = ""
    for entry in json_data:
        if entry["role"] == "user":
            formatted_chatlog += f"User: {entry['content']}\n"
        elif entry["role"] == "assistant":
            formatted_chatlog += f"Assistant: {entry['content']}\n"
    formatted_chatlog = formatted_chatlog.replace("User", Username + " ")
    formatted_chatlog = formatted_chatlog.replace("Assistant", Assistantname + " ")

    with open(get_temp_path('Database.data'), 'w', encoding='utf-8') as file:
        file.write(AnswerModifier(formatted_chatlog))


def ShowChatsOnGUI():
    try:
        with open(get_temp_path('Database.data'), 'r', encoding='utf-8') as file:
            Data = file.read()
            if len(Data.strip()) > 0:
                # No need to split and join if we're just reading and writing the same content
                with open(get_temp_path('Database.data'), 'w', encoding='utf-8') as write_file:
                    write_file.write(Data)
    except Exception as e:
        print(f"Error in ShowChatsOnGUI: {e}")

def InitialExecution():
    try:
        # Create necessary directories
        os.makedirs('Data', exist_ok=True)
        os.makedirs(os.path.join('Frontend', 'Files'), exist_ok=True)
        
        # Initialize status files with correct initial states
        SetAssistantStatus("Available...")
        SetMicroPhoneStatus("True")  # Start with microphone enabled
        
        # Initialize chat history
        ShowTextToScreen("")  # Clear any existing text
        ShowDefaultChatIfNoChats()  # Set default chat if none exists
        ChatLogIntegration()  # Load chat history from JSON
        ShowChatsOnGUI()  # Display chats on GUI
        
        # Create empty response file
        with open(get_temp_path('Responses.data'), 'w', encoding='utf-8') as file:
            file.write("")
            
        print("Initialization complete - System is ready")
    except Exception as e:
        print(f"Error in InitialExecution: {e}")

# Make sure InitialExecution runs before threads start
InitialExecution()

def MainExecution():
    TaskExecution = False
    ImageExecution = False
    ImageGenerationQuery = ""
    EmailExecution = False

    SetAssistantStatus("Listening ...")
    Query = SpeechRecognition()
    print(f"\nReceived Query: {Query}")
    ShowTextToScreen(f"{Username} : {Query}")

    SetAssistantStatus("Thinking ...")
    Decision = FirstLayerDMM(Query)
    print(f"\nDecision from Model: {Decision}")  # Debug print

    G = any(i for i in Decision if i.startswith("general"))
    R = any(i for i in Decision if i.startswith("realtime"))
    print(f"General query: {G}, Realtime query: {R}")  # Debug print

    Merged_query = " and ".join(
    [" ".join(i.split()[1:]) for i in Decision if i.startswith("general") or i.startswith("realtime")]
    )
    print(f"Merged query: {Merged_query}")  # Debug print

    # Handle image generation
    for queries in Decision:
        if "generate" in queries:
            # Extract the actual image description by removing "generate" and any extra spaces
            ImageGenerationQuery = queries.replace("generate", "").strip()
            ImageExecution = True
            print(f"Image generation requested: {ImageGenerationQuery}")  # Debug print

    # Handle email commands
    for queries in Decision:
        if not EmailExecution:
            if queries.startswith("email"):
                EmailExecution = True
                print(f"Email command detected: {queries}")
                
                email_client = EmailClient()
                
                if queries.startswith("email check"):
                    SetAssistantStatus("Checking emails...")
                    result = email_client.check_emails(limit=5)
                    
                    if isinstance(result, str):
                        # Error occurred
                        Answer = result
                    else:
                        # Format the result for display
                        Answer = "Here are your recent emails:\n\n"
                        for i, email in enumerate(result):
                            Answer += f"{i+1}. From: {email['sender']}\n"
                            Answer += f"   Subject: {email['subject']}\n"
                            Answer += f"   Date: {email['date']}\n\n"
                    
                    ShowTextToScreen(f"{Assistantname} : {Answer}")
                    SetAssistantStatus("Answering ...")
                    TextToSpeech("I've checked your emails. Here's what I found.")
                    
                elif queries.startswith("email summarize"):
                    SetAssistantStatus("Summarizing emails...")
                    result = email_client.summarize_emails(limit=10)
                    ShowTextToScreen(f"{Assistantname} : {result}")
                    SetAssistantStatus("Answering ...")
                    TextToSpeech("I've summarized your recent emails.")
                    
                elif queries.startswith("email send"):
                    # Parse the email command: "email send recipient, subject, message"
                    # Extract data from the command using regex or string splitting
                    command_parts = queries.replace("email send", "").strip()
                    
                    # Simple parsing assuming comma separation
                    try:
                        parts = command_parts.split(',', 2)
                        if len(parts) >= 3:
                            recipient = parts[0].strip()
                            subject = parts[1].strip()
                            message = parts[2].strip()
                            
                            SetAssistantStatus("Sending email...")
                            result = email_client.send_email(recipient, subject, message)
                            ShowTextToScreen(f"{Assistantname} : {result}")
                            SetAssistantStatus("Answering ...")
                            TextToSpeech("I've sent the email as requested.")
                        else:
                            Answer = "I couldn't parse the email command correctly. Please provide recipient, subject, and message."
                            ShowTextToScreen(f"{Assistantname} : {Answer}")
                            SetAssistantStatus("Answering ...")
                            TextToSpeech(Answer)
                    except Exception as e:
                        Answer = f"Error sending email: {str(e)}"
                        ShowTextToScreen(f"{Assistantname} : {Answer}")
                        SetAssistantStatus("Answering ...")
                        TextToSpeech("I encountered an error while trying to send the email.")
                
                return True

    # Handle automation tasks
    for queries in Decision:
        if not TaskExecution:
            if any(queries.startswith(func) for func in Functions):
                print(f"Executing automation for: {queries}")  # Debug print
                run(Automation(list(Decision)))
                TaskExecution = True

    if ImageExecution:
        print("Starting image generation process")  # Debug print
        # Get absolute paths
        current_dir = os.path.dirname(os.path.abspath(__file__))
        image_data_path = os.path.join(current_dir, "Frontend", "Files", "ImageGeneration.data")
        image_gen_script = os.path.join(current_dir, "Backend", "ImageGeneration.py")
        
        # Write the image generation data with the actual query
        with open(image_data_path, "w") as file:
            file.write(f"{ImageGenerationQuery},True")  # Removed space before True to match expected format

        try:
            # Use python3 and absolute path
            p1 = subprocess.Popen(['python3', image_gen_script],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                stdin=subprocess.PIPE, shell=False)
            print(f"Image generation process started for: {ImageGenerationQuery}")  # Added query to debug print
            
            # Wait for a short time to check for immediate errors
            try:
                stdout, stderr = p1.communicate(timeout=2)
                if stderr:
                    print(f"Image generation error: {stderr.decode()}")
            except subprocess.TimeoutExpired:
                # Process is still running, which is fine
                pass
                
        except Exception as e:
            print(f"Error running ImageGeneration.py: {e}")
            print(f"Script path: {image_gen_script}")

    # Handle responses
    try:
        if G and R:
            print("Processing combined general and realtime query")  # Debug print
            SetAssistantStatus("Searching ...")
            Answer = RealtimeSearchEngine(QueryModifier(Merged_query))
            print(f"Got answer: {Answer}")  # Debug print
            ShowTextToScreen(f"{Assistantname} : {Answer}")
            SetAssistantStatus("Answering ...")
            TextToSpeech(Answer)
            return True
        elif R:
            print("Processing realtime query")  # Debug print
            SetAssistantStatus("Searching ...")
            Answer = RealtimeSearchEngine(QueryModifier(Merged_query))
            print(f"Got answer: {Answer}")  # Debug print
            ShowTextToScreen(f"{Assistantname} : {Answer}")
            SetAssistantStatus("Answering ...")
            TextToSpeech(Answer)
            return True
        else:
            for Queries in Decision:
                if "general" in Queries:
                    print("Processing general query")  # Debug print
                    SetAssistantStatus("Thinking ...")
                    QueryFinal = Queries.replace("general", "")
                    Answer = ChatBot(QueryModifier(QueryFinal))
                    print(f"Got answer: {Answer}")  # Debug print
                    ShowTextToScreen(f"{Assistantname} : {Answer}")
                    SetAssistantStatus("Answering ...")
                    TextToSpeech(Answer)
                    return True
                
                elif "realtime" in Queries:
                    print("Processing realtime query")  # Debug print
                    SetAssistantStatus("Searching ...")
                    QueryFinal = Queries.replace("realtime", "")
                    Answer = RealtimeSearchEngine(QueryModifier(QueryFinal))
                    print(f"Got answer: {Answer}")  # Debug print
                    ShowTextToScreen(f"{Assistantname} : {Answer}")
                    SetAssistantStatus("Answering ...")
                    TextToSpeech(Answer)
                    return True

                elif "exit" in Queries:
                    print("Processing exit command")  # Debug print
                    QueryFinal = "Okay, Bye!"
                    Answer = ChatBot(QueryModifier(QueryFinal))
                    ShowTextToScreen(f"{Assistantname} : {Answer}")
                    SetAssistantStatus("Answering ...")
                    TextToSpeech(Answer)
                    SetAssistantStatus("Answering ...")
                    os._exit(1)
    except Exception as e:
        print(f"Error in response handling: {e}")
        return False

    print("No matching query type found")  # Debug print
    return False

def FirstThread():
    previous_status = None
    processing_states = ["Thinking", "Listening", "Searching", "Answering"]
    
    while True:
        try:
            CurrentStatus = GetMicroPhoneStatus()
            AIStatus = GetAssistantStatus()
            
            if CurrentStatus == "True":
                if not any(state in AIStatus for state in processing_states):
                    MainExecution()
            else:
                # Only update status if it's different and not in a processing state
                if (AIStatus != "Available..." and 
                    not any(state in AIStatus for state in processing_states)):
                    SetAssistantStatus("Available...")
            
            # Add a longer delay to prevent rapid status updates
            time.sleep(1.0)
            
        except Exception as e:
            print(f"Error in FirstThread: {e}")
            time.sleep(1.0)

def SecondThread():
    GraphicalUserInterface()

if __name__ == "__main__":
    thread2 = threading.Thread(target=FirstThread, daemon=True)
    thread2.start()
    SecondThread()