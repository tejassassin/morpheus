import { useEffect } from "react";
import "./App.css";
import { useParams } from "react-router-dom";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import Home from "./Home";
import bg from "./images/bg.jpg";

function App() {
  return (
    <div className="App" style={{ backgroundImage: `url(${bg})` }}>
      <Router>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/:command" element={<Home />} />
        </Routes>
      </Router>
    </div>
  );
}

export default App;
