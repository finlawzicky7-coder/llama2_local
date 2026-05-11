from webbrowser import open as webopen
from pywhatkit import search, playonyt
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
from groq import Groq
import subprocess
import requests
import keyboard
import asyncio
import os
import webbrowser as webopen
from urllib.parse import urlparse
import shutil
import re
import webbrowser

env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")

classes = ["zCubwf", "hgKElc", "L1tM0c YYrZ6", "z20LcW", "gsrt vk_bk FzvWSb WprNhf", "pclqee", "tw-Data-text tw-text-small tw-ta",
           "IZ6rdc", "OSr6df L1tM0c", "YYrZ6", "webanswers-webanswers_table__webanswers-table", "dDoNo ikb4Bb gsrt", "sXLaOe",
           "LWKfbc", "vQfq4c", "y9gBwe", "kno-desc", "SPZz6b"]

user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'

client = Groq(api_key=GroqAPIKey)

messages = [
    "Your satisfaction is my top priority; feel free to reach out if there's anything else I can help you with.",
    "I'm at your service for any additional questions or support you may need—don't hesitate to ask."
]

messages = []

SystemChatBot = [{"role": "system", "content": f"Hello, I am {os.environ['USER']}. You're a content writer. You have to write content like letter, codes, applications, essays, notes, songs, poems etc."}]

def GoogleSearch(Topic):
    search(Topic)
    return True

def Content(Topic):
    # Content("write a application for a sick leave.")
    def OpenTextEdit(File):
        defult_text_editor = "TextEdit"  # macOS default text editor is TextEdit
        if not os.path.exists(File):
            print(f"File {File} does not exist!")
            return False
        subprocess.run(["open", File])
        print(f"Opening {File} in TextEdit...")
        return True

    def ContentWriterAI(prompt):
        messages.append({"role": "user", "content": f'{prompt}'})

        completion = client.chat.completions.create(
            model="mixtral-8x7b-32768",  # Specify the AI model
            messages=SystemChatBot + messages,
            max_tokens=2048,  # Limit the maximum tokens in response
            temperature=0.7,  # Adjust response randomness
            top_p=1,  # Use nucleus sampling for response
            stream=True,  # Enable streaming response
            stop=None  # Allow the model to determine stopping condition
        )

        Answer = ""
        
        for chunk in completion:
            if chunk.choices[0].delta.content:
                if chunk.choices and chunk.choices[0].delta.content:
                    Answer += chunk.choices[0].delta.content


        Answer = Answer.replace("</s>", "")
        messages.append({"role": "assistant", "content": Answer})
        return Answer

    Topic : str = Topic.replace("Content", "")
    ContentByAI = ContentWriterAI(Topic)

    file_dir = 'data'
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)  # Create the directory if it doesn't exist

    file_path = f'{file_dir}/{Topic.lower().replace(" ","_")}.txt'
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(ContentByAI)
    OpenTextEdit(file_path)
    return True

def YoutubeSearch(Topic):
    Url4Search = f"https://www.youtube.com/results?search_query={Topic}"
    webbrowser.open(Url4Search)
    return True

def playYoutube(query):
    playonyt(query)
    return True

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'

def OpenApp(app, sess=requests.session()):
    try:
        # Normalize the app name for case-sensitivity and ensure it's properly formatted.
        app_path = f"/Applications/{app}.app"
        
        # Try opening the app if it's installed.
        if os.path.exists(app_path):
            subprocess.run(["open", "-a", app])  # Open the app on macOS
            return True  # Indicate success.
        else:
            print(f"{app} is not installed. Attempting to open the download page in a browser...")
            # Fallback to opening a website (e.g., Chrome download page if Chrome isn't installed)
            if app.lower() == "google chrome":
                webbrowser.open("https://www.google.com/chrome/")
            else:
                # Default case - perform a Google search for the app name
                webbrowser.open(f"https://www.google.com/search?q={app}+download")
            return True

    except Exception as e:
        print(f"Error opening app: {e}")
        # Nested function to extract links from HTML content.
        def extract_links(html):
            if html is None:
                return []
            soup = BeautifulSoup(html, 'html.parser')  # Parse the HTML content.
            links = soup.find_all('a', {'jsname': 'UWckNb'})  # Find relevant links.
            return [link.get('href') for link in links]  # Return the links.

        # Nested function to perform a Google search and retrieve HTML.
        def search_google(query):
            url = f"https://www.google.com/search?q={query}"  # Construct the Google search URL
            headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}  # Custom User-Agent string
            response = sess.get(url, headers=headers)  # Perform the GET request.

            if response.status_code == 200:
                return response.text  # Return the HTML content.
            else:
                print("Failed to retrieve search results.")  # Print an error message.
                return None

        html = search_google(app)  # Perform the Google search.

        if html:
            links = extract_links(html)  # Extract all links from the HTML content.
            if links:  # If we have any links, open the first one.
                webbrowser.open(links[0])  # Open the first link in the default web browser.

    return True  # Indicate success.

def open_in_chrome(url):
    """
    This function opens the URL in Google Chrome on macOS.
    """
    # Attempt to open in Google Chrome using the 'open -a' command with Chrome
    try:
        os.system(f"open -a 'Google Chrome' {url}")
        print(f"Opened URL in Google Chrome: {url}")
    except Exception as e:
        print(f"Error opening Google Chrome with URL {url}: {e}")

# macOS compatible version of CloseApp function using AppleScript
def CloseApp(app):
    if app.lower() == "google chrome":
        print("Google Chrome cannot be closed using this function.")
        return False

    script = f'''
    tell application "{app}"
        quit
    end tell
    '''
    try:
        subprocess.run(['osascript', '-e', script])
        print(f"Closed {app}")
        return True
    except Exception as e:
        print(f"Error closing {app}: {e}")
        return False

def System(command):
    def mute():
        subprocess.run(["osascript", "-e", "set volume output muted true"])  # macOS mute command
    
    def unmute():
        subprocess.run(["osascript", "-e", "set volume output muted false"])  # macOS unmute command

    def volume_up():
        subprocess.run(["osascript", "-e", "set volume output volume (output volume of (get volume settings) + 10)"])  # macOS volume up
    
    def volume_down():
        subprocess.run(["osascript", "-e", "set volume output volume (output volume of (get volume settings) - 10)"])  # macOS volume down

    if command == "mute":
        mute()

    elif command == "unmute":
        unmute()

    elif command == "volume up":
        volume_up()

    elif command == "volume down":
        volume_down()

    return True

async def TranslateAndExecute(commands: list[str]):
    funcs = []

    for command in commands:

        if command.startswith("open "):
            if "open it" in command:
                pass
            if "open file" == command:
                pass
            else:
                fun = asyncio.to_thread(OpenApp, command.removeprefix("open "))
                funcs.append(fun)

        elif command.startswith("general "):
            pass

        elif command.startswith("realtime "):
            pass

        elif command.startswith("close "):
            fun = asyncio.to_thread(CloseApp, command.removeprefix("close "))
            funcs.append(fun)

        elif command.startswith("play "):
            fun = asyncio.to_thread(playYoutube, command.removeprefix("play "))
            funcs.append(fun)

        elif command.startswith("content "):
            fun = asyncio.to_thread(Content, command.removeprefix("content "))
            funcs.append(fun)

        elif command.startswith("google search"):
            fun = asyncio.to_thread(GoogleSearch, command.removeprefix("google search "))
            funcs.append(fun)

        elif command.startswith("youtube search "):
            fun = asyncio.to_thread(YoutubeSearch, command.removeprefix("youtube search "))
            funcs.append(fun)

        elif command.startswith("system "):
            fun = asyncio.to_thread(System, command.removeprefix("system "))
            funcs.append(fun)

        else:
            print(f"No function found for {command}")

    results = await asyncio.gather(*funcs)

    for result in results:
        if isinstance(result, str):
            yield result
        else:
            yield result

async def Automation(commands: list[str]):
    async for result in TranslateAndExecute(commands):
        pass
    return True

if __name__ == "__main__":
    asyncio.run(Automation([ "open youtube"]))
