import { useState } from "react";
import { Box, Stack, Paper, List } from "@mui/material";
import ChatMessage from "./ChatMessage";
import ChatInput from "./ChatInput";

export default function ChatBot() {
  const [messages, setMessages] = useState([]);

  const handleSend = async (text) => {
    if (!text.trim()) {
      return;
    }

    const userMessage = { id: Date.now(), role: "user", text };
    setMessages((prev) => [...prev, userMessage]);

    try {
      const response = await fetch("/api/openai", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ model: "gpt-4o-mini", input: text }),
      });
      const data = await response.json();
      const botText =
        data.output?.[0]?.content?.[0]?.text ||
        data.choices?.[0]?.message?.content ||
        "No response";
      const botMessage = { id: Date.now() + 1, role: "bot", text: botText };
      setMessages((prev) => [...prev, botMessage]);
    } catch (err) {
      const botMessage = {
        id: Date.now() + 1,
        role: "bot",
        text: "Error contacting server.",
      };
      setMessages((prev) => [...prev, botMessage]);
    }
  };

  return (
    <Box
      component={Paper}
      sx={{
        height: 400,
        border: 1,
        borderColor: "divider",
      }}
    >
      <Stack sx={{ height: "100%" }}>
        <List sx={{ flexGrow: 1, overflowY: "auto", p: 1 }}>
          {messages.map((msg) => (
            <ChatMessage key={msg.id} message={msg} />
          ))}
        </List>
        <ChatInput onSend={handleSend} />
      </Stack>
    </Box>
  );
}
