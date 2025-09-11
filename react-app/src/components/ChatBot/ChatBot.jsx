import { useState, useMemo, useCallback, useEffect } from "react";
import debounce from "lodash.debounce";
import { Box, Stack, Paper, List } from "@mui/material";
import ChatMessage from "./ChatMessage";
import ChatInput from "./ChatInput";

export default function ChatBot() {
  const [messages, setMessages] = useState([]);
  // const apiBase = process.env.REACT_APP_API_URL || "http://localhost:8000";
  const apiBase = "http://localhost:8000";

  const handleSend = useCallback(async (text) => {
    if (!text.trim()) {
      return;
    }

    const userMessage = { id: Date.now(), role: "user", text };
    setMessages((prev) => [...prev, userMessage]);

    try {
      const response = await fetch(`${apiBase}/api/openai`, {
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
        text: "Error contacting server.{}"+err.message,
      };
      setMessages((prev) => [...prev, botMessage]);
    }
  }, []);

  // Debounce to prevent rapid multiple API calls
  const debouncedHandleSend = useMemo(() => debounce(handleSend, 500), [handleSend]);

  const handleImageUpload = useCallback(
    async (file) => {
      const formData = new FormData();
      formData.append("file", file);
      const userMessage = {
        id: Date.now(),
        role: "user",
        text: `[Image: ${file.name}]`,
      };
      setMessages((prev) => [...prev, userMessage]);
      try {
        await fetch(`${apiBase}/api/upload-image`, {
          method: "POST",
          body: formData,
        });
      } catch (err) {
        const botMessage = {
          id: Date.now() + 1,
          role: "bot",
          text: "Image upload failed: " + err.message,
        };
        setMessages((prev) => [...prev, botMessage]);
      }
    },
    [apiBase]
  );

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      debouncedHandleSend.cancel();
    };
  }, [debouncedHandleSend]);

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
        <ChatInput onSend={debouncedHandleSend} onSendImage={handleImageUpload} />
      </Stack>
    </Box>
  );
}
