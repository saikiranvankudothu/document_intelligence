import axios from "axios";
const API_BASE = process.env.REACT_APP_API_BASE_URL || "";

export async function uploadDocument(file, onUploadProgress) {
  const form = new FormData();
  form.append("file", file);
  // adjust endpoint path if your backend uses /upload/ or /api/upload
  const res = await axios.post(`${API_BASE}/upload/`, form, {
    headers: { "Content-Type": "multipart/form-data" },
    onUploadProgress,
  });
  return res.data;
}

export async function getDocuments() {
  const res = await axios.get(`${API_BASE}/documents`);
  return res.data;
}
