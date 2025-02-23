# Gemini Harvester: Retrieval-Augmented Generation (RAG) Application

## Live Demo

- **Backend (FastAPI)**: [Google Cloud Backend](https://fastapi-rag-644291291076.asia-south1.run.app/docs)
- **Frontend (Next.js)**: [Vercel Frontend](https://ragurl.vercel.app/)

## Project Overview

Welcome to **Gemini Harvester**! This project is a Retrieval-Augmented Generation (RAG) application designed to make it easy to extract, process, and query web content. Using Google Gemini AI and Qdrant vector search, Gemini Harvester allows users to extract information from URLs, embed text into a vector database, and generate intelligent responses based on the processed content.

## Tech Stack

This project uses the following technologies:

- **Backend**: FastAPI (Python)
- **Frontend**: Next.js (React, TypeScript)
- **Database**: Qdrant (for vector storage and search)
- **AI Model**: Google Gemini AI
- **Deployment**:
  - Backend hosted on Google Cloud
  - Frontend hosted on Vercel
- **Styling**: Tailwind CSS

## Prerequisites

To run this project locally, ensure that you have:

- **Python** (3.8 or above)
- **Node.js** (16.x or above) and **npm**
- **Virtual Environment Tool** (e.g., venv)

## Environment Variables

The following environment variables are required for the backend:

```
QDRANT_URL=<Your Qdrant URL>
QDRANT_API_KEY=<Your Qdrant API Key>
GEMINI_API_KEY=<Your Google Gemini API Key>
COLLECTION_NAME=<Your Qdrant Collection Name>
```

## Installation and Setup

### 1. Clone the Repository

Clone the repository and navigate to the project directory:

```bash
git clone https://github.com/gaurav8707/ragurl
cd ragurl
```

### 2. Backend Setup (FastAPI)

1. Navigate to the backend directory:
   ```bash
   cd backend-fastapi
   ```
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the backend service:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

The backend service should be running at [http://localhost:8000](http://localhost:8000).

### 3. Frontend Setup (Next.js)

1. Navigate to the frontend directory:
   ```bash
   cd ../frontend-next
   ```
2. Update the API base URL in the code:
   Open the frontend code file where `API_BASE_URL` is defined in `app/page.tsx` and replace the existing cloud URL with your local backend URL:
   ```javascript
   const API_BASE_URL = "http://localhost:8000";
   ```
3. Install dependencies:
   ```bash
   npm install
   ```
4. Run the frontend service:
   ```bash
   npm run dev
   ```

The frontend service should be running at [http://localhost:3000](http://localhost:3000).

## Connecting the Frontend with the Backend

The frontend connects to the backend using Axios for HTTP requests. CORS middleware is configured in the FastAPI backend to allow requests from the frontend hosted on Vercel.

## Using the Application

1. Open [http://localhost:3000](http://localhost:3000) in your browser.
2. You can:
   - Enter a URL to extract and process content.
   - Submit a query to get answers based on the processed content.
   - Delete processed URLs when needed.

## Challenges Faced

- **Handling Subpages**: Currently, the app does not support extracting content from subpages. BFS and DFS approaches are planned for future improvements.
- **CORS Policy Errors**: Encountered CORS policy issues while connecting the FastAPI backend with the Next.js frontend, resolved with proper CORS configuration.
- **Deployment Issues**: Deploying FastAPI on platforms like Render led to memory issues, so I opted for Google Cloud, which handled scaling more effectively.

## Future Scope

- Implement BFS and DFS to handle subpage extraction.
- Enhance the UI to be more user-friendly and interactive.
- Explore other databases for better performance.
- Integrate advanced NLP techniques for improved content analysis.
- Add a user feedback mechanism for RLHF to minimize AI hallucinations and improve response accuracy.

## Known Issues

- Processing errors may occur if the URL content extraction fails.
- CORS misconfigurations can lead to connectivity issues between the frontend and backend.

## Contributing

Interested in contributing? Follow these steps:

1. Fork the repository.
2. Create a new branch for your feature.
3. Make your changes.
4. Submit a pull request.

Feedback and suggestions are always welcome!

