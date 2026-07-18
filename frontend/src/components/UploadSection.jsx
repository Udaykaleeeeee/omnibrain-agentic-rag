import { useRef, useState } from "react";
import { FaFilePdf, FaCloudUploadAlt } from "react-icons/fa";
import { uploadPDF } from "../services/api";
import "./UploadSection.css";

function UploadSection() {
  const fileInputRef = useRef(null);

  const [selectedFile, setSelectedFile] = useState(null);
  const [status, setStatus] = useState("");

  const handleFileChange = (event) => {
    if (event.target.files.length > 0) {
      setSelectedFile(event.target.files[0]);
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
      const response = await uploadPDF(formData);
      setStatus(response.data.message);
    } catch (error) {
      console.error(error);

      if (error.response) {
        setStatus(error.response.data.message || "Upload failed.");
      } else {
        setStatus("Cannot connect to backend.");
      }
    }
  };

  return (
    <div className="upload-card">
      <h2 className="upload-heading">
        <FaFilePdf className="pdf-icon" />
        Upload PDF
      </h2>

      <p className="subtitle">
        Upload your PDF to begin your AI conversation.
      </p>

      <div className="upload-box">
        <div className="upload-icon">
          <FaCloudUploadAlt />
        </div>

        <p className="drag-text">
          Select a PDF to upload
        </p>

        <span>or</span>

        <input
          type="file"
          accept=".pdf"
          hidden
          ref={fileInputRef}
          onChange={handleFileChange}
        />

        <button
          className="select-btn"
          onClick={() => fileInputRef.current.click()}
        >
          Select PDF
        </button>
      </div>

      <div className="file-info">
        <strong>Selected File</strong>

        {selectedFile ? (
          <p className="selected-file">
            <FaFilePdf className="small-icon" />
            {selectedFile.name}
          </p>
        ) : (
          <p>No PDF selected</p>
        )}
      </div>

      <button
        className="upload-btn"
        onClick={handleUpload}
      >
        Upload PDF
      </button>

      {status && (
        <p className="status-message">
          {status}
        </p>
      )}
    </div>
  );
}

export default UploadSection;