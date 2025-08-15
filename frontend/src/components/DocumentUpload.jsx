import React, { useState } from "react";
import { uploadDocument, getDocuments } from "../api/documentApi";

export default function DocumentUpload({ onUploaded, setProcessing }) {
  const [progress, setProgress] = useState(0);
  const [uploading, setUploading] = useState(false);

  const handleFileChange = async (e) => {
    if (!e.target.files?.length) return;
    const file = e.target.files[0];
    setUploading(true);
    setProcessing(true);

    try {
      const res = await uploadDocument(file, (evt) => {
        if (evt.lengthComputable) {
          setProgress(Math.round((evt.loaded * 100) / evt.total));
        }
      });

      // backend should return document id and filename; fallback to response
      const doc = {
        id: res.document_id || res.id || Math.random().toString(36).slice(2, 9),
        filename: res.filename || file.name,
      };
      onUploaded(doc);

      // Refresh server-side processing might still be working — keep a small delay or poll
    } catch (err) {
      console.error("Upload failed", err);
      alert("Upload failed. Check console.");
    } finally {
      setUploading(false);
      setProgress(0);
      setProcessing(false);
    }
  };

  return (
    <div className="card">
      <h3>Upload Document</h3>
      <input type="file" accept=".pdf,.docx,.txt" onChange={handleFileChange} />
      {uploading && <div className="small-muted">Uploading... {progress}%</div>}
    </div>
  );
}
