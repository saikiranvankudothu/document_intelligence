import { useState } from "react";
import axios from "axios";

export default function FileUpload({ onUploadComplete }) {
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const formData = new FormData();
    formData.append("file", file);

    setLoading(true);
    try {
      await axios.post("http://localhost:8000/upload", formData, {
        onUploadProgress: (event) => {
          setProgress(Math.round((event.loaded * 100) / event.total));
        },
      });
      onUploadComplete();
    } catch (err) {
      console.error("Upload failed:", err);
    }
    setLoading(false);
  };

  return (
    <div className="p-4 border rounded-lg">
      <input type="file" onChange={handleFileUpload} />
      {loading && <p>Uploading... {progress}%</p>}
    </div>
  );
}
