import React from "react";

export default function Loader({ text = "Loading..." }) {
  return (
    <div className="card loader" style={{ alignItems: "center" }}>
      <div className="spinner"></div>
      <div>{text}</div>
    </div>
  );
}
