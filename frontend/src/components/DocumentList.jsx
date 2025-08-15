import React, { useEffect, useState } from "react";
import { getDocuments } from "../api/backend";

export default function DocumentList({ onSelect, selected }) {
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
  }, []);

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
            onClick={() =>
              onSelect({ id: d.id, filename: d.filename || d.name })
            }
          >
            <div>
              <strong>{d.filename || d.name}</strong>
            </div>
            <div className="small-muted">id: {d.id}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
