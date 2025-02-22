import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from pydantic import BaseModel, HttpUrl
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
import numpy as np
import textwrap
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="RAG Application")

# ✅ CORS Configuration (Includes Vercel)
origins = [
    "http://localhost:3000",   # Local Next.js Dev Server
    "http://127.0.0.1:3000",
    "https://your-vercel-app.vercel.app",  # Replace with your actual Vercel frontend URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# ✅ Load API Credentials from .env
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")

# ✅ Initialize Qdrant Client
qdrant_client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY
)

# ✅ Initialize Gemini API
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

# ✅ Initialize Sentence Transformer
encoder = SentenceTransformer('all-MiniLM-L6-v2')


# ✅ Root Endpoint (Prevents 404 on Base URL)
@app.get("/")
async def root():
    return {"message": "RAG API is running!"}


# ✅ Pydantic Models
class URLInput(BaseModel):
    url: HttpUrl

class Query(BaseModel):
    question: str


# ✅ Function to Create Collection if Not Exists
def create_collection_if_not_exists():
    """Create Qdrant collection if it doesn't exist."""
    collections = qdrant_client.get_collections().collections
    if not any(collection.name == COLLECTION_NAME for collection in collections):
        qdrant_client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config={"size": 384, "distance": "Cosine"}
        )


# ✅ Extract Text from URL
def extract_text_from_url(url: str) -> str:
    """Extracts clean text from a given URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Remove script & style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Clean extracted text
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        return ' '.join(chunk for chunk in chunks if chunk)

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error extracting text: {str(e)}")


# ✅ Chunk Text
def chunk_text(text: str, chunk_size: int = 1000) -> List[str]:
    """Splits text into manageable chunks."""
    return textwrap.wrap(text, chunk_size, break_long_words=False)


# ✅ Generate Embeddings
def embed_chunks(chunks: List[str]) -> List[np.ndarray]:
    """Encodes text chunks into embeddings."""
    try:
        return encoder.encode(chunks)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating embeddings: {str(e)}")


# ✅ Process URL & Store in Qdrant
@app.post("/process-url")
async def process_url(url_input: URLInput):
    """Processes a given URL and stores its embeddings in Qdrant."""
    try:
        text = extract_text_from_url(str(url_input.url))
        chunks = chunk_text(text)
        embeddings = embed_chunks(chunks)

        create_collection_if_not_exists()

        points = [
            {"id": i, "vector": embedding.tolist(), "payload": {"text": chunk, "url": str(url_input.url)}}
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings))
        ]

        qdrant_client.upsert(collection_name=COLLECTION_NAME, points=points)
        return {"message": f"Stored {len(chunks)} chunks from {url_input.url}"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ✅ Query the RAG System
@app.post("/query")
async def query(query: Query):
    """Searches Qdrant for relevant context and queries Gemini."""
    try:
        query_embedding = encoder.encode(query.question)

        search_results = qdrant_client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_embedding.tolist(),
            limit=3
        )

        relevant_chunks = [result.payload["text"] for result in search_results]

        # Constructing Gemini prompt
        context = "\n".join(relevant_chunks)
        prompt = f"""Based on the following context, answer the question concisely.

Context:
{context}

Question: {query.question}"""

        response = model.generate_content(prompt)

        return {"answer": response.text, "source_chunks": relevant_chunks}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ✅ Delete URL Data from Qdrant
@app.delete("/delete-url")
async def delete_url(url_input: URLInput):
    """Deletes all stored embeddings related to a specific URL."""
    try:
        search_response = qdrant_client.scroll(
            collection_name=COLLECTION_NAME,
            scroll_filter={"must": [{"key": "url", "match": {"value": str(url_input.url)}}]},
            limit=100
        )

        points = search_response[0]
        point_ids = [point.id for point in points]

        if not point_ids:
            raise HTTPException(status_code=404, detail="No content found for this URL")

        qdrant_client.delete(collection_name=COLLECTION_NAME, points_selector=point_ids)

        return {"message": f"Deleted {len(point_ids)} chunks for {url_input.url}"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ✅ Run Server with Dynamic Port (for Render)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
