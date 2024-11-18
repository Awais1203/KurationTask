import React from "react";
import { useNavigate } from "react-router-dom"; // Import useNavigate
import "../Auth.css"; // Import custom CSS

const Signup = () => {
  const navigate = useNavigate(); // Initialize useNavigate

  const handleSignup = async (e) => {
    e.preventDefault();
    const username = e.target.username.value;
    const email = e.target.email.value;
    const password = e.target.password.value;
    // Implement your signup logic here
  };

  const handleLoginRedirect = () => {
    navigate("/login"); // Navigate to login page
  };

  return (
    <div className="auth-container">
      <h2 className="auth-title">Sign Up</h2>
      <form className="auth-form" onSubmit={handleSignup}>
        <input
          type="text"
          name="username"
          placeholder="Username"
          required
          className="form-control"
        />
        <input
          type="email"
          name="email"
          placeholder="Email"
          required
          className="form-control"
        />
        <input
          type="password"
          name="password"
          placeholder="Password"
          required
          className="form-control"
        />
        <button type="submit" className="btn btn-success">
          Sign Up
        </button>
      </form>
      <div className="login-redirect">
        <p>Already have an account?</p>
        <button className="btn btn-link" onClick={handleLoginRedirect}>
          Login
        </button>
      </div>
    </div>
  );
};

export default Signup;
