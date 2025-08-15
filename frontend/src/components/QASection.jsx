import React, { useState } from "react";
import { askQuestion } from "../api/qaApi";
import Loader from "./Loader";

export default function QASection({ docId }) {
  const [q, setQ] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);

  const handleAsk = async () => {
    if (!q.trim()) return;
    setLoading(true);
    setAnswer("");
    try {
      const res = await askQuestion({ question: q, doc_id: docId });
      setAnswer(res.answer || res);
    } catch (e) {
      console.error(e);
      setAnswer("Failed to get an answer.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h3>Q & A</h3>
      <input
        value={q}
        onChange={(e) => setQ(e.target.value)}
        placeholder="Ask a question..."
        style={{ width: "100%", padding: "8px", marginBottom: "8px" }}
      />
      <button onClick={handleAsk} disabled={loading}>
        Ask
      </button>
      {loading && <Loader text="Generating answer..." />}
      {answer && (
        <div style={{ marginTop: 8 }}>
          <strong>Answer:</strong>
          <div>{answer}</div>
        </div>
      )}
    </div>
  );
}
