import axios from "axios";

const api = axios.create({
  baseURL: "http://127.0.0.1:8000",
  timeout: 30000,
});

// =========================
// Upload Document
// =========================
export const uploadDocument = (formData, onUploadProgress) => {
  return api.post("/ingest", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
    onUploadProgress,
  });
};

// =========================
// Backend Health
// =========================
export const checkHealth = () => {
  return api.get("/health");
};
export const checkBackend = checkHealth;

// =========================
// Documents
// =========================
export const getDocuments = () => {
  return api.get("/documents");
};

export const getDocumentDetails = (documentId) => {
  return api.get(`/documents/${documentId}`);
};

// =========================
// Delete Document
// =========================
export const deleteDocument = (documentId) => {
  return api.delete(`/documents/${documentId}`);
};

export default api;