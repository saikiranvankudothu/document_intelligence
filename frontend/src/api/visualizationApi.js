import axios from "axios";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export async function getFlowchart(docId) {
  const res = await axios.get(`${API_BASE}/nlp/visualization/${docId}`);
  return res.data;
}
