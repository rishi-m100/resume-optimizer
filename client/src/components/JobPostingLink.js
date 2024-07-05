import React, { useState, useRef, useEffect } from "react";
import "./JobPostingLink.css";

function JobPostingLink({ onScrapingStatus }) {
  const [link, setLink] = useState("");
  const [isScaping, setIsScraping] = useState(false);
  const [submittedLink, setSubmittedLink] = useState("");
  const [showPreview, setShowPreview] = useState(true);
  const iframeRef = useRef(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsScraping(true);
    setSubmittedLink(link);
    setShowPreview(true); // Reset preview visibility on new submission
    try {
      const response = await fetch("/scrape-job-posting", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ link }),
      });

      if (response.ok) {
        onScrapingStatus("Job posting scraped successfully");
      } else {
        onScrapingStatus("Failed to scrape job posting");
      }
    } catch (error) {
      onScrapingStatus("Error: " + error.message);
    } finally {
      setIsScraping(false);
      setLink("");
    }
  };

  const handleIframeError = () => {
    setShowPreview(false);
  };

  const handleIframeLoad = () => {
    try {
      const iframeDocument =
        iframeRef.current.contentDocument ||
        iframeRef.current.contentWindow.document;
      if (iframeDocument.body.innerText.includes("refused to connect")) {
        setShowPreview(false);
      }
    } catch (error) {
      // If we can't access the iframe content due to CORS, hide the preview
      setShowPreview(false);
    }
  };

  useEffect(() => {
    // Reset showPreview when submittedLink changes
    setShowPreview(true);
  }, [submittedLink]);

  return (
    <div className="job-posting-link">
      <h2>Scrape Job Posting</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={link}
          onChange={(e) => setLink(e.target.value)}
          placeholder="Enter job posting URL"
          required
        />
        <button type="submit" disabled={isScaping}>
          {isScaping ? "Scraping..." : "Scrape"}
        </button>
      </form>
      {isScaping && <div className="loading-spinner"></div>}
      {submittedLink && (
        <div className="submitted-link">
          <h3>Submitted Link:</h3>
          <a href={submittedLink} target="_blank" rel="noopener noreferrer">
            {submittedLink}
          </a>
        </div>
      )}
      {submittedLink && showPreview && (
        <div className="preview">
          <h3>Preview:</h3>
          <iframe
            ref={iframeRef}
            src={submittedLink}
            title="Job Posting Preview"
            width="100%"
            height="500px"
            sandbox="allow-scripts allow-same-origin"
            onError={handleIframeError}
            onLoad={handleIframeLoad}
          />
        </div>
      )}
    </div>
  );
}

export default JobPostingLink;
