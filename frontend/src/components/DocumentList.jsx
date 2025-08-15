import React, { useEffect, useState } from "react";
import { getDocuments } from "../api/backend";
import axios from "axios";

export default function DocumentList({ onSelect, selected, reloadTrigger }) {
  const [docs, setDocs] = useState([]);
  const [loading, setLoading] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      const data = await getDocuments();
      setDocs(data || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, [reloadTrigger]); // reload when trigger changes

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this document?"))
      return;
    try {
      await axios.delete(`http://localhost:8000/documents/${id}`);
      // Reload list after deletion
      load();
      // If the deleted doc was selected, clear selection
      if (selected?.id === id) {
        onSelect(null);
      }
    } catch (err) {
      console.error(err);
      alert("Failed to delete document");
    }
  };

  return (
    <div>
      <h3>Documents</h3>
      {loading && <div className="small-muted">Loading documents...</div>}
      <div>
        {docs.length === 0 && !loading && (
          <div className="small-muted">No documents yet</div>
        )}
        {docs.map((d) => (
          <div
            key={d.id}
            className={`document-item ${
              selected?.id === d.id ? "selected" : ""
            }`}
          >
            <div
              style={{ cursor: "pointer" }}
              onClick={() =>
                onSelect({ id: d.id, filename: d.filename || d.name })
              }
            >
              <strong>{d.filename || d.name}</strong>
              <div className="small-muted">id: {d.id}</div>
            </div>
            <button
              style={{
                background: "#dc2626",
                marginTop: "4px",
                padding: "4px 8px",
                borderRadius: "4px",
              }}
              onClick={() => handleDelete(d.id)}
            >
              Delete
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
