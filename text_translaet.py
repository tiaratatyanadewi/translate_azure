import requests
import uuid
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get values from environment
API_KEY = os.getenv("AZURE_TRANSLATOR_KEY")
ENDPOINT = os.getenv("AZURE_TRANSLATOR_ENDPOINT")
LOCATION = os.getenv("AZURE_TRANSLATOR_LOCATION")
TARGET_LANGUAGE = os.getenv("TARGET_LANGUAGE", "id")

# Read original document
with open("input.txt", "r", encoding="utf-8") as f:
    original_text = f.read()

# Add prompt/context
context_prompt = (
    "Translate the following text to Bahasa Indonesia. "
    "Do not translate any medical terms, drug names, or anatomy names. "
    "Keep them in English where applicable.\n\n"
)
text_to_translate = context_prompt + original_text

# Build request
path = "/translate?api-version=3.0"
params = f"&to={TARGET_LANGUAGE}"
constructed_url = ENDPOINT + path + params

headers = {
    "Ocp-Apim-Subscription-Key": API_KEY,
    "Ocp-Apim-Subscription-Region": LOCATION,
    "Content-type": "application/json",
    "X-ClientTraceId": str(uuid.uuid4()),
}

body = [{"text": text_to_translate}]

response = requests.post(constructed_url, headers=headers, json=body)
result = response.json()

# Extract and clean translated result
translated_body = result[0]["translations"][0]["text"]
translated_lines = translated_body.splitlines()
translated_text_only = (
    "\n".join(translated_lines[2:]) if len(translated_lines) > 2 else translated_body
)

# Write result
with open("translated.txt", "w", encoding="utf-8") as f:
    f.write(translated_text_only)

print("Translated content saved to 'translated.txt'")
