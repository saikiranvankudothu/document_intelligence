import React, { useState } from "react";
import DocumentUpload from "../components/DocumentUpload";
import DocumentList from "../components/DocumentList";
import SummaryView from "../components/SummaryView";
import QASection from "../components/QASection";
import FlowchartView from "../components/FlowchartView";
import Loader from "../components/Loader";

export default function App() {
  const [selectedDoc, setSelectedDoc] = useState(null); // { id, filename }
  const [processing, setProcessing] = useState(false);
  const [reloadDocs, setReloadDocs] = useState(0); // triggers document list refresh

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>Document Intelligence</h1>
      </header>

      <div className="layout">
        <aside className="left-col">
          <DocumentUpload
            onUploadComplete={(doc) => {
              setReloadDocs((r) => r + 1); // refresh document list
              if (doc?.doc_id) {
                setSelectedDoc({ id: doc.doc_id, filename: doc.filename });
              }
            }}
            setProcessing={setProcessing}
          />
          <hr />
          <DocumentList
            onSelect={(doc) => setSelectedDoc(doc)}
            selected={selectedDoc}
            reloadTrigger={reloadDocs}
          />
        </aside>

        <main className="main-col">
          {processing && <Loader text="Processing document..." />}
          {!processing && !selectedDoc && (
            <p>Select or upload a document to begin.</p>
          )}

          {!processing && selectedDoc && (
            <>
              <h2>{selectedDoc.filename}</h2>
              <div className="grid">
                <div className="card">
                  <SummaryView docId={selectedDoc.id} />
                </div>
                <div className="card">
                  <QASection selectedDoc={selectedDoc} />
                </div>
                <div className="card flowchart-card">
                  <FlowchartView docId={selectedDoc.id} />
                </div>
              </div>
            </>
          )}
        </main>
      </div>
    </div>
  );
}
