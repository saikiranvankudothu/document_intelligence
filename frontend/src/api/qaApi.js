import axios from "axios";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export async function askQuestion(payload) {
  const res = await axios.post(`${API_BASE}/nlp/qa`, payload);
  return res.data;
}
