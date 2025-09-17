import { useState, useRef } from "react";
import { Box, TextField, IconButton, Button } from "@mui/material";
import SendIcon from "@mui/icons-material/Send";
import ImageIcon from "@mui/icons-material/Image";

export default function ChatInput({ onSend, onSendImage, onRetrieve }) {
  const [text, setText] = useState("");
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file && onSendImage) {
      onSendImage(file);
      // reset the input so the same file can be uploaded again if needed
      e.target.value = null;
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSend(text);
    setText("");
  };

  const handleRetrieveClick = () => {
    if (!onRetrieve) {
      return;
    }
    const trimmed = text.trim();
    if (!trimmed) {
      return;
    }
    onRetrieve(text);
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
      <input
        type="file"
        accept="image/*"
        ref={fileInputRef}
        style={{ display: "none" }}
        onChange={handleFileChange}
      />
      <IconButton
        color="primary"
        aria-label="upload image"
        onClick={() => fileInputRef.current?.click()}
      >
        <ImageIcon />
      </IconButton>
      <Button
        type="button"
        variant="contained"
        size="small"
        onClick={handleRetrieveClick}
        sx={{ ml: 1 }}
        disabled={!text.trim()}
      >
        Retrieve
      </Button>
      <IconButton type="submit" color="primary" aria-label="send">
        <SendIcon />
      </IconButton>
    </Box>
  );
}
