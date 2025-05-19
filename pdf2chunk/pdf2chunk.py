import fitz  # PyMuPDF
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pickle

FILE_PATH = "data/apartmentdata.pdf"
def extract_text_from_pdf(file_path):
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# 2. Split into chunks
def chunk_text(text, chunk_size=500, overlap=50):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        length_function=len
    )
    return splitter.split_text(text)
# 3. Embed the chunks using SentenceTransformer
def embed_chunks(chunks):
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(chunks)
    return embeddings, model
# 4. Store embeddings in FAISS
def store_faiss_index(embeddings):
    dim = embeddings[0].shape[0]
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings))
    return index

# 4. Store embeddings in FAISS
def store_faiss_index(embeddings):
    dim = embeddings[0].shape[0]
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings))
    return index
# 5. Save FAISS index and chunks to disk

def save_vector_store(index, chunks, file_prefix="manual_vectors"):
    faiss.write_index(index, f"{file_prefix}.faiss")
    with open(f"{file_prefix}_chunks.pkl", "wb") as f:
        pickle.dump(chunks, f)

# === Run the pipeline ===
pdf_path = FILE_PATH
text = extract_text_from_pdf(pdf_path)
chunks = chunk_text(text)
embeddings, model = embed_chunks(chunks)
index = store_faiss_index(embeddings)
save_vector_store(index, chunks)
print("✅ PDF processed and stored into FAISS vector DB.")
