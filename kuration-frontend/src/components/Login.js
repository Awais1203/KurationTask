import React, { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import useAuthApi from "../hooks/useAuthApi";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faGoogle } from "@fortawesome/free-brands-svg-icons";
import { useNavigate } from "react-router-dom";
import "../Auth.css";

const Login = () => {
  const { login: contextLogin } = useAuth();
  const { login, googleLogin, completeGoogleLogin, loading, error, token } =
    useAuthApi();
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const handleLogin = async (e) => {
    e.preventDefault();
    const data = await login(username, password);
    if (data) {
      contextLogin(data);
      navigate("/dashboard");
    }
  };

  const handleGoogleLogin = async () => {
    await googleLogin();
  };

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get("code");

    if (code) {
      const fetchData = async () => {
        const data = await completeGoogleLogin(code);
        if (data) {
          contextLogin(data);
          navigate("/dashboard");
        }
      };
      fetchData();

      window.history.replaceState({}, document.title, window.location.pathname);
    }
  }, [navigate, completeGoogleLogin, contextLogin]);

  return (
    <div className="auth-container">
      <h2 className="auth-title">Login</h2>
      <form className="auth-form" onSubmit={handleLogin}>
        <input
          type="text"
          name="username"
          placeholder="Username"
          required
          className="form-control"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
        <input
          type="password"
          name="password"
          placeholder="Password"
          required
          className="form-control"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <button type="submit" className="btn btn-success" disabled={loading}>
          {loading ? "Logging in..." : "Login"}
        </button>
        <button
          type="button"
          className="btn btn-google"
          onClick={handleGoogleLogin}>
          <FontAwesomeIcon icon={faGoogle} /> Login with Google
        </button>
        {error && <p className="error-message">{error}</p>}
      </form>
      <div className="signup-redirect">
        <p>Don't have an account?</p>
        <button className="btn btn-link" onClick={() => navigate("/signup")}>
          Sign Up
        </button>
      </div>
    </div>
  );
};

export default Login;
