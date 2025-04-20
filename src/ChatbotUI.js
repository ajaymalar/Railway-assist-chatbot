import React, { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import jsPDF from "jspdf";
import "./ChatbotUI.css";

function ChatbotUI() {
  const navigate = useNavigate();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const chatEndRef = useRef(null);
  const [darkMode, setDarkMode] = useState(localStorage.getItem("darkMode") === "true");
  const [chatHistory, setChatHistory] = useState(() => {
    return JSON.parse(localStorage.getItem("chatHistory")) || [];
  });
  const [selectedChat, setSelectedChat] = useState(null);
// ✅ Redirect to login if token is missing
useEffect(() => {
  const token = localStorage.getItem("token");
  if (!token) {
    alert("Please login to access the chatbot.");
    navigate("/login");
  }
}, [navigate]);

  // Save dark mode preference
  useEffect(() => {
    localStorage.setItem("darkMode", darkMode);
  }, [darkMode]);

  // Save chat history
  useEffect(() => {
    localStorage.setItem("chatHistory", JSON.stringify(chatHistory));
  }, [chatHistory]);

  // Scroll to the latest message
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Send message to backend
  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;
  
    const newUserMessage = { text: input, user: "You" };
    setMessages((prev) => [...prev, newUserMessage]);
    setInput("");
  
    try {
      const token = localStorage.getItem("token");
  
      const res = await axios.post("http://127.0.0.1:5000/chat",
        { message: input },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
  
      if (res.status === 200 && res.data.response) {
        const newBotMessage = { text: res.data.response, user: "Bot" };
        setMessages((prev) => {
          const updatedMessages = [...prev, newBotMessage];
          setChatHistory((history) => {
            const newHistory = [...history];
            if (selectedChat !== null) {
              newHistory[selectedChat] = updatedMessages;
            } else {
              newHistory.push(updatedMessages);
              setSelectedChat(newHistory.length - 1);
            }
            return newHistory;
          });
  
          return updatedMessages;
        });
      } else {
        throw new Error("Invalid response from backend");
      }
    } catch (error) {
      console.error("Error connecting to backend:", error);
      setMessages((prev) => [
        ...prev,
        { text: "Error: Could not connect to backend", user: "Bot" },
      ]);
    }
  };
  
  // Start new chat
  const startNewChat = () => {
    if (messages.length > 0) {
      setChatHistory((prev) => [...prev, messages]);
    }
    setMessages([]);
    setSelectedChat(null);
  };

  // Load previous chat
  const loadChatHistory = (index) => {
    setMessages([...chatHistory[index]]);
setSelectedChat(index);

  };

  // Voice input handling
  const startVoiceRecognition = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      const audioChunks = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunks.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
        const formData = new FormData();
        formData.append("file", audioBlob, "audio.webm");

        try {
          const response = await axios.post("http://127.0.0.1:5000/transcribe", formData, {
            headers: { "Content-Type": "multipart/form-data" },
          });

          if (response.data.text) {
            setInput(response.data.text);
          }
        } catch (error) {
          console.error("Transcription Error:", error);
        }
      };

      mediaRecorder.start();
      setTimeout(() => {
        mediaRecorder.stop();
        stream.getTracks().forEach((track) => track.stop());
      }, 5000);
    } catch (error) {
      console.error("Error capturing audio:", error);
    }
  };

  // Logout function
  const handleLogout = () => {
    localStorage.removeItem("token"); // ✅ Clear token
    navigate("/login");              // ✅ Redirect to login
  };
  

  // Export chat history to PDF
  const exportPDF = () => {
    const doc = new jsPDF();
    doc.setFont("helvetica", "normal");
    doc.text("Chat History", 10, 10);
    let yPosition = 20;

    messages.forEach((msg, index) => {
      if (yPosition > 280) {
        doc.addPage();
        yPosition = 20;
      }
      const timestamp = new Date().toLocaleTimeString();
      doc.text(`${index + 1}. [${timestamp}] ${msg.user}: ${msg.text}`, 10, yPosition);
      yPosition += 10;
    });

    doc.save(`Chat_History_${new Date().toISOString().slice(0, 10)}.pdf`);
  };

  return (
    <div className={`chat-container ${darkMode ? "dark" : ""}`}>
      <div className="sidebar">
        <h2>ChatBot</h2>
        <button onClick={startNewChat}>New Chat</button>
        <h3>Chat History</h3>
        <ul>
          {chatHistory.map((_, index) => (
            <li
              key={index}
              onClick={() => loadChatHistory(index)}
              className={selectedChat === index ? "active" : ""}
            >
              Chat {index + 1}
            </li>
          ))}
        </ul>
      </div>

      <div className="chat-content">
        <div className="chat-header">
          <button onClick={() => navigate("/signup")}>Signup</button>
          <button onClick={() => navigate("/login")}>Login</button>
          <button className="logout-btn" onClick={handleLogout}>Logout</button>
        </div>

        <div className="chat-messages">
          {messages.map((msg, index) => (
            <div key={index} className={`message ${msg.user === "You" ? "user" : "bot"}`}>
              <strong>{msg.user}: </strong> {msg.text}
            </div>
          ))}
          <div ref={chatEndRef} />
        </div>

        <div className="chat-footer">
          <button className="toggle-mode" onClick={() => setDarkMode(!darkMode)}>
            {darkMode ? "🌙 Dark Mode" : "☀️ Light Mode"}
          </button>
          <button className="download-btn" onClick={exportPDF}>Download PDF</button>

          <form onSubmit={handleSendMessage} className="chat-input">
          <textarea
  placeholder="Type a message or use voice..."
  value={input}
  onChange={(e) => setInput(e.target.value)}
  rows={1}
  style={{ resize: "none", overflowY: "auto", minHeight: "40px", maxHeight: "150px" }}
/>

            <button type="button" onClick={startVoiceRecognition}>🎤</button>
            <button type="submit">Send</button>
          </form>
        </div>
      </div>
    </div>
  );
}

export default ChatbotUI;
