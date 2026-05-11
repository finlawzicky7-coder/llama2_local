import asyncio
from random import randint
import requests
from dotenv import dotenv_values
import os
import subprocess
from time import sleep

# Get the current directory (where the script is located)
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
try:
    env_vars = dotenv_values(os.path.join(current_dir, ".env"))
    api_key = env_vars.get("HuggingFaceAPIKey")
    print(f"API Key found: {'Yes' if api_key else 'No'}")
except Exception as e:
    print(f"Error loading .env file: {e}")
    raise

if not api_key:
    raise ValueError("HuggingFaceAPIKey not found in .env file")

# Function to open images in Preview (more reliable on macOS than Photos)
def open_images(prompt):
    folder_path = os.path.join(current_dir, "Data")
    prompt = prompt.replace(" ", "_")
    Files = [f"{prompt}{i}.jpg" for i in range(1, 5)]

    for jpg_file in Files:
        Image_path = os.path.join(folder_path, jpg_file)
        try:
            if os.path.exists(Image_path):
                # Use 'open' command on macOS to open with default app
                subprocess.run(["open", Image_path])
                print(f"Opening image: {Image_path}")
            else:
                print(f"Image file not found: {Image_path}")
        except Exception as e:
            print(f"Error opening image {Image_path}: {e}")

# API setup
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
headers = {"Authorization": f"Bearer {api_key}"}

async def query(payload):
    try:
        print(f"Making API request with payload: {payload}")
        response = await asyncio.to_thread(
            requests.post, 
            API_URL, 
            headers=headers, 
            json=payload,
            timeout=30
        )
        print(f"Response status code: {response.status_code}")
        
        if response.status_code == 200:
            return response.content
        elif response.status_code == 429:
            print("Rate limit hit, waiting before retry...")
            await asyncio.sleep(2)
            return None
        else:
            print(f"Error: API returned status code {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"Error in query: {e}")
        return None

async def generate_images(prompt: str):
    print(f"Starting image generation for prompt: {prompt}")
    folder_path = os.path.join(current_dir, "Data")
    os.makedirs(folder_path, exist_ok=True)

    tasks = []
    for i in range(4):  # Changed back to 4 images
        payload = {
            "inputs": f"{prompt}, quality=4K, sharpness=maximum, Ultra High details, high resolution",
            "seed": randint(0, 1000000)
        }
        task = asyncio.create_task(query(payload))
        tasks.append(task)

    try:
        image_bytes_lists = await asyncio.gather(*tasks)
        success = False

        for i, image_bytes in enumerate(image_bytes_lists):
            if image_bytes:
                image_path = os.path.join(folder_path, f"{prompt.replace(' ', '_')}{i + 1}.jpg")
                try:
                    with open(image_path, "wb") as f:
                        f.write(image_bytes)
                    print(f"Image saved as: {image_path}")
                    success = True
                    # Open the image immediately after saving
                    subprocess.run(["open", image_path])
                except Exception as e:
                    print(f"Error saving image {i + 1}: {e}")

        if not success:
            print("No images were successfully generated")

    except Exception as e:
        print(f"Error in generate_images: {e}")

def GenerateImage(prompt: str):
    if not prompt or not isinstance(prompt, str):
        print("Invalid prompt")
        return
    try:
        print(f"Starting GenerateImage with prompt: {prompt}")
        asyncio.run(generate_images(prompt))
    except Exception as e:
        print(f"Error in GenerateImage: {e}")

if __name__ == "__main__":
    # Main loop for normal operation
    try:
        image_data_path = os.path.join(current_dir, "Frontend", "Files", "ImageGeneration.data")
        os.makedirs(os.path.dirname(image_data_path), exist_ok=True)
        
        if not os.path.exists(image_data_path):
            with open(image_data_path, "w") as f:
                f.write(",False")
        
        with open(image_data_path, "r") as f:
            data = f.read().strip()
            if "," not in data:
                data = ",False"
            prompt, status = data.split(",")

        if status.strip() == "True" and prompt.strip():
            print(f"Generating image for prompt: {prompt.strip()}")
            GenerateImage(prompt.strip())
            
            with open(image_data_path, "w") as f:
                f.write(",False")
        
    except Exception as e:
        print(f"Error in main execution: {e}")
else:
    # Main loop for normal operation
    while True:
        try:
            image_data_path = os.path.join(current_dir, "Frontend", "Files", "ImageGeneration.data")
            os.makedirs(os.path.dirname(image_data_path), exist_ok=True)
            
            if not os.path.exists(image_data_path):
                with open(image_data_path, "w") as f:
                    f.write(",False")
            
            with open(image_data_path, "r") as f:
                data = f.read().strip()
                if "," not in data:
                    data = ",False"
                prompt, status = data.split(",")

            if status.strip() == "True" and prompt.strip():
                print(f"Generating image for prompt: {prompt.strip()}")
                GenerateImage(prompt.strip())
                
                with open(image_data_path, "w") as f:
                    f.write(",False")
                break
            
            sleep(1)

        except Exception as e:
            print(f"Error in main loop: {e}")
            sleep(1)
