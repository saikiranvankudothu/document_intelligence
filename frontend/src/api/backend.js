import axios from "axios";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export const getDocuments = async () => {
  const res = await axios.get(`${API_BASE}/documents`);
  return res.data;
};

export const getSummary = async (docId) => {
  const res = await axios.get(`${API_BASE}/nlp/summary/${docId}`);
  return res.data;
};

export const getAnswer = async (docId, question) => {
  const res = await axios.post(`${API_BASE}/nlp/qa`, {
    question,
    doc_id: docId,
  });
  return res.data;
};

export const getFlowchart = async (docId) => {
  const res = await axios.get(`${API_BASE}/visualization/${docId}`);
  return res.data;
};
