import { useState } from "react";
import Button from "@mui/material/Button";

export default function ChatInput({ onSend }) {
  const [text, setText] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    onSend(text);
    setText("");
  };

  return (
    <form className="chatbot-input" onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="Type your message"
        value={text}
        onChange={(e) => setText(e.target.value)}
      />
      <Button type="submit" variant="contained">
        Send
      </Button>
    </form>
  );
}
