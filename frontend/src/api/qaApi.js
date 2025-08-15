import axios from "axios";
const API_BASE = process.env.REACT_APP_API_BASE_URL || "";

export async function askQuestion({ question, doc_id }) {
  // Use /nlp/qa endpoint that accepts {"question":"...", "doc_id": ...}
  const res = await axios.post(`${API_BASE}/nlp/qa`, { question, doc_id });
  return res.data;
}
