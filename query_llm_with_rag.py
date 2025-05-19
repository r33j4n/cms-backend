import faiss
import numpy as np
import pickle
import requests
import os
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# Load .env variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# 1. Load FAISS index and chunks
index = faiss.read_index("manual_vectors.faiss")
with open("manual_vectors_chunks.pkl", "rb") as f:
    chunks = pickle.load(f)

# 2. Load the same embedding model used earlier
model = SentenceTransformer("all-MiniLM-L6-v2")


# 3. Define the function to query FAISS + call Groq
def generate_answer_from_query(user_query, top_k=3):
    # Step 1: Embed the user query
    query_vector = model.encode([user_query])

    # Step 2: Search in FAISS
    distances, indices = index.search(np.array(query_vector), top_k)
    relevant_chunks = [chunks[i] for i in indices[0]]

    # Step 3: Create prompt for Groq
    context = "\n\n".join(relevant_chunks)
    prompt = f"""
Use the following instructions from the apartment manual to help the user.

Manual:
{context}

Complaint:
{user_query}

Answer:"""

    # Step 4: Send to Groq
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "system",
             "content": "You are a helpful assistant that answers apartment-related complaints using a user manual."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2
    }

    response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
    return response.json()["choices"][0]["message"]["content"]

query = "There is a leak in the bathroom tap. What should I do?"
answer = generate_answer_from_query(query)
print("🔧 Suggested Instruction:\n", answer)