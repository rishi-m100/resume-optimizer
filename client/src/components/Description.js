// Description.js
import React from "react";
import "./Description.css";

function Description() {
  return (
    <div className="description-container">
      {/* <h2>Resume Optimizer</h2> */}
      <p>
        Welcome to the Resume Optimizer! This app helps you create a tailored
        resume for specific job postings by combining the best elements from
        multiple versions of your resume.
      </p>
      <h3>How it works:</h3>
      <ol>
        <li>Upload up to 5 different versions of your resume (PDF format).</li>
        <li>Provide a link to the job posting you're interested in.</li>
        <li>
          Our AI-powered system analyzes your resumes and the job posting.
        </li>
        <li>
          We generate an optimized resume that highlights your most relevant
          skills and experiences for the specific job.
        </li>
      </ol>
      <p>
        By using multiple resume versions, we can select the most impactful
        content for each section, ensuring your application stands out to
        potential employers.
      </p>
      <div className="benefits">
        <h3>Benefits:</h3>
        <ul>
          <li>
            Save time by avoiding manual resume tailoring for each application
          </li>
          <li>
            Improve your chances of passing Applicant Tracking Systems (ATS)
          </li>
          <li>
            Highlight your most relevant skills and experiences for each job
          </li>
          <li>Increase your interview chances with optimized content</li>
        </ul>
      </div>
    </div>
  );
}

export default Description;
