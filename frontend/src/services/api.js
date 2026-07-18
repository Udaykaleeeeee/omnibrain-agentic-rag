import axios from "axios";

const API = axios.create({
  baseURL: "http://127.0.0.1:8000",
});

export const uploadPDF = (formData) => {
  return API.post("/upload-pdf", formData);
};

export default API;