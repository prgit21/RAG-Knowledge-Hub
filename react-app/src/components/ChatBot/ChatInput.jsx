import { useState } from "react";
import { Box, TextField, IconButton } from "@mui/material";
import SendIcon from "@mui/icons-material/Send";

export default function ChatInput({ onSend }) {
  const [text, setText] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    onSend(text);
    setText("");
  };

  return (
    <Box
      component="form"
      onSubmit={handleSubmit}
      sx={{ display: "flex", borderTop: 1, borderColor: "divider", p: 1 }}
    >
      <TextField
        placeholder="Type your message"
        value={text}
        onChange={(e) => setText(e.target.value)}
        fullWidth
      />
      <IconButton type="submit" color="primary" aria-label="send">
        <SendIcon />
      </IconButton>
    </Box>
  );
}
