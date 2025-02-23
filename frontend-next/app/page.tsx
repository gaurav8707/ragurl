"use client";
import { useState } from "react";
import axios from "axios";

const API_BASE_URL = "https://fastapi-rag-644291291076.asia-south1.run.app";

export default function Home() {
  const [url, setUrl] = useState("");
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [queryloading, setQueryLoading] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [urlError, setUrlError] = useState("");
  const [queryError, setQueryError] = useState("");
  const [deleteError, setDeleteError] = useState("");
  const [success, setSuccess] = useState("");
  const [deleteSuccess, setDeleteSuccess] = useState("");
  const [queryResponse, setQueryResponse] = useState("");

  // Function to Process URL
  const handleUrlSubmit = async (): Promise<void> => {
    if (!url.trim()) {
      setUrlError("Please enter a valid URL");
      return;
    }

    setLoading(true);
    setUrlError("");
    setSuccess("");

    try {
      const response = await axios.post(`${API_BASE_URL}/process-url`, {
        url: url,
      });

      setSuccess("URL processed successfully!");
      console.log("Scrape Response:", response.data);
    } catch (error) {
      if (axios.isAxiosError(error)) {
        setUrlError(error.response?.data?.message || "Failed to process URL");
        console.error("API Error:", error.response?.data);
      } else {
        setUrlError("An unexpected error occurred");
        console.error("Unexpected Error:", error);
      }
    } finally {
      setLoading(false);
    }
  };

  // Function to Delete URL
  const handleDeleteUrl = async (): Promise<void> => {
    if (!url.trim()) {
      setDeleteError("Please enter a valid URL to delete");
      return;
    }

    setDeleting(true);
    setDeleteError("");
    setDeleteSuccess("");

    try {
      const response = await axios.delete(`${API_BASE_URL}/delete-url`, {
        data: { url: url }, // Sending URL as request body
      });

      setDeleteSuccess("URL deleted successfully!");
      console.log("Delete Response:", response.data);
    } catch (error) {
      if (axios.isAxiosError(error)) {
        setDeleteError(error.response?.data?.message || "Failed to delete URL");
        console.error("API Error:", error.response?.data);
      } else {
        setDeleteError("An unexpected error occurred");
        console.error("Unexpected Error:", error);
      }
    } finally {
      setDeleting(false);
    }
  };

  // Function to Query
  const handleQuerySubmit = async (): Promise<void> => {
    if (!query.trim()) {
      setQueryError("Please enter a valid query");
      return;
    }

    setQueryLoading(true);
    setQueryError("");
    setQueryResponse("");

    try {
      const response = await axios.post(`${API_BASE_URL}/query`, {
        question: query,
      });

      // Extract the 'answer' field from the response
      setQueryResponse(response.data.answer);
      console.log("Chat Response:", response.data);
    } catch (error) {
      if (axios.isAxiosError(error)) {
        setQueryError(error.response?.data?.message || "Failed to process query");
        // console.error("API Error:", error.response?.data);
      } else {
        setQueryError("An unexpected error occurred");
        console.error("Unexpected Error:", error);
      }
    } finally {
      setQueryLoading(false);
    }
  };

  return (
    <div className="bg-gray-900 text-white flex flex-col items-center justify-center min-h-screen">
      <div className="flex flex-col items-center w-full max-w-3xl px-4">
        <div className="flex flex-row p-4 px-10 m-4 rounded-xl text-3xl font-semibold bg-blue-700 shadow-lg">
        Gemini Harvestor
        </div>

        {/* URL Input Section */}
        <div className="flex flex-col w-full bg-red-800 m-4 p-6 rounded-2xl shadow-lg">
          <div className="flex flex-col md:flex-row gap-4">
            <input
              type="text"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="Please enter your URL"
              className="flex-1 p-3 text-black rounded-lg text-lg"
              disabled={loading || deleting}
            />
            <button
              onClick={handleUrlSubmit}
              disabled={loading}
              className={`px-6 py-3 rounded-lg text-lg font-medium transition-colors
                ${loading
                  ? "bg-gray-500 cursor-not-allowed"
                  : "bg-amber-600 hover:bg-amber-500 cursor-pointer"
                }`}
            >
              {loading ? "Processing..." : "Submit"}
            </button>
            <button
              onClick={handleDeleteUrl}
              disabled={deleting}
              className={`px-6 py-3 rounded-lg text-lg font-medium transition-colors
                ${deleting
                  ? "bg-gray-500 cursor-not-allowed"
                  : "bg-red-600 hover:bg-red-500 cursor-pointer"
                }`}
            >
              {deleting ? "Deleting..." : "Delete"}
            </button>
          </div>

          {urlError && (
            <div className="mt-4 p-3 bg-red-600 text-white rounded-lg">{urlError}</div>
          )}

          {success && (
            <div className="mt-4 p-3 bg-green-600 text-white rounded-lg">{success}</div>
          )}

          {deleteError && (
            <div className="mt-4 p-3 bg-red-600 text-white rounded-lg">{deleteError}</div>
          )}

          {deleteSuccess && (
            <div className="mt-4 p-3 bg-green-600 text-white rounded-lg">{deleteSuccess}</div>
          )}
        </div>

        {/* Query Input Section */}
        <div className="flex flex-col w-full bg-red-800 m-4 p-6 rounded-2xl">
          <div className="flex flex-col md:flex-row gap-4">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Enter your query:"
              className="flex-1 p-3 text-black rounded-lg text-lg"
              disabled={queryloading}
            />
            <button
              onClick={handleQuerySubmit}
              disabled={queryloading}
              className={`px-6 py-3 rounded-lg text-lg font-medium transition-colors
                ${queryloading
                  ? "bg-gray-500 cursor-not-allowed"
                  : "bg-amber-600 hover:bg-amber-500 cursor-pointer"
                }`}
            >
              {queryloading ? "Processing..." : "Ask"}
            </button>
          </div>

          {queryError && (
            <div className="mt-4 p-3 bg-red-600 text-white rounded-lg">{queryError}</div>
          )}

          {queryResponse && (
            <div className="mt-4 p-3 bg-green-600 text-white rounded-lg">
              <strong>Response:</strong> {queryResponse}
            </div>
          )}
        </div>
      </div>

      <footer className="w-full bg-gray-800 text-white p-4 text-center mt-auto">
        <p className="text-sm">
          Gemini Harvester is a Retrieval-Augmented Generation (RAG) application that allows users to extract, 
          process, and query web content using Google Gemini AI and Qdrant vector search. The app enables 
          seamless knowledge extraction from URLs, embedding of text into a vector database, and intelligent 
          response generation using a large language model.
        </p>
      </footer>
    </div>
  );
}
// export const metadata = {
//   title: "Gemini Harvestor",
//   description: "Gemini Harvester is a Retrieval-Augmented Generation (RAG) application that allows users to extract, process, and query web content using Google Gemini AI and Qdrant vector search. The app enables seamless knowledge extraction from URLs, embedding of text into a vector database, and intelligent response generation using a large language model.",
// }
