const express = require('express');
const cors = require('cors');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const dotenv = require('dotenv');

// Initialize dotenv to load environment variables
dotenv.config();

// Create an Express app
const app = express();
const port = 3000;

// Mock database (replace with real DB in production)
const users = [
  {
    id: 1,
    username: 'john_doe',
    password: '$2a$10$N1Lz0xX2ZTgtsKp2t03/iM9km11qtmYgHih6/0nI/jTpYaE.mJAXm', // bcrypt hash of 'password123'
  },
];

// Enable CORS
app.use(cors({
  origin: 'http://localhost:9000', // Allow only this origin
}));

// Middleware to parse JSON request body
app.use(express.json());

// Function to generate JWT token
function generateToken(user) {
  return jwt.sign(
    { id: user.id, username: user.username },
    process.env.JWT_SECRET,
    { expiresIn: '1h' } // Token will expire in 1 hour
  );
}

// Middleware to authenticate JWT token
function authenticateToken(req, res, next) {
  const token = req.header('Authorization')?.replace('Bearer ', '');

  if (!token) {
    return res.status(401).json({ message: 'Access denied, token missing.' });
  }

  // Verify JWT token
  jwt.verify(token, process.env.JWT_SECRET, (err, user) => {
    if (err) {
      return res.status(403).json({ message: 'Invalid or expired token.' });
    }
    req.user = user;  // Attach the user to the request object
    next();  // Continue to the next middleware or route handler
  });
}

// Sample route: Public route (no authentication required)
app.get('/api/hello', (req, res) => {
  res.json({ message: 'Hello from the Node.js backend!' });
});

// Login route to authenticate users and issue JWT token
app.post('/api/login', async (req, res) => {
  const { username, password } = req.body;

  // Find user in the "database"
  const user = users.find(u => u.username === username);
  if (!user) {
    return res.status(401).json({ message: 'Invalid credentials.' });
  }

  // Compare the hashed password
  const isMatch = await bcrypt.compare(password, user.password);
  if (!isMatch) {
    return res.status(401).json({ message: 'Invalid credentials.' });
  }

  // Generate a JWT token
  const token = generateToken(user);

  // Return the token to the client
  res.json({ token });
});

// Protected route that requires authentication (using the JWT token)
app.get('/api/protected', authenticateToken, (req, res) => {
  res.json({ message: 'This is a protected route.', user: req.user });
});

// Start the server
app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});
