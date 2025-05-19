import requests
from API_KEY import GRQAPI_KEY
# GROQ_API_KEY = os.getenv("GROQ_API_KEY")  # Put it in your .env
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

def ask_llama3_with_groq(prompt):
    headers = {
        "Authorization": f"Bearer {GRQAPI_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant who replies based on PDF manual instructions."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2
    }

    response = requests.post(GROQ_URL, headers=headers, json=payload)
    return response.json()["choices"][0]["message"]["content"]