import axios from "axios";

const API_BASE = process.env.REACT_APP_API_BASE_URL || "http://localhost:8000";

export async function getFlowchart(docId) {
  const res = await axios.get(`${API_BASE}/visualization/${docId}`);
  return res.data;
}
