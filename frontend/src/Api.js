import axios from "axios";

// Base URL of your FastAPI backend
const API_BASE_URL = "http://127.0.0.1:8000";  // Update if backend is running on a different port

// 🔎 Search Movies
export const searchMovies = async (query, userId = "guest") => {
    try {
        const response = await axios.get(`${API_BASE_URL}/search`, {
            params: { q: query, user_id: userId }
        });
        return response.data;
    } catch (error) {
        console.error("Error fetching search results:", error);
        return { error: "Failed to fetch search results" };
    }
};

// 🎯 Recommend Movies
export const recommendMovies = async (userId = "guest") => {
    try {
        const response = await axios.get(`${API_BASE_URL}/recommend`, {
            params: { user_id: userId }
        });
        return response.data;
    } catch (error) {
        console.error("Error fetching recommendations:", error);
        return { error: "Failed to fetch recommendations" };
    }
};
