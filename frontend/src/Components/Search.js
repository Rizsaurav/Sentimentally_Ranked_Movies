import { useState, useEffect } from "react";
import searchBgImage from "../Assets/search.jpg"; // Different background image
import movieCardImage from "../Assets/movie_card.jpg";
import "../Style.css";

const Search = () => {
  const [query, setQuery] = useState("");
  const [movies, setMovies] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [parallaxY, setParallaxY] = useState(0);

  // 🔥 Parallax Effect
  useEffect(() => {
    const handleScroll = () => {
      setParallaxY(window.scrollY * 0.3); // Smooth parallax effect
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  // 🔎 Handle Movie Search
  const handleSearch = async () => {
    if (!query.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`http://127.0.0.1:8000/search?q=${query}&user_id=guest`);
      const data = await response.json();

      if (data.results && data.results.length > 0) {
        setMovies(data.results);
      } else {
        setMovies([]);
        setError("No movies found.");
      }
    } catch (err) {
      setError("Failed to fetch search results.");
    }

    setLoading(false);
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter") handleSearch();
  };

  return (
    <div className="search-container">
      {/* 🔥 Parallax Background */}
      <div className="parallax-bg"
        style={{
          backgroundImage: `url(${searchBgImage})`,
          backgroundSize: "cover",
          backgroundPosition: "center",
          transform: `translateY(${parallaxY}px)`,
        }}>
      </div>

      {/* 🔎 Search Section */}
      <div className="search-section">
        <h1 className="cinematic-title">🔎 Search for Movies</h1>
        <div className="search-bar">
          <input
            type="text"
            placeholder="Enter movie title..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
          />
          <button onClick={handleSearch} disabled={loading}>
            {loading ? "Searching..." : "Search"}
          </button>
        </div>
        <p className="search-subtitle">Find movies by title, genre, or actor</p>
      </div>

      {/* 🎬 Movies Grid */}
      {movies.length > 0 && (
        <div className="movie-grid">
          {movies.map((movie) => (
            <div className="movie-card" key={movie.id}>
              {/* 🎭 Genre Tags */}
              <div className="genre-tags">
                {movie.genre.map((genre, index) => (
                  <span key={index} className="genre-tag">{genre}</span>
                ))}
              </div>

              <img 
                src={movie.poster || movieCardImage} 
                alt={movie.title} 
              />
              <h3>{movie.title}</h3>
              <p>⭐ {movie.rating ? movie.rating.toFixed(1) : "N/A"}</p>
            </div>
          ))}
        </div>
      )}

      {error && <p className="error">{error}</p>}
    </div>
  );
};

export default Search;
