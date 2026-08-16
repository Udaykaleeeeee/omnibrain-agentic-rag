import "./Navbar.css";
import { FaBrain } from "react-icons/fa";

function Navbar() {
  const scrollToSection = (id) => {
    document.getElementById(id)?.scrollIntoView({
      behavior: "smooth",
    });
  };

  return (
    <nav className="navbar">

      <div className="navbar-logo">

        <FaBrain />

        <span>OmniBrain</span>

      </div>

      <div className="navbar-links">

        <button onClick={() => scrollToSection("upload")}>
          Upload
        </button>

        <button onClick={() => scrollToSection("pipeline")}>
          Pipeline
        </button>

        <button onClick={() => scrollToSection("documents")}>
          Documents
        </button>

        <button onClick={() => scrollToSection("overview")}>
          Overview
        </button>

        <button onClick={() => scrollToSection("chunks")}>
          Chunks
        </button>

        <button onClick={() => scrollToSection("status")}>
          Status
        </button>

      </div>

    </nav>
  );
}

export default Navbar;