import axios from "axios";

const API_BASE = process.env.REACT_APP_API_BASE_URL || "http://localhost:8000";

export async function askQuestion(payload) {
  const res = await axios.post(`${API_BASE}/nlp/qa`, payload);
  return res.data;
}
