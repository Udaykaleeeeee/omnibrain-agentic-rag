import { useEffect, useState } from "react";
import "./RecentDocuments.css";
import {
  FaFilePdf,
  FaArrowRight,
  FaClock,
  FaTrash,
} from "react-icons/fa";

import {
  getDocuments,
  deleteDocument,
} from "../services/api";

function RecentDocuments({
  selectedDocument,
  setSelectedDocument,
}) {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchDocuments = async () => {
    try {
      const response = await getDocuments();

      const docs = response.data.documents || [];
      console.log("Documents API Response:", docs);

      setDocuments(docs);
      console.log("Documents State:", docs.length);

      // Automatically select the first document
      if (docs.length > 0 && !selectedDocument) {
        setSelectedDocument(docs[0]);
      }

    } catch (error) {
      console.error("Failed to fetch documents:", error);
    } finally {
      setLoading(false);
    }
  };
  const handleDelete = async (documentId) => {
  try {
    await deleteDocument(documentId);

    const updatedDocs = documents.filter(
      (doc) => doc.document_id !== documentId
    );

    setDocuments(updatedDocs);

    if (
      selectedDocument?.document_id === documentId
    ) {
      setSelectedDocument(
        updatedDocs.length > 0
          ? updatedDocs[0]
          : null
      );
    }
  } catch (error) {
    console.error("Delete failed:", error);
  }
};

  useEffect(() => {
  fetchDocuments();

  const interval = setInterval(fetchDocuments, 5000);

  return () => clearInterval(interval);
}, []);

  return (
    <section className="recent-documents card fade">

      <div className="recent-header">

        <div>
          <h2>Recent Documents</h2>
          <p>Recently processed knowledge sources.</p>
        </div>

        <button>
          View All
          <FaArrowRight />
        </button>

      </div>

      {loading ? (

        <div className="empty-state">
          Loading documents...
        </div>

      ) : documents.length === 0 ? (

        <div className="empty-state">
          No documents uploaded yet.
        </div>

      ) : (

        <div className="document-list">

          {documents.map((doc) => (

            <div
              key={doc.document_id}
              onClick={() => setSelectedDocument(doc)}
              className={`document-card ${
                selectedDocument?.document_id === doc.document_id
                  ? "selected-document"
                  : ""
              }`}
            >

              <div className="document-left">

                <div className="pdf-icon">
                  <FaFilePdf />
                </div>

                <div>

                  <h3>{doc.filename}</h3>

                  <span>
                    {doc.source_format.toUpperCase()} • {doc.total_pages} Pages
                  </span>

                </div>

              </div>

              <div className="document-right">

                <div className="time">

                  <FaClock />

                  {new Date(doc.ingested_at).toLocaleString()}

                </div>

                <div className="document-actions">

  <span className="ready">
    Ready
  </span>

  <button
    className="delete-btn"
    onClick={(e) => {
      e.stopPropagation();
      handleDelete(doc.document_id);
    }}
  >
    <FaTrash />
  </button>

</div>

              </div>

            </div>

          ))}

        </div>

      )}

    </section>
  );
}

export default RecentDocuments;