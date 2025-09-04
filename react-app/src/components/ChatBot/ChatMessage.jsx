import { ListItem, Box } from "@mui/material";

export default function ChatMessage({ message }) {
  const isUser = message.role === "user";

  return (
    <ListItem
      disableGutters
      sx={{ justifyContent: isUser ? "flex-end" : "flex-start", mb: 1 }}
    >
      <Box
        sx={{
          bgcolor: isUser ? "#e0f7fa" : "#eeeeee",
          p: "6px 10px",
          borderRadius: 1,
        }}
      >
        {message.text}
      </Box>
    </ListItem>
  );
}

