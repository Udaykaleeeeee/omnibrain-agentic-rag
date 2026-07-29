import { useRef, useState } from "react";
import {
  FaCloudUploadAlt,
  FaFilePdf,
  FaCheckCircle,
} from "react-icons/fa";
import { ClipLoader } from "react-spinners";
import { toast } from "react-toastify";

import "./UploadSection.css";
import { uploadDocument } from "../services/api";

function UploadSection() {
  const fileInputRef = useRef(null);

  const [selectedFile, setSelectedFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState("");
  const [uploadResult, setUploadResult] = useState(null);

  // -------------------------
  // File Selection
  // -------------------------

  const handleFileChange = (event) => {
    if (!event.target.files.length) return;

    const file = event.target.files[0];

    setSelectedFile(file);
    setUploadResult(null);
    setProgress(0);
    setStatus("");
  };

  // -------------------------
  // Upload
  // -------------------------

  const handleUpload = async () => {
    if (!selectedFile) {
      toast.error("Please select a document.");
      return;
    }

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      setLoading(true);
      setProgress(0);
      setStatus("");

      const response = await uploadDocument(
        formData,
        (progressEvent) => {
          if (!progressEvent.total) return;

          const percent = Math.round(
            (progressEvent.loaded * 100) /
              progressEvent.total
          );

          setProgress(percent);
        }
      );

      setUploadResult(response.data);

      setStatus(response.data.message);

      toast.success("Document uploaded successfully!");

    } catch (error) {
      console.error(error);

      if (error.response) {

        const detail = error.response.data.detail;

        if (typeof detail === "string") {
          setStatus(detail);
          toast.error(detail);
        } else if (detail?.error) {
          setStatus(detail.error);
          toast.error(detail.error);
        } else {
          setStatus("Upload failed.");
          toast.error("Upload failed.");
        }

      } else {
        setStatus("Cannot connect to backend.");
        toast.error("Backend unavailable.");
      }

    } finally {
      setLoading(false);
    }
  };

    return (
    <div className="upload-card card">

      <div className="upload-header">

        <h2>Document Upload</h2>

        <p>
          Upload PDF, DOCX or TXT files to start AI-powered document ingestion.
        </p>

      </div>

      {/* Upload Area */}

      <div
        className="drop-zone"
        onClick={() => fileInputRef.current.click()}
      >

        <FaCloudUploadAlt className="cloud-icon" />

        <h3>Drag & Drop your document</h3>

        <p>or click to browse</p>

        <span className="supported-text">
          Supported: PDF • DOCX • TXT
        </span>

        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.docx,.txt"
          hidden
          onChange={handleFileChange}
        />

      </div>

      {/* Selected File */}

      <div className="selected-file-card">

        <h4>Selected File</h4>

        {selectedFile ? (

          <div className="file-name">

            <FaFilePdf />

            <span>{selectedFile.name}</span>

          </div>

        ) : (

          <p>No file selected</p>

        )}

      </div>

      {/* Upload Progress */}

      {loading && (

        <div className="progress-wrapper">

          <div className="progress-top">

            <span>Uploading...</span>

            <span>{progress}%</span>

          </div>

          <div className="progress-bar">

            <div
              className="progress-fill"
              style={{ width: `${progress}%` }}
            ></div>

          </div>

        </div>

      )}

      {/* Upload Button */}

      <button
        className="upload-button"
        onClick={handleUpload}
        disabled={loading}
      >

        {loading ? (

          <>

            <ClipLoader
              color="#ffffff"
              size={18}
            />

            Uploading...

          </>

        ) : (

          "Upload Document"

        )}

      </button>

      {/* Status */}

      {status && (

        <div className="status-message">

          {status}

        </div>

      )}

      {/* Success Card */}

      {uploadResult && (

        <div className="success-card">

          <div className="success-title">

            <FaCheckCircle />

            <span>Document Uploaded Successfully</span>

          </div>

          <div className="success-grid">

            <div>

              <label>Filename</label>

              <p>{uploadResult.filename}</p>

            </div>

            <div>

              <label>Pages</label>

              <p>{uploadResult.total_pages}</p>

            </div>

            <div>

              <label>Chunks Created</label>

              <p>{uploadResult.chunks_created}</p>

            </div>

            <div>

              <label>OCR Pages</label>

              <p>{uploadResult.ocr_pages_used}</p>

            </div>

            <div>

              <label>Format</label>

              <p>{uploadResult.source_format}</p>

            </div>

            <div>

              <label>Status</label>

              <p>{uploadResult.status}</p>

            </div>

          </div>

        </div>

      )}

    </div>
  );

}

export default UploadSection;