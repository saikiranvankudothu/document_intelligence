import React, { useState, useEffect } from "react";
import { getDocuments } from "../api/backend"; // uses fixed route
import { getSummary } from "../api/summarizationApi";
import { getFlowchart } from "../api/visualizationApi";
import QASection from "../components/QASection";

export default function Dashboard() {
  const [documents, setDocuments] = useState([]);
  const [selectedDoc, setSelectedDoc] = useState(null);
  const [summary, setSummary] = useState("");
  const [flowchart, setFlowchart] = useState("");

  useEffect(() => {
    getDocuments().then(setDocuments);
  }, []);

  const loadDocData = async (doc) => {
    setSelectedDoc(doc);
    try {
      const sumData = await getSummary(doc.id);
      setSummary(sumData.summary || "");
      const flowData = await getFlowchart(doc.id);
      setFlowchart(flowData.mermaid || "");
    } catch (err) {
      console.error("Error loading document data", err);
    }
  };

  return (
    <div>
      <h1>Document Dashboard</h1>
      <ul>
        {documents.map((doc) => (
          <li key={doc.id} onClick={() => loadDocData(doc)}>
            {doc.filename}
          </li>
        ))}
      </ul>

      {selectedDoc && (
        <div>
          <h2>Summary</h2>
          <p>{summary}</p>

          <h2>Flowchart</h2>
          {flowchart ? <pre>{flowchart}</pre> : <p>No flowchart available</p>}

          <h2>Ask a Question</h2>
          <QASection selectedDoc={selectedDoc} />
        </div>
      )}
    </div>
  );
}
