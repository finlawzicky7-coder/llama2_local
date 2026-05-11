from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values
import os

# Get the current directory (where the script is located)
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
env_vars = dotenv_values(os.path.join(current_dir, ".env"))
Username = env_vars.get("username", "User")  # Match the variable name in .env
Assistantname = env_vars.get("Assistantname", "Jarvis")
GroqAPIKey = env_vars.get("GroqAPIKey")
CO_API_KEY = env_vars.get("CO_API_KEY")
HuggingFaceAPIKey = env_vars.get("HuggingFaceAPIKey")
AssistantVoice = env_vars.get("AssistantVoice")

if not GroqAPIKey:
    raise ValueError("GroqAPIKey not found in .env file")

# Initialize Groq client
client = Groq(api_key=GroqAPIKey)

# System initialization
System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which also has real-time up-to-date information from the internet.
*** Do not tell time until I ask, do not talk too much, just answer the question.***
*** Reply in only English, even if the question is in Hindi, reply in English.***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
"""

SystemChatBot = [
    {"role": "system", "content": System}
]

# Create necessary directories
chat_log_path = os.path.join(current_dir, "Data", "ChatLog.json")
os.makedirs(os.path.dirname(chat_log_path), exist_ok=True)

# Load existing chat log or create new one
try:
    with open(chat_log_path, "r", encoding='utf-8') as f:
        messages = load(f)
except (FileNotFoundError, ValueError):
    messages = []
    with open(chat_log_path, "w", encoding='utf-8') as f:
        dump(messages, f, indent=4)

def RealtimeInformation():
    current_date_time = datetime.datetime.now()
    return {
        "day": current_date_time.strftime("%A"),
        "date": current_date_time.strftime("%d"),
        "month": current_date_time.strftime("%B"),
        "year": current_date_time.strftime("%Y"),
        "time": f"{current_date_time.strftime('%H')}:{current_date_time.strftime('%M')}:{current_date_time.strftime('%S')}"
    }

def AnswerModifier(Answers):
    if not isinstance(Answers, str):
        return str(Answers)
    lines = Answers.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    return '\n'.join(non_empty_lines)

def ChatBot(Query):
    if not Query or not isinstance(Query, str):
        return "Invalid input"

    try:
        # Load current chat log
        with open(chat_log_path, "r", encoding='utf-8') as f:
            messages = load(f)

        # Add user query
        messages.append({"role": "user", "content": Query})

        # Get current time info
        time_info = RealtimeInformation()
        time_message = f"Current time: {time_info['time']}, Date: {time_info['date']} {time_info['month']} {time_info['year']}, Day: {time_info['day']}"

        # Make API request
        try:
            completion = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=SystemChatBot + [{"role": "system", "content": time_message}] + messages,
                max_tokens=2000,
                temperature=0.7,
                top_p=1,
                stream=True
            )

            Answer = ""
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    Answer += chunk.choices[0].delta.content

            Answer = Answer.replace("</s>", "").strip()

        except Exception as e:
            print(f"Error in API call: {e}")
            Answer = "I apologize, but I'm having trouble connecting to my language model right now. Please try again in a moment."

        # Add response to messages
        messages.append({"role": "assistant", "content": Answer})

        # Save updated chat log
        with open(chat_log_path, "w", encoding='utf-8') as f:
            dump(messages, f, indent=4)

        return AnswerModifier(Answer)

    except Exception as e:
        print(f"Error in ChatBot: {e}")
        return "I apologize, but I encountered an error. Please try again."

if __name__ == "__main__":
    while True:
        try:
            user_input = input("Enter Your Questions: ")
            if user_input.lower() in ['exit', 'quit']:
                break
            print(ChatBot(user_input))
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
