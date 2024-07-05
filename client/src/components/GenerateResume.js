import React, { useState } from "react";
import axios from "axios";
import "./GenerateResume.css"; // Make sure to create this CSS file

function GenerateResume() {
  const [status, setStatus] = useState("");
  const [pdfUrl, setPdfUrl] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);

  const handleGenerateResume = async () => {
    setIsGenerating(true);
    setStatus("Processing...");
    try {
      // Run model.py
      const modelResponse = await axios.post("/api/run-model");
      console.log("Model response:", modelResponse.data);
      setStatus("Optimizing with Machine Learning...");

      // Run reconstruct.py
      const reconstructResponse = await axios.post("/api/run-reconstruct");
      console.log("Reconstruct response:", reconstructResponse.data);
      setStatus("Generating Resume...");

      // Generate resume
      const generateResponse = await axios.post("/api/generate-resume");
      console.log("Generate resume response:", generateResponse.data);

      // Set PDF URL and status
      setPdfUrl(generateResponse.data.pdfUrl);
      setStatus("Resume generated successfully!");
    } catch (error) {
      console.error("Error during resume generation:", error);
      setStatus("Error: " + (error.response?.data?.error || error.message));
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="generate-resume">
      <h2>Generate Optimized Resume</h2>
      <button
        className="generate-resume-button"
        onClick={handleGenerateResume}
        disabled={isGenerating}
      >
        {isGenerating ? "Generating..." : "Generate Optimized Resume"}
      </button>
      {status && <p className="status">{status}</p>}
      {pdfUrl && (
        <div>
          <a href={pdfUrl} download className="download-link">
            Download PDF
          </a>
        </div>
      )}
    </div>
  );
}

export default GenerateResume;
