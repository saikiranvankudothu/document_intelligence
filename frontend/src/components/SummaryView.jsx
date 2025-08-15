import React, { useEffect, useState } from "react";
import { getSummary } from "../api/summarizationApi";
import Loader from "./Loader";

export default function SummaryView({ docId }) {
  const [summary, setSummary] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!docId) return;
    setLoading(true);
    getSummary(docId)
      .then((res) => {
        // expecting { summary: "..." } or plain string
        setSummary(res.summary || res);
      })
      .catch((e) => {
        console.error(e);
        setSummary("Failed to load summary.");
      })
      .finally(() => setLoading(false));
  }, [docId]);

  if (loading) return <Loader text="Fetching summary..." />;

  return (
    <div>
      <h3>Summary</h3>
      <div>
        {summary || <span className="small-muted">No summary available</span>}
      </div>
    </div>
  );
}
