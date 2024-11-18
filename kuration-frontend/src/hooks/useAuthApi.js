import { useState } from "react";
import config from "../config";

const useAuthApi = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [token, setToken] = useState(null);

  const login = async (username, password) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${config.BASE_URL}/token`, {
        method: "POST",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: new URLSearchParams({
          grant_type: "",
          username,
          password,
          scope: "",
          client_id: "",
          client_secret: "",
        }),
      });

      if (!response.ok) {
        throw new Error("Login failed");
      }

      const data = await response.json();
      setToken(data.access_token); // Save the token
      return data; // Return the response data
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const googleLogin = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${config.BASE_URL}/auth/google`, {
        method: "GET",
        headers: {
          Accept: "application/json",
        },
      });

      if (!response.ok) {
        throw new Error("Google login failed");
      }

      const data = await response.json();
      // Redirect to the URL returned from the API
      window.location.href = data.url; // Redirect to Google login
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const completeGoogleLogin = async (code) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(
        `${config.BASE_URL}/auth/google/callback?code=${code}`,
        {
          method: "GET",
          headers: {
            Accept: "application/json",
          },
        }
      );

      if (!response.ok) {
        throw new Error("Google callback failed");
      }

      const data = await response.json();
      setToken(data.access_token); // Save the token
      return data; // Return the response data
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return {
    login,
    googleLogin,
    completeGoogleLogin,
    loading,
    error,
    token,
  };
};

export default useAuthApi;
