import google.generativeai as genai
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

# Get API key from environment variable
api_key = os.getenv("GOOGLE_API_KEY")

# Debug print (optional)
print("Loaded API Key:", api_key)

# Configure Gemini with API key
genai.configure(api_key=api_key)

# System prompt for chatbot behaviour
SYSTEM_PROMPT = """
You are a Q&A chatbot.
Your job is to answer user questions clearly and briefly.
Use simple explanations.
If you don't know something, admit it.
"""

# Create model with system instructions
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction=SYSTEM_PROMPT,
    generation_config=genai.GenerationConfig(
        max_output_tokens=500,
        temperature=0.7,
        top_p=0.9,
    ),
)

# Start chat session
chat = model.start_chat(history=[])

print("🤖 Gemini Q&A Chatbot Started!")
print("Type 'bye' to stop.\n")

while True:
    user_input = input("You: ")

    if user_input.lower() == "bye":
        print("Gemini: Goodbye! Have a Nice Day!")
        break

    try:
        response = chat.send_message(user_input)
        print("Gemini:", response.text)
    except Exception as e:
        print("Error:", e)
