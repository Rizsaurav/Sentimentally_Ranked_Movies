import { useEffect, useState } from "react";
import recommendationsBgImage from "../Assets/recommendations.jpg"; // Background Image
import movieCardImage from "../Assets/movie_card.jpg"; // Default Movie Card Image
import "../Style.css";

const Recommendations = () => {
  const [movies, setMovies] = useState([]);
  const [error, setError] = useState(null);
  const [parallaxY, setParallaxY] = useState(0);

  // 🔥 Parallax Effect
  useEffect(() => {
    const handleScroll = () => {
      setParallaxY(window.scrollY * 0.3); // Smooth parallax effect
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/recommend?user_id=guest")
      .then((res) => res.json())
      .then((data) => {
        if (data.recommendations) {
          setMovies(data.recommendations);
        } else {
          setError("No recommendations found.");
        }
      })
      .catch(() => setError("Failed to fetch recommendations."));
  }, []);

  return (
    <div className="recommendations-container">
      {/* 🔥 Parallax Background */}
      <div className="parallax-bg"
        style={{
          backgroundImage: `url(${recommendationsBgImage})`,
          backgroundSize: "cover",
          backgroundPosition: "center",
          transform: `translateY(${parallaxY}px)`,
        }}>
      </div>

      {/* 🎬 Recommendations Section */}
      <div className="recommendations-section">
        <h1 className="cinematic-title" style={{ marginTop: "100px" }}> {/* 🔽 Lowered Title */}
          🎬 Movie Recommendations
        </h1>
        <p className="search-subtitle">Personalized suggestions based on your Sentiment Analysis done on each Review and Ratings.</p>

        {error && <p className="error">{error}</p>}

        <div className="movie-grid">
          {movies.map((movie) => (
            <div className="movie-card" key={movie.id}>
              <img 
                src={movie.image || movieCardImage} 
                alt={movie.title} 
                className="movie-poster"
              />
              <h3>{movie.title}</h3>
              <p>⭐ {movie.rating ? movie.rating.toFixed(1) : "N/A"}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Recommendations;
