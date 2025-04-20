// src/AuthForm.js
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./AuthForm.css";

function AuthForm() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSignup = async (e) => {
    e.preventDefault();

    try {
      const response = await fetch("http://127.0.0.1:5000/signup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: email, password }),
      });

      const data = await response.json();

      if (response.ok) {
        alert("Signup successful! Please login.");
        navigate("/login");
      } else {
        alert(data.error || "Signup failed");
      }
    } catch (error) {
      alert("Error connecting to server");
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-box">
        <h2>Create an Account</h2>
        <form onSubmit={handleSignup}>
          <label>Email</label>
          <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />

          <label>Password</label>
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />

          <button type="submit">Sign Up</button>
        </form>
        <p>
          Already have an account? <span onClick={() => navigate("/login")} style={{ color: "blue", cursor: "pointer" }}>Login</span>
        </p>
      </div>
    </div>
  );
}

export default AuthForm;
