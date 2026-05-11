from googlesearch import search
from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values
import os

# Get the current directory (where the script is located)
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

env_vars = dotenv_values(os.path.join(current_dir, ".env"))

Username = env_vars.get("username", "User")  # Default to "User" if not found
Assistantname = env_vars.get("Assistantname", "Jarvis")  # Default to "Jarvis" if not found
GroqAPIKey = env_vars.get("GroqAPIKey")

if GroqAPIKey is None:
    raise ValueError("GroqAPIKey not found in .env file. Please add your Groq API key to the .env file.")

# Set environment variable for Groq
os.environ["GROQ_API_KEY"] = GroqAPIKey

client = Groq(api_key=GroqAPIKey)

System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which has real-time up-to-date information from the internet.
*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***
*** Just answer the question from the provided data in a professional way. ***"""

# Use os.path.join for file paths
chat_log_path = os.path.join(current_dir, "Data", "ChatLog.json")

try:
    with open(chat_log_path, "r", encoding='utf-8') as f:
        messages = load(f)
except FileNotFoundError:
    os.makedirs(os.path.dirname(chat_log_path), exist_ok=True)
    with open(chat_log_path, "w", encoding='utf-8') as f:
        dump([], f)
        messages = []

def GoogleSearch(query):
    results = list(search(query, advanced=True, num_results=5))
    Answer = f"The search results for '{query}' are:\n[start\n]"

    for i in results:
        Answer += f"Title: {i.title}\nDescription: {i.description}\n\n"

    Answer += "[end]"
    return Answer

def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

SystemChatBot = [
    {"role": "system", "content": System},
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": "Hello, how can i help you?"},
]

def Information():
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")
    
    # Initialize data variable
    data = ""
    
    data += f"please use this real-time information if needed,\n"
    data += f"Day: {day}\n"
    data += f"Date: {date}\n"
    data += f"Month: {month}\n"
    data += f"Year: {year}\n"
    data += f"Time: {hour} hours :{minute} minutes :{second} seconds.\n"
    
    return data

def RealtimeSearchEngine(prompt):
    global SystemChatBot, messages

    # Load existing chat log
    with open(chat_log_path, "r", encoding='utf-8') as f:
        messages = load(f)
    
    messages.append({"role": "user", "content": f"{prompt}"})

    SystemChatBot.append({"role": "system", "content": GoogleSearch(prompt)})

    # Get the real-time information and append it to the SystemChatBot
    SystemChatBot.append({"role": "system", "content": Information()})

    # Make a request to the Groq API for a response
    completion = client.chat.completions.create(
        model="llama3-70b-8192",  # Specify the AI model to use
        messages=SystemChatBot + messages,  # Include updated messages
        max_tokens=2048,  # Limit the number of tokens in the response
        temperature=0.7,  # Adjust response randomness (higher means more random)
        top_p=1,  # Use nucleus sampling to control diversity
        stream=True,  # Enable streaming response
        stop=None  # Allow the model to determine when to stop
    )

    Answer = ""  # Initialize an empty string to store the AI's response

    # Process the streamed response chunks
    for chunk in completion:
        if chunk.choices[0].delta.content:
            Answer += chunk.choices[0].delta.content

    Answer = Answer.replace("</s>", "")  # Clean up the answer

    messages.append({"role": "assistant", "content": Answer})

    # Save the updated chat log to the file
    with open(chat_log_path, "w", encoding='utf-8') as f:
        dump(messages, f, indent=4)

    return AnswerModifier(Answer)  # Return the modified answer


if __name__ == "__main__":
    while True:
        user_input = input("Enter Your Query: ")  # Get user input
        print(RealtimeSearchEngine(user_input))  # Call the RealtimeSearchEngine function and print the response

