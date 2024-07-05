import React, { useState, useRef } from "react";
import "./FileUpload.css";

function FileUpload({ onUploadStatus }) {
  const [files, setFiles] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    const newFiles = Array.from(e.target.files);
    setFiles((prevFiles) => {
      const updatedFiles = [...prevFiles, ...newFiles];
      return updatedFiles.slice(0, 5); // Limit to 5 files
    });
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const newFiles = Array.from(e.dataTransfer.files).filter(
      (file) => file.type === "application/pdf"
    );
    setFiles((prevFiles) => {
      const updatedFiles = [...prevFiles, ...newFiles];
      return updatedFiles.slice(0, 5); // Limit to 5 files
    });
  };

  const handleRemoveFile = (index) => {
    setFiles((prevFiles) => prevFiles.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (files.length === 0) {
      onUploadStatus("Please select at least one file");
      return;
    }

    if (files.length > 5) {
      onUploadStatus("Maximum 5 files allowed");
      return;
    }

    setIsUploading(true);
    const formData = new FormData();
    files.forEach((file, index) => {
      formData.append(`file${index}`, file);
    });

    try {
      const response = await fetch("/upload", {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        const result = await response.json();
        onUploadStatus(
          `${result.message}: ${result.processed_files} files processed`
        );
        setFiles([]); // Clear the files after successful upload
      } else {
        const errorData = await response.json();
        onUploadStatus(errorData.error || "File upload failed");
      }
    } catch (error) {
      onUploadStatus("Error uploading files");
      console.error("Error:", error);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="file-upload-container">
      <form onSubmit={handleSubmit} className="file-upload-form">
        <div
          className="drop-zone"
          onDragOver={handleDragOver}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current.click()}
        >
          <p>Drag & drop PDF files here or click to select (Max 5 files)</p>
          <input
            type="file"
            ref={fileInputRef}
            accept=".pdf"
            onChange={handleFileChange}
            multiple
            style={{ display: "none" }}
          />
        </div>
        {files.length > 0 && (
          <div className="file-list">
            {files.map((file, index) => (
              <div key={index} className="file-item">
                <span>{file.name}</span>
                <button type="button" onClick={() => handleRemoveFile(index)}>
                  Remove
                </button>
              </div>
            ))}
          </div>
        )}
        <button type="submit" disabled={files.length === 0 || isUploading}>
          {isUploading ? "Uploading..." : "Upload PDFs"}
        </button>
      </form>
      <center> {isUploading && <div className="loading-spinner"></div>}</center>
    </div>
  );
}

export default FileUpload;
