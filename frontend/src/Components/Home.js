import React, { useState, useEffect } from "react";
import bgImage from "../Assets/bg.jpg";
import movieCardImage from "../Assets/movie_card.jpg";

const Home = () => {
  const [query, setQuery] = useState("");
  const [movies, setMovies] = useState([]);
  const [error, setError] = useState(null);
  const [parallaxY, setParallaxY] = useState(0);

  // 🔥 Handle Background Motion (Parallax)
  useEffect(() => {
    const handleScroll = () => setParallaxY(window.scrollY * 0.5);
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  // 🔎 Handle Movie Search
  const handleSearch = async () => {
    if (!query.trim()) return;

    try {
      const response = await fetch(`http://127.0.0.1:8000/search?q=${query}&user_id=guest`, {
        method: "GET",
        headers: { "Content-Type": "application/json" },
      });
      const data = await response.json();

      console.log("🔍 API Response:", data);

      if (data.results && data.results.length > 0) {
        setMovies(data.results);
        setError(null);
      } else {
        setMovies([]);
        setError("No movies found.");
      }
    } catch (err) {
      console.error("❌ Fetch error:", err);
      setError("Failed to fetch search results.");
    }
  };

  return (
    <div className="home-container">
      <div className="parallax-bg" style={{ backgroundImage: `url(${bgImage})`, transform: `translateY(${parallaxY}px)` }}></div>

      {/* Search Section */}
      <div className="search-section">
        <h1 className="cinematic-title">🎬 Welcome to Movie Finder</h1>
        <div className="search-bar">
          <input
            type="text"
            placeholder="Search for movies, genres, or actors..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSearch()}
          />
          <button onClick={handleSearch}>🔎</button>
        </div>
        <p className="search-subtitle">Find your next favorite movie</p>
      </div>

      {/* Movies Grid */}
      <div className="movie-grid">
        {movies.length > 0 ? (
          movies.map((movie) => (
            <div className="movie-card" key={movie.id}>
              <img src={movieCardImage} alt={movie.title} />
              <h3>{movie.title}</h3>
              <p>⭐ {movie.rating}</p>
              <div className="genre-tags">
                {movie.genre.map((g, index) => (
                  <span key={index} className="genre-tag">{g}</span>
                ))}
              </div>
            </div>
          ))
        ) : (
          error && <p className="error">{error}</p>
        )}
      </div>
    </div>
  );
};

export default Home;
