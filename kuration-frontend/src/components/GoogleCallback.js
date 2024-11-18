import React, { useEffect } from "react";
import useAuthApi from "../hooks/useAuthApi";
import { useNavigate } from "react-router-dom";

const GoogleCallback = () => {
  const { completeGoogleLogin } = useAuthApi();
  const navigate = useNavigate();

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get("code");
    console.log("Code from URL:", code);

    if (code) {
      const fetchData = async () => {
        const data = await completeGoogleLogin(code);
        console.log("Data from completeGoogleLogin:", data);
        if (data) {
          navigate("/dashboard");
        } else {
          console.error("Failed to complete Google login");
        }
      };
      fetchData();
    } else {
      console.error("No code found in the URL");
      navigate("/login");
    }
  }, [navigate, completeGoogleLogin]);

  return <div>Loading...</div>; // Show a loading state while processing
};

export default GoogleCallback;
