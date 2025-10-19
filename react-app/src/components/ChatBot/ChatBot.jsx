import { useState, useMemo, useCallback, useEffect } from "react";
import debounce from "lodash.debounce";
import { Box, Stack, Paper, List } from "@mui/material";
import ChatMessage from "./ChatMessage";
import ChatInput from "./ChatInput";

const getApiBaseUrl = () => {
  const runtimeConfig =
    typeof window !== "undefined" ? window.__APP_CONFIG__ : undefined;
  const runtimeUrl = runtimeConfig?.apiUrl;
  const envUrl = process.env.REACT_APP_API_URL;

  if (runtimeUrl && runtimeUrl.trim().length > 0) {
    return runtimeUrl;
  }

  if (envUrl && envUrl.trim().length > 0) {
    return envUrl;
  }

  if (process.env.NODE_ENV !== "production") {
    return "http://localhost:8000";
  }

  console.warn(
    "ChatBot API base URL is not configured. Set window.__APP_CONFIG__.apiUrl or REACT_APP_API_URL."
  );
  return "";
};

export default function ChatBot() {
  const [messages, setMessages] = useState([]);
  const apiBase = useMemo(getApiBaseUrl, []);

  const extractCompletionText = useCallback((payload) => {
    if (!payload) {
      return "";
    }

    const outputBlocks = Array.isArray(payload.output) ? payload.output : [];
    for (const block of outputBlocks) {
      const contents = Array.isArray(block?.content) ? block.content : [];
      for (const part of contents) {
        if (typeof part?.text === "string" && part.text.trim()) {
          return part.text;
        }
      }
    }

    const choices = Array.isArray(payload.choices) ? payload.choices : [];
    for (const choice of choices) {
      const content = choice?.message?.content;
      if (typeof content === "string" && content.trim()) {
        return content;
      }
    }

    if (typeof payload.message === "string" && payload.message.trim()) {
      return payload.message;
    }

    return "";
  }, []);

  const handleSend = useCallback(
    async (text) => {
      if (!text.trim()) {
        return;
      }

      const timestamp = Date.now();
      const userMessage = { id: timestamp, role: "user", text };
      setMessages((prev) => [...prev, userMessage]);

      try {
        const response = await fetch(`${apiBase}/api/openai`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ model: "gpt-4o-mini", input: text }),
        });
        const data = await response.json();
        if (!response.ok) {
          const detail =
            typeof data?.detail === "string"
              ? data.detail
              : response.statusText || "OpenAI request failed";
          throw new Error(detail);
        }

        const botText = extractCompletionText(data) || "No response";
        const botMessage = { id: timestamp + 1, role: "bot", text: botText };
        setMessages((prev) => [...prev, botMessage]);
      } catch (err) {
        const message = err instanceof Error ? err.message : "Unknown error";
        const botMessage = {
          id: timestamp + 1,
          role: "bot",
          text: `Error contacting server: ${message}`,
        };
        setMessages((prev) => [...prev, botMessage]);
      }
    },
    [apiBase, extractCompletionText]
  );

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

  const handleRetrieve = useCallback(
    async (text) => {
      if (!text.trim()) {
        return;
      }

      const timestamp = Date.now();
      const userMessage = { id: timestamp, role: "user", text };
      setMessages((prev) => [...prev, userMessage]);

      try {
        const response = await fetch(`${apiBase}/api/search/retrieve`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ query: text, k: 3 }),
        });

        let data;
        try {
          data = await response.json();
        } catch (parseError) {
          throw new Error(
            parseError instanceof Error
              ? `Failed to parse retrieval response: ${parseError.message}`
              : "Failed to parse retrieval response"
          );
        }

        if (!response.ok) {
          const detail =
            typeof data?.detail === "string"
              ? data.detail
              : Array.isArray(data?.detail)
              ? data.detail
                  .map((item) =>
                    typeof item === "string"
                      ? item
                      : typeof item?.msg === "string"
                      ? item.msg
                      : ""
                  )
                  .filter(Boolean)
                  .join(", ")
              : response.statusText || "Retrieval request failed";
          throw new Error(detail);
        }

        const answerText =
          extractCompletionText(data?.completion) ||
          (Array.isArray(data?.items) && data.items.length > 0
            ? `Retrieved ${data.items.length} result${data.items.length === 1 ? "" : "s"}.`
            : "No answer generated.");

        const citations = Array.isArray(data?.items)
          ? data.items.map((item) => ({
              id: item.id,
              url: item.url,
              score: item.score,
              ocrText: item.ocr_text,
              modalities: Array.isArray(item.modalities_used)
                ? item.modalities_used
                : [],
            }))
          : [];

        const botMessage = {
          id: timestamp + 1,
          role: "bot",
          text: answerText,
          citations,
        };
        setMessages((prev) => [...prev, botMessage]);
      } catch (err) {
        const message = err instanceof Error ? err.message : "Unknown error";
        const botMessage = {
          id: timestamp + 1,
          role: "bot",
          text: `Retrieval failed: ${message}`,
        };
        setMessages((prev) => [...prev, botMessage]);
      }
    },
    [apiBase, extractCompletionText]
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
        <ChatInput
          onSend={debouncedHandleSend}
          onSendImage={handleImageUpload}
          onRetrieve={handleRetrieve}
        />
      </Stack>
    </Box>
  );
}
