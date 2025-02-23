# Gemini Harvester: Retrieval-Augmented Generation (RAG) Application

## Project Overview

Welcome to **Gemini Harvester**! This application is designed to simplify the process of extracting, processing, and querying web content. Using Google Gemini AI and Qdrant vector search, this project allows users to easily retrieve and analyze information from URLs and get intelligent answers based on that content.

## Tech Stack

Here's what powers this application:

- **Backend**: FastAPI (Python)
- **Frontend**: Next.js (React, TypeScript)
- **Database**: Qdrant (for storing and searching vectors)
- **AI Model**: Google Gemini AI
- **Deployment**:
  - Backend hosted on Google Cloud
  - Frontend hosted on Vercel
- **Styling**: Tailwind CSS

## Prerequisites

Before you get started, make sure you have:

- **Python** (3.8 or above)
- **Node.js** (16.x or above) and **npm**
- **Virtual Environment Tool** (e.g., venv)

## Environment Variables

Set up the following environment variables:

### Backend (.env)
```
QDRANT_URL=<Your Qdrant URL>
QDRANT_API_KEY=<Your Qdrant API Key>
GEMINI_API_KEY=<Your Google Gemini API Key>
COLLECTION_NAME=<Your Qdrant Collection Name>
```

## Installation and Setup

### 1. Clone the Repository

Start by cloning the repository:
```bash
git clone https://github.com/gaurav8707/ragurl
cd ragurl
```

### 2. Backend Setup (FastAPI)

1. Navigate to the backend folder:
   ```bash
   cd backend-fastapi
   ```
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the backend service:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

The backend will be running at [http://localhost:8000](http://localhost:8000).

### 3. Frontend Setup (Next.js)

1. Navigate to the frontend folder:
   ```bash
   cd ../frontend-next
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the frontend service:
   ```bash
   npm run dev
   ```

The frontend will be running at [http://localhost:3000](http://localhost:3000).

## Connecting Frontend and Backend

The frontend uses Axios to send HTTP requests to the backend. CORS middleware is configured in FastAPI to allow requests from the frontend hosted on Vercel.

## Running the Application

To test the app locally:

1. Start both backend and frontend.
2. Open [http://localhost:3000](http://localhost:3000).
3. Use the app to:
   - Extract and process content from URLs.
   - Ask questions based on the extracted content.
   - Delete content when no longer needed.

## Deployed Links

You can access the live version here:

- **Backend (FastAPI)**: [https://fastapi-rag-644291291076.asia-south1.run.app/docs](https://fastapi-rag-644291291076.asia-south1.run.app/docs)
- **Frontend (Next.js)**: [https://ragurl.vercel.app/](https://ragurl.vercel.app/)

## Challenges Faced

- **Handling Subpages**: The app doesn’t currently support extracting content from subpages. Plans are in place to implement BFS and DFS for better content extraction.
- **CORS Errors**: Encountered and resolved CORS issues when connecting the frontend to the backend.
- **Deployment Issues**: Deploying FastAPI on Render caused memory issues, so I switched to Google Cloud for more scalable deployment.

## Future Scope

- Implement BFS and DFS to handle subpages.
- Improve the UI for a more interactive experience.
- Test different databases for performance.
- Integrate advanced NLP techniques.
- Add a user feedback mechanism for RLHF to minimize hallucinations.

## Known Issues

- Content extraction errors may occur if the URL is not accessible.
- The app might not work as expected if CORS settings are incorrect.

## Contributing

Want to contribute? Here's how:

1. Fork the repository.
2. Create a new branch.
3. Make your changes.
4. Submit a pull request.

Feedback and suggestions are always welcome!

