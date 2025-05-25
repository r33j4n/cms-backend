import faiss
import numpy as np
import pickle
import requests
import os
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# Load environment
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Load FAISS and chunks once at startup
index = faiss.read_index("manual_vectors.faiss")
with open("manual_vectors_chunks.pkl", "rb") as f:
    chunks = pickle.load(f)

# Load the embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

def get_solution_from_complaint(complaint_text, top_k=3):
    # Embed complaint
    query_vector = model.encode([complaint_text])
    _, I = index.search(np.array(query_vector), top_k)
    retrieved_chunks = [chunks[i] for i in I[0]]

    # Build prompt
    context = "\n\n".join(retrieved_chunks)
    prompt = f"""Use the following instructions from the apartment manual to help the user. Provide only the answer, no additional text.

Manual:
{context}

Complaint:
{complaint_text}

Answer:"""

    # Groq call
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    body = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that answers apartment-related complaints using a user manual."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2
    }

    response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=body)
    return response.json()["choices"][0]["message"]["content"]

def classify_complaint_domain(complaint_text):
    """
    Classify the complaint into one of the predefined domains.

    Domains:
    - Plumbing
    - Electrical
    - HVAC
    - Structural
    - Appliance
    - Security
    - Noise
    - Cleanliness
    - Maintenance
    - Other

    Args:
        complaint_text (str): The text of the complaint

    Returns:
        str: The domain of the complaint
    """
    # Groq call
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = f"""Classify the following apartment complaint into exactly one of these domains:
- Plumbing
- Electrical
- HVAC
- Structural
- Appliance
- Security
- Noise
- Cleanliness
- Maintenance
- Other

Complaint: {complaint_text}

Return only the domain name, nothing else."""

    body = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that classifies apartment complaints into predefined domains."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1
    }

    response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=body)
    domain = response.json()["choices"][0]["message"]["content"].strip()

    # Ensure the domain is one of the predefined domains
    predefined_domains = ["Plumbing", "Electrical", "HVAC", "Structural", "Appliance", 
                         "Security", "Noise", "Cleanliness", "Maintenance", "Other"]

    if domain not in predefined_domains:
        return "Other"

    return domain
