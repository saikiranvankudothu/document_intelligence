import React, { useState } from "react";
import { askQuestion } from "../api/qaApi";

export default function QASection({ selectedDoc }) {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");

  const handleAsk = async () => {
    if (!selectedDoc?.id) {
      alert("Please select a document first.");
      return;
    }
    const res = await askQuestion({
      question,
      doc_id: selectedDoc.id,
    });
    setAnswer(res.answer);
  };

  return (
    <div>
      <input
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        placeholder="Ask a question about this document..."
      />
      <button onClick={handleAsk}>Ask</button>
      {answer && (
        <p>
          <strong>Answer:</strong> {answer}
        </p>
      )}
    </div>
  );
}
