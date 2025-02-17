import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import Home from "./Components/Home";
import Search from "./Components/Search";
import Recommendations from "./Components/Recommendation";
import "./Style.css";

function App() {
  return (
    <Router>
      <nav className="navbar">
        <div className="nav-left">🎬 Movie Finder</div>
        <div className="nav-right">
          <Link to="/">Home</Link>
          <Link to="/search">Search</Link>
          <Link to="/recommend">Recommendations</Link>
        </div>
      </nav>

      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/search" element={<Search />} />
        <Route path="/recommend" element={<Recommendations />} />
      </Routes>
    </Router>
  );
}

export default App;
