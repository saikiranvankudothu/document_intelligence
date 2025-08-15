import React, { useState } from "react";
import { uploadDocument } from "../api/documentApi";

export default function DocumentUpload({ onUploadComplete, setProcessing }) {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleUpload = async () => {
    if (!file) {
      alert("Please select a file first.");
      return;
    }
    setLoading(true);
    setProcessing(true);
    try {
      const result = await uploadDocument(file);
      if (onUploadComplete) onUploadComplete(result); // pass doc info to App
    } catch (error) {
      console.error("Upload failed", error);
      alert("Failed to upload document");
    } finally {
      setLoading(false);
      setProcessing(false);
    }
  };

  return (
    <div>
      <input type="file" onChange={(e) => setFile(e.target.files[0])} />
      <button onClick={handleUpload} disabled={loading}>
        {loading ? "Uploading..." : "Upload"}
      </button>
    </div>
  );
}
