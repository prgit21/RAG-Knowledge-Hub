import { useState } from "react";
import { Box, Stack, Paper, List } from "@mui/material";
import ChatMessage from "./ChatMessage";
import ChatInput from "./ChatInput";

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
    setMessages((prev) => [...prev, userMessage, botMessage]);
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
