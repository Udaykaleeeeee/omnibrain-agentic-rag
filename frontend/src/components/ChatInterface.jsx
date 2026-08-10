import { useState } from "react";
import { FaComments, FaPaperPlane, FaFileAlt } from "react-icons/fa";

import "./ChatInterface.css";

function ChatInterface() {
  const [question, setQuestion] = useState("");

  return (
    <section className="chat-section card">

      <div className="chat-header">

        <span className="chat-badge">
          AI Question Answering
        </span>

        <h2>Ask Your Documents</h2>

        <p>
          Query uploaded files and retrieve AI-generated answers with citations.
        </p>

      </div>

      <div className="chat-input-wrapper">

        <input
          type="text"
          className="chat-input"
          placeholder="Ask a question about uploaded documents..."
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
        />

        <button className="ask-btn">
          <FaPaperPlane />
          Ask
        </button>

      </div>

      <div className="answer-card">

        <div className="answer-header">
          <h3>Answer</h3>
        </div>

        <div className="answer-empty">

          <FaComments />

          <h3>No Question Asked Yet</h3>

          <p>
            Upload a document and ask a question to begin retrieval.
          </p>

        </div>

      </div>

      <div className="citation-box">

        <div className="citation-title">

          <FaFileAlt />

          <span>Citations</span>

        </div>

        <p>No citations available yet.</p>

      </div>

    </section>
  );
}

export default ChatInterface;