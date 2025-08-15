import React, { useEffect, useRef, useState } from "react";
import mermaid from "mermaid";
import { getFlowchart } from "../api/visualizationApi";
import Loader from "./Loader";

export default function FlowchartView({ docId }) {
  const containerRef = useRef();
  const [loading, setLoading] = useState(false);
  const [mermaidCode, setMermaidCode] = useState("");

  useEffect(() => {
    mermaid.initialize({ startOnLoad: false });
  }, []);

  useEffect(() => {
    if (!docId) return;
    setLoading(true);
    getFlowchart(docId)
      .then((res) => {
        const code = res.mermaid || res.mermaid_code || res.chart || "";
        setMermaidCode(code);
      })
      .catch((e) => {
        console.error(e);
      })
      .finally(() => setLoading(false));
  }, [docId]);

  useEffect(() => {
    if (!mermaidCode) {
      containerRef.current.innerHTML =
        "<div class='small-muted'>No flowchart available</div>";
      return;
    }
    mermaid
      .render("mermaidGraph", mermaidCode)
      .then(({ svg }) => {
        containerRef.current.innerHTML = svg;
      })
      .catch((e) => {
        containerRef.current.innerHTML = `<pre style="white-space:pre-wrap">${mermaidCode}</pre>`;
        console.error("Mermaid render failed:", e);
      });
  }, [mermaidCode]);

  if (loading) return <Loader text="Loading flowchart..." />;

  return (
    <div>
      <h3>Flowchart</h3>
      <div ref={containerRef} style={{ minHeight: 200 }} />
    </div>
  );
}
