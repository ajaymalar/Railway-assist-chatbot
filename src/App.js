import React, { useState } from "react";
import { Routes, Route } from "react-router-dom";
import AuthForm from "./AuthForm";
import Login from "./Login";
import ChatbotUI from "./ChatbotUI";
import axios from "axios";

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { text: input, sender: "user" };
    setMessages((prevMessages) => [...prevMessages, userMessage]);

    try {
      console.log("Sending message to backend...");

      const response = await axios.post("http://127.0.0.1:5000/chat", { message: input });

      console.log("Response from backend:", response); // Debugging backend response

      const botMessage = { text: response.data.response, sender: "bot" };
      setMessages((prevMessages) => [...prevMessages, botMessage]);
    } catch (error) {
      console.error("Error:", error);

      // Display error message for better UX
      let errorMessage = "Bot is not responding. Please try again later.";
      if (error.response) {
        errorMessage = error.response.data.error || errorMessage;
      } else if (error.request) {
        errorMessage = "No response from server. Please check backend.";
      }

      const botError = { text: errorMessage, sender: "bot" };
      setMessages((prevMessages) => [...prevMessages, botError]);
    }

    setInput("");
  };

  return (
    <>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/signup" element={<AuthForm />} />
        <Route path="/login" element={<Login />} />
        <Route path="/chat" element={<ChatbotUI />} />
        <Route path="*" element={<h1>404 - Page Not Found</h1>} />
      </Routes>

      <div>
        <h1>Chatbot</h1>
        <div className="chatbox">
          {messages.map((msg, index) => (
            <p key={index} className={msg.sender}>
              {msg.text}
            </p>
          ))}
        </div>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type a message..."
        />
        <button onClick={sendMessage}>Send</button>
      </div>
    </>
  );
}

export default App;
