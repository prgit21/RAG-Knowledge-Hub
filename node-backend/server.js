const express = require('express');
const cors = require('cors');
const app = express();
const port = 3000;

// Enable CORS for all routes
app.use(cors()); // This will allow all origins by default

// You can also enable CORS for a specific origin like:
app.use(cors({
  origin: 'http://localhost:9000' // Allow requests only from this origin
}));

// Sample route
app.get('/api/hello', (req, res) => {
  res.json({ message: 'Hello from the Node.js backend!' });
});

app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});
