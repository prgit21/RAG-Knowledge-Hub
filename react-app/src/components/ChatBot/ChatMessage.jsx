import { ListItem, Box } from "@mui/material";

export default function ChatMessage({ message }) {
  const isUser = message.role === "user";
  const citations =
    !isUser && Array.isArray(message.citations) ? message.citations : [];

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
        {citations.length > 0 && (
          <Box sx={{ mt: 1 }}>
            <Box sx={{ fontSize: "0.75rem", fontWeight: 600 }}>Citations</Box>
            <Box
              component="ul"
              sx={{
                m: 0,
                pl: 2,
                fontSize: "0.75rem",
                listStyleType: "disc",
              }}
            >
              {citations.map((item, index) => {
                const formattedScore =
                  typeof item.score === "number" && !Number.isNaN(item.score)
                    ? item.score.toFixed(3)
                    : null;
                const modalities = Array.isArray(item.modalities)
                  ? item.modalities
                  : [];
                let snippet = null;
                if (typeof item.ocrText === "string" && item.ocrText.trim()) {
                  const trimmed = item.ocrText.trim();
                  snippet =
                    trimmed.length > 200 ? `${trimmed.slice(0, 200)}…` : trimmed;
                }

                return (
                  <Box
                    component="li"
                    key={`citation-${item.id}-${index}`}
                    sx={{ listStyleType: "disc", mb: 0.75 }}
                  >
                    <Box
                      component="a"
                      href={item.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      sx={{
                        color: "primary.main",
                        textDecoration: "none",
                        fontWeight: 500,
                        "&:hover": { textDecoration: "underline" },
                      }}
                    >
                      {`cite-${item.id}`}
                    </Box>
                    {formattedScore && (
                      <Box component="span" sx={{ color: "text.secondary", ml: 0.5 }}>
                        {`· score ${formattedScore}`}
                      </Box>
                    )}
                    {modalities.length > 0 && (
                      <Box component="span" sx={{ color: "text.secondary", ml: 0.5 }}>
                        {`· ${modalities.join(", ")}`}
                      </Box>
                    )}
                    {snippet && (
                      <Box component="div" sx={{ color: "text.secondary", mt: 0.25 }}>
                        {snippet}
                      </Box>
                    )}
                  </Box>
                );
              })}
            </Box>
          </Box>
        )}
      </Box>
    </ListItem>
  );
}

