import axios from "axios";
const API_BASE = process.env.REACT_APP_API_BASE_URL || "";

export async function getSummary(docId) {
  try {
    // Try direct document summary endpoint
    const res = await axios.get(`${API_BASE}/nlp/summary/${docId}`);
    return res.data;
  } catch (err) {
    // fallback: call generic endpoint to fetch and summarize by id
    // Adjust to your backend routes; we return empty summary if not available
    console.warn("summary endpoint failed:", err.message);
    return { summary: "" };
  }
}
