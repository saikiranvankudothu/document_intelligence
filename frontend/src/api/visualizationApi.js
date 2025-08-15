import axios from "axios";
const API_BASE = process.env.REACT_APP_API_BASE_URL || "";

export async function getFlowchart(docId) {
  const res = await axios.get(`${API_BASE}/visualization/${docId}`);
  return res.data;
}
