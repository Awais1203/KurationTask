import React from "react";
import { useAuth } from '../context/AuthContext';
import LeadCaptureForm from "./LeadCaptureForm";

const Dashboard = () => {
  const { logout } = useAuth();

  const handleLogout = () => {
    logout();
    window.location.href = '/login';
  };

  return (
    <div>
      <h1>Dashboard</h1>
      <button onClick={handleLogout} className="btn btn-danger">Logout</button>
      <LeadCaptureForm />
    </div>
  );
};

export default Dashboard;
