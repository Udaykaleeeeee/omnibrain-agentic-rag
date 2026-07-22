import axios from "axios";

const API = axios.create({
  baseURL: "http://127.0.0.1:8000",
});

export const checkBackend = () => {
  return API.get("/health");
};

export const getSupportedFormats = () => {
  return API.get("/ingest/formats");
};

export const uploadDocument = (formData) => {
  return API.post("/ingest", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
};

export default API;