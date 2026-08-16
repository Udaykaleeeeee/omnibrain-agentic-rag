import Accordion from "./Accordion";
import {
  FaFilePdf,
  FaLayerGroup,
  FaSearch,
  FaCheckCircle,
  FaFileAlt,
} from "react-icons/fa";

import "./DocumentInsights.css";

function DocumentInsights({ selectedDocument }) {
  if (!selectedDocument) {
    return (
      <Accordion title="Document Overview">
        <div className="empty-overview">
          Select a document from Recent Documents.
        </div>
      </Accordion>
    );
  }

  const fileName =
    selectedDocument.filename.length > 35
      ? selectedDocument.filename.slice(0, 35) + "..."
      : selectedDocument.filename.replace(".pdf", "");

  return (
    <Accordion title="Document Overview">
      <div className="overview-grid">

        <div className="overview-card document-card-large">
          <FaFilePdf className="document-icon" />
          <p className="document-label">Selected Document</p>
          <h3 className="document-name">{fileName}</h3>
        </div>

        <div className="overview-card">
          <FaFileAlt />
          <h2>{selectedDocument.total_pages}</h2>
          <p>Total Pages</p>
        </div>

        <div className="overview-card">
          <FaSearch />
          <h2>{selectedDocument.ocr_pages_used}</h2>
          <p>OCR Pages</p>
        </div>

        <div className="overview-card">
          <FaLayerGroup />
          <h2>{selectedDocument.chunk_count}</h2>
          <p>Chunks Created</p>
        </div>

        <div className="overview-card">
          <FaCheckCircle />
          <h2>Ready</h2>
          <p>Status</p>
        </div>

      </div>
    </Accordion>
  );
}

export default DocumentInsights;