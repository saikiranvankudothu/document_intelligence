import axios from "axios";

export const getDocuments = async () => {
  const res = await axios.get("http://localhost:8000/documents");
  return res.data;
};

export const getSummary = async (docId) => {
  const res = await axios.get(`http://localhost:8000/summary/${docId}`);
  return res.data;
};

export const getAnswer = async (docId, question) => {
  const res = await axios.post(`http://localhost:8000/qa/${docId}`, {
    question,
  });
  return res.data;
};

export const getFlowchart = async (docId) => {
  const res = await axios.get(`http://localhost:8000/flowchart/${docId}`);
  return res.data;
};
