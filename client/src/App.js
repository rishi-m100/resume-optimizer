import React, { useState } from "react";
import "./App.css";
import FileUpload from "./components/FileUpload";
import JobPostingLink from "./components/JobPostingLink";
import GenerateResume from "./components/GenerateResume";
import Description from "./components/Description";

function App() {
  const [uploadStatus, setUploadStatus] = useState("");
  const [scrapingStatus, setScrapingStatus] = useState("");

  const handleUploadStatus = (status) => {
    setUploadStatus(status);
  };

  const handleScrapingStatus = (status) => {
    setScrapingStatus(status);
  };

  return (
    <div className="App">
      <h1>Resume Optimizer</h1>
      <br></br>
      <FileUpload onUploadStatus={handleUploadStatus} />
      {uploadStatus && <p className="status-message">{uploadStatus}</p>}
      <JobPostingLink onScrapingStatus={handleScrapingStatus} />
      {scrapingStatus && <p className="status-message">{scrapingStatus}</p>}
      <GenerateResume />
      <Description />
    </div>
  );
}

export default App;
