import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import dotenv_values
import mtranslate as mt

env_vars = dotenv_values(".env")

# Get InputLanguage with a default value
InputLanguage = env_vars.get("InputLanguage", "en-US")  # Default to en-US if not found

# HTML template for Speech Recognition
HtmlCode = '''<!DOCTYPE html>
<html lang="en">
<head>
    <title>Speech Recognition</title>
</head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="end" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>
    <script>
        const output = document.getElementById('output');
        let recognition;

        function startRecognition() {
            recognition = new webkitSpeechRecognition() || new SpeechRecognition();
            recognition.lang = '';  // This will be replaced with InputLanguage
            recognition.continuous = true;

            recognition.onresult = function(event) {
                const transcript = event.results[event.results.length - 1][0].transcript;
                output.textContent += transcript;
            };

            recognition.onend = function() {
                recognition.start();
            };
            recognition.start();
        }

        function stopRecognition() {
            recognition.stop();
            output.innerHTML = "";
        }
    </script>
</body>
</html>'''

# Replace the input language in the HTML
HtmlCode = HtmlCode.replace("recognition.lang = '';", f"recognition.lang = '{InputLanguage}';")

# Save the HTML file
html_file_path = os.path.join("Data", "Voice.html")
with open(html_file_path, "w") as f:
    f.write(HtmlCode)

# Get the absolute file path for macOS
current_dir = os.getcwd()
file_path = os.path.abspath(html_file_path)

# Format the URL as a file URL
Link = f"file://{file_path}"

# Chrome options
chrome_options = Options()
user_agent = 'mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebkit/537.36 (KHTML,Like Gecko) Chrome/89.0.142.86'
chrome_options.add_argument(f'user-agent={user_agent}')
chrome_options.add_argument("--use-fake-ui-for-media-stream")
chrome_options.add_argument("--use-fake-device-for-media-stream")
# Removed headless mode for testing on macOS
# chrome_options.add_argument("--headless")  # Ensure the UI can open
chrome_options.add_argument('--disable-web-security')  # Added for file access
chrome_options.add_argument('--allow-file-access-from-files')

# Initialize the ChromeDriver service
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

TempDirPath = os.path.join(current_dir, "frontend", "files")

def SetAssistantStatus(status):
    status_file_path = os.path.join(TempDirPath, 'status.data')
    with open(status_file_path, "w", encoding='utf-8') as file:
        file.write(status)

def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ["how", "what", "who", "where", "why", "which", "whose", "whom", "can you", "what's", "where's", "how's", "can you"]

    if any(word + "" in new_query for word in question_words):
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"
    else:
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "."
        else:
            new_query += "."
    
    return new_query.capitalize()

def UniversalTranslator(Text):
    english_translation = mt.translate(Text, "en", "auto")
    return english_translation.capitalize()

def SpeechRecognition():
    try:
        if not os.path.exists(html_file_path):
            print(f"Voice.html not found at: {html_file_path}")
            # Create the file if it doesn't exist
            os.makedirs(os.path.dirname(html_file_path), exist_ok=True)
            with open(html_file_path, "w") as f:
                f.write(HtmlCode)
            print("Created Voice.html file")

        print(f"Opening URL: {Link}")
        driver.get(Link)  # Open the local HTML file
        print("Starting speech recognition...")
        
        # Start speech recognition
        start_button = driver.find_element(by=By.ID, value="start")
        start_button.click()
        print("Speech recognition started")

        max_attempts = 30  # Wait up to 30 seconds for input
        attempt = 0
        
        while attempt < max_attempts:
            try:
                Text = driver.find_element(by=By.ID, value="output").text

                if Text:
                    print(f"Recognized text: {Text}")
                    driver.find_element(by=By.ID, value="end").click()  # Stop recognition
                    
                    if InputLanguage.lower() == "en-us" or "en" in InputLanguage.lower():
                        return QueryModifier(Text)
                    else:
                        SetAssistantStatus("Translating...")
                        return QueryModifier(UniversalTranslator(Text))
                
                attempt += 1
                time.sleep(1)
                
            except Exception as e:
                print(f"Error reading text: {e}")
                attempt += 1
                time.sleep(1)
                
        print("No speech input detected after 30 seconds")
        return "I couldn't hear anything. Could you please try speaking again?"
        
    except Exception as e:
        print(f"Error in speech recognition: {e}")
        return "There was an error with speech recognition. Please try again."

# Main execution block
if __name__ == "__main__":
    while True:
        Text = SpeechRecognition()
        print(Text)
