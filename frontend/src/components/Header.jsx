import "./Header.css";
import { FaBrain } from "react-icons/fa";

function Header() {
  return (
    <header className="header">
      <div className="header-title">
        <FaBrain className="logo" />

        <div>
          <h1>OmniBrain</h1>
          <h2>Agentic RAG</h2>
        </div>
      </div>

      <p>Upload your PDF and start chatting with your documents.</p>
    </header>
  );
}

export default Header;