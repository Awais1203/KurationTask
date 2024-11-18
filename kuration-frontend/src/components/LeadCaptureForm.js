import React, { useState } from "react";
import useLeadEnrichment from '../hooks/useLeadEnrichment'; // Import the custom hook
import "./LeadCaptureForm.css"; // Optional: Create a CSS file for styling

const LeadCaptureForm = () => {
  const [companyName, setCompanyName] = useState("");
  const [websiteUrl, setWebsiteUrl] = useState("");
  const { enrichLead, loading, error, enrichedData } = useLeadEnrichment(); // Use the custom hook

  const handleSubmit = async (e) => {
    e.preventDefault();
    await enrichLead(companyName, websiteUrl); // Call the enrichLead function from the hook
  };

  return (
    <div className="lead-capture-form">
      <h2>Lead Capture Form</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="companyName">Company Name:</label>
          <input
            type="text"
            id="companyName"
            value={companyName}
            onChange={(e) => setCompanyName(e.target.value)}
            required
          />
        </div>
        <div>
          <label htmlFor="websiteUrl">Website URL:</label>
          <input
            type="url"
            id="websiteUrl"
            value={websiteUrl}
            onChange={(e) => setWebsiteUrl(e.target.value)}
            required
          />
        </div>
        <button type="submit" disabled={loading}>
          {loading ? "Enriching..." : "Enrich Lead"}
        </button>
      </form>

      {loading && <p>Loading...</p>}
      {error && <p className="error-message">{error}</p>}
      {enrichedData && (
        <div className="enriched-data">
          <h3>Enriched Data:</h3>
          <table>
            <thead>
              <tr>
                <th>Company Name</th>
                <th>Website URL</th>
                <th>Description</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>{enrichedData.company_name}</td>
                <td><a href={enrichedData.website_url} target="_blank" rel="noopener noreferrer">{enrichedData.website_url}</a></td>
                <td>{enrichedData.description}</td>
              </tr>
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default LeadCaptureForm;
