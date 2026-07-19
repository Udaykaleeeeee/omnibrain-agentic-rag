import { useRef, useState } from "react";
import {
  FaCloudUploadAlt,
  FaFilePdf,
} from "react-icons/fa";

import "./UploadSection.css";
import { uploadPDF } from "../services/api";

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
      setStatus("Please select a PDF first.");
      return;
    }

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      setLoading(true);

      const response = await uploadPDF(formData);

      console.log(response.data);

      setStatus("Document uploaded successfully.");
    } catch (error) {
      console.error(error);

      if (error.response) {
        setStatus("Upload failed.");
      } else {
        setStatus("Cannot connect to backend.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="upload-card card">

      <h2>Document Upload</h2>

      <p className="upload-subtitle">
        Securely upload your document and begin an AI-powered conversation instantly.
      </p>

      <div
        className="drop-zone"
        onClick={() => fileInputRef.current.click()}
      >

        <FaCloudUploadAlt className="cloud-icon" />

        <h3>Drag & Drop PDF Here</h3>

        <p>or click to browse</p>

        <input
          type="file"
          accept=".pdf"
          hidden
          ref={fileInputRef}
          onChange={handleFileChange}
        />

      </div>

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

      <button
        className="upload-button"
        onClick={handleUpload}
        disabled={loading}
      >
        {loading ? "Uploading..." : "Upload PDF"}
      </button>

      {status && (
        <p className="status">{status}</p>
      )}

    </div>
  );
}

export default UploadSection;