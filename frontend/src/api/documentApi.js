import axios from "axios";

const API_BASE = process.env.REACT_APP_API_BASE_URL || "http://localhost:8000";

export async function uploadDocument(file) {
  const formData = new FormData();
  formData.append("file", file);
  const res = await axios.post(`${API_BASE}/upload/`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return res.data;
}
