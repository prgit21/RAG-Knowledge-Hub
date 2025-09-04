import { useState } from "react";
import ChatMessage from "./ChatMessage";
import ChatInput from "./ChatInput";
import "./ChatBot.css";

export default function ChatBot() {
  const [messages, setMessages] = useState([]);

  const handleSend = (text) => {
    if (!text.trim()) {
      return;
    }
    const userMessage = { id: Date.now(), role: "user", text };
    const botMessage = {
      id: Date.now() + 1,
      role: "bot",
      text: "This is a not a demo response.",
    };
    debugger
    setMessages((prev) => [...prev, userMessage, botMessage]);
  };

  return (
    <div className="chatbot-container">
      <div className="chatbot-messages">
        {messages.map((msg) => (
          <ChatMessage key={msg.id} message={msg} />
        ))}
      </div>
      <ChatInput onSend={handleSend} />
    </div>
  );
}
