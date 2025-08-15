import axios from "axios";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export async function uploadDocument(file) {
  const formData = new FormData();
  formData.append("file", file);

  // Pass extract & save_to_db so backend actually stores the doc
  const res = await axios.post(
    `${API_BASE}/upload/?extract=true&save_to_db=true`,
    formData,
    {
      headers: { "Content-Type": "multipart/form-data" },
    }
  );
  return res.data; // returns { filename, path, doc_id, extracted_text }
}
