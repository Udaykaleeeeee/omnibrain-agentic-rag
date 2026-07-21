import "./Header.css";
import { FaBrain } from "react-icons/fa";

function Header() {
  return (
    <header className="header">
      <div className="logo-wrapper">
        <div className="brain">
          <FaBrain />
        </div>

        <div className="title-group">
          <h1>OmniBrain</h1>
          <h2>Agentic RAG Platform</h2>
        </div>
      </div>

      <p>
        Upload your PDF and interact intelligently with your documents using
        Agentic AI.
      </p>
    </header>
  );
}

export default Header;