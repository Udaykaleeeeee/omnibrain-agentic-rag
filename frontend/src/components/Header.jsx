import "./Header.css";
import { FaBrain } from "react-icons/fa";
import { FaArrowRight } from "react-icons/fa";

function Header() {
  return (
    <header className="hero fade">

      <div className="hero-glow"></div>

      <div className="hero-logo">

        <FaBrain />

      </div>

      <span className="hero-badge">
        AI Powered Document Intelligence
      </span>

      <h1>

        OmniBrain

      </h1>

      <h2>

        Intelligent Knowledge Workspace

      </h2>

      <p>

        Upload, process and transform documents into an
        intelligent searchable knowledge base using OCR,
        embeddings and Retrieval Augmented Generation.

      </p>

      <button className="hero-btn">

        Upload Document

        <FaArrowRight />

      </button>

    </header>
  );
}

export default Header;