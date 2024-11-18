import { useState } from "react";

const useLeadEnrichment = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [enrichedData, setEnrichedData] = useState(null);

  const enrichLead = async (companyName, websiteUrl) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch("http://localhost:8000/users/api/enrich", {
        // Update with your FastAPI URL
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          company_name: companyName,
          website_url: websiteUrl,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to enrich lead data");
      }

      const data = await response.json();
      setEnrichedData(data); // Set the enriched data
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return { enrichLead, loading, error, enrichedData };
};

export default useLeadEnrichment;
