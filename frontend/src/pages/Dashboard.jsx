import { useState, useEffect } from "react";
import FileUpload from "../components/FileUpload";
import DocumentList from "../components/DocumentList";
import SummaryViewer from "../components/SummaryView";
import QAViewer from "../components/QASection";
import Flowchart from "../components/FlowchartView";
import { getSummary, getFlowchart } from "../api/backend";

export default function Dashboard() {
  const [selectedDoc, setSelectedDoc] = useState(null);
  const [summary, setSummary] = useState("");
  const [flowchart, setFlowchart] = useState("");

  useEffect(() => {
    if (selectedDoc) {
      getSummary(selectedDoc.id).then((data) => setSummary(data.summary));
      getFlowchart(selectedDoc.id).then((data) => setFlowchart(data.chart));
    }
  }, [selectedDoc]);

  return (
    <div className="p-4 grid grid-cols-3 gap-4">
      <div>
        <FileUpload onUploadComplete={() => window.location.reload()} />
        <DocumentList onSelect={setSelectedDoc} />
      </div>
      <div>
        <SummaryViewer summary={summary} />
        {selectedDoc && <QAViewer docId={selectedDoc.id} />}
      </div>
      <div>
        <Flowchart chartDefinition={flowchart} />
      </div>
    </div>
  );
}
