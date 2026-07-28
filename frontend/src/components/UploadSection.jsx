import { useRef, useState } from "react";
import {
  FaCloudUploadAlt,
  FaFilePdf,
  FaArrowRight,
  FaCheckCircle,
} from "react-icons/fa";

import "./UploadSection.css";
import { uploadDocument } from "../services/api";

function UploadSection() {
  const fileInputRef = useRef(null);

  const [selectedFile, setSelectedFile] = useState(null);
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e) => {
    if (e.target.files.length > 0) {
      setSelectedFile(e.target.files[0]);
      setStatus("");
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setStatus("Please select a document first.");
      return;
    }

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      setLoading(true);

      const response = await uploadDocument(formData);

      console.log(response.data);

      setStatus("Document uploaded successfully!");

    } catch (error) {

        console.error("ERROR:", error);
        console.error("Response:", error.response);
        console.error("Request:", error.request);

        if (error.response) {
          console.log("Backend Error Data:", error.response.data);
          setStatus("Upload failed.");
        } else {
          setStatus("Cannot connect to backend.");
        }
      } finally {

    }
  };

  return (

    <section className="upload-card card fade">

      <div className="upload-header">

        <h2>Upload Knowledge</h2>

        <p>

          Upload PDF, DOCX or TXT documents and let OmniBrain
          transform them into an intelligent searchable knowledge base.

        </p>

      </div>

      <div
        className="drop-zone"
        onClick={() => fileInputRef.current.click()}
      >

        <div className="upload-icon">

          <FaCloudUploadAlt />

        </div>

        <h3>

          Drag & Drop your document

        </h3>

        <p>

          or click to browse from your computer

        </p>

        <div className="supported-tags">

          <span>PDF</span>

          <span>DOCX</span>

          <span>TXT</span>

        </div>

        <input
          type="file"
          accept=".pdf,.docx,.txt"
          hidden
          ref={fileInputRef}
          onChange={handleFileChange}
        />

      </div>

      <div className="selected-card">

        <div>

          <h4>

            Selected Document

          </h4>

          {selectedFile ? (

            <div className="file-row">

              <FaFilePdf />

              <div>

                <strong>{selectedFile.name}</strong>

                <small>

                  Ready for processing

                </small>

              </div>

            </div>

          ) : (

            <p>

              No document selected yet.

            </p>

          )}

        </div>

        {selectedFile && (

          <FaCheckCircle className="success-icon" />

        )}

      </div>

      <button
        className="upload-button"
        onClick={handleUpload}
        disabled={loading}
      >

        {loading ? "Uploading..." : "Upload Document"}

        {!loading && <FaArrowRight />}

      </button>

      {status && (

        <div className="upload-status">

          {status}

        </div>

      )}

    </section>

  ); 
}

export default UploadSection;