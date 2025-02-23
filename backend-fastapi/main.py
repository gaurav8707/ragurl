import os
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
import numpy as np
from urllib.parse import urlparse
import textwrap
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="RAG Application")

# ✅ CORS Configuration
origins = [
    "http://localhost:3000",    # Next.js development server
    "http://127.0.0.1:3000",
    "https://frontend-next-inky.vercel.app/",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600,  # Cache preflight requests for 10 minutes
)

# Load Credentials from .env
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")

# Initialize Qdrant client
qdrant_client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY
)

# Initialize Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

# Initialize sentence transformer
encoder = SentenceTransformer('all-MiniLM-L6-v2')

class URLInput(BaseModel):
    url: HttpUrl

class Query(BaseModel):
    question: str

def create_collection_if_not_exists():
    """Create Qdrant collection if it doesn't exist"""
    collections = qdrant_client.get_collections().collections
    if not any(collection.name == COLLECTION_NAME for collection in collections):
        qdrant_client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config={
                "size": 384,  # Dimension for all-MiniLM-L6-v2
                "distance": "Cosine"
            }
        )

def extract_text_from_url(url: str) -> str:
    """Extract text content from URL"""
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
            
        # Get text and clean it
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error extracting text from URL: {str(e)}")

def chunk_text(text: str, chunk_size: int = 1000) -> List[str]:
    """Split text into chunks of approximately equal size"""
    chunks = textwrap.wrap(text, chunk_size, break_long_words=False)
    return chunks

def embed_chunks(chunks: List[str]) -> List[np.ndarray]:
    """Generate embeddings for text chunks"""
    try:
        embeddings = encoder.encode(chunks)
        return embeddings
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating embeddings: {str(e)}")

@app.post("/process-url")
async def process_url(url_input: URLInput):
    """Process URL and store chunks in Qdrant"""
    try:
        # Extract text from URL
        text = extract_text_from_url(str(url_input.url))
        
        # Chunk the text
        chunks = chunk_text(text)
        
        # Generate embeddings
        embeddings = embed_chunks(chunks)
        
        # Create collection if it doesn't exist
        create_collection_if_not_exists()
        
        # Store chunks and embeddings in Qdrant
        points = [
            {
                "id": i,
                "vector": embedding.tolist(),
                "payload": {
                    "text": chunk,
                    "url": str(url_input.url)
                }
            }
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings))
        ]
        
        qdrant_client.upsert(
            collection_name=COLLECTION_NAME,
            points=points
        )
        
        return {"message": f"Successfully processed URL and stored {len(chunks)} chunks"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query")
async def query(query: Query):
    """Query the RAG system"""
    try:
        # Generate embedding for the query
        query_embedding = encoder.encode(query.question)
        
        # Search in Qdrant
        search_results = qdrant_client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_embedding.tolist(),
            limit=3
        )
        
        # Extract relevant chunks
        relevant_chunks = [result.payload["text"] for result in search_results]
        
        # Construct prompt for Gemini
        context = "\n".join(relevant_chunks)
        prompt = f"""Based on the following context, please answer the question.
        
Context:
{context}

Question: {query.question}

Please provide a clear and concise answer based on the context provided."""
        
        # Generate response using Gemini
        response = model.generate_content(prompt)
        
        return {
            "answer": response.text,
            "source_chunks": relevant_chunks
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/delete-url")
async def delete_url(url_input: URLInput):
    """Delete all chunks associated with a specific URL"""
    try:
        # Get all points with matching URL
        search_response = qdrant_client.scroll(
            collection_name=COLLECTION_NAME,
            scroll_filter={
                "must": [
                    {
                        "key": "url",
                        "match": {"value": str(url_input.url)}
                    }
                ]
            },
            limit=100  # Adjust based on your needs
        )
        
        # Extract point IDs
        points = search_response[0]  # First element contains points
        point_ids = [point.id for point in points]
        
        if not point_ids:
            raise HTTPException(status_code=404, detail="No content found for this URL")
        
        # Delete points
        qdrant_client.delete(
            collection_name=COLLECTION_NAME,
            points_selector=point_ids
        )
        
        return {
            "message": f"Successfully deleted {len(point_ids)} chunks associated with the URL",
            "deleted_count": len(point_ids)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 9999))  # Use Cloud Run's PORT if available, default to 9999
    uvicorn.run(app, host="0.0.0.0", port=port)
