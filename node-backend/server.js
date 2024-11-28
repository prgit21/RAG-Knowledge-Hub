const express = require("express");
const cors = require("cors");
const jwt = require("jsonwebtoken");
const bcrypt = require("bcryptjs");
const dotenv = require("dotenv");
const app = express();
const port = 3000;
dotenv.config();

/// TODO Mock database , create actual DB
const users = [
  {
    id: 1,
    username: "user",
    password: "$2a$10$N1Lz0xX2ZTgtsKp2t03/iM9km11qtmYgHih6/0nI/jTpYaE.mJAXm", // bcrypt hash of 'password123'
  },
];

// Enable CORS
app.use(
  cors({
    origin: "http://localhost:9000",
  })
);

// Middleware to parse JSON request body
app.use(express.json());

function generateToken(user) {
  return jwt.sign(
    { id: user.id, username: user.username },
    process.env.JWT_SECRET,
    { expiresIn: "1h" }
  );
}

// Middleware to authenticate JWT token
function authenticateToken(req, res, next) {
  const token = req.header("Authorization")?.replace("Bearer ", "");

  if (!token) {
    return res.status(401).json({ message: "Access denied, token missing." });
  }

  jwt.verify(token, process.env.JWT_SECRET, (err, user) => {
    if (err) {
      return res.status(403).json({ message: "Invalid or expired token." });
    }
    req.user = user;
    next();
  });
}

app.get("/api/hello", (req, res) => {
  res.json({ message: "Hello from the Node.js backend!" });
});

// Login route to authenticate users and issue JWT token
app.post("/api/login", async (req, res) => {
  const { username, password } = req.body;

  const user = users.find((u) => u.username === username); //parse user
  if (!user) {
    return res.status(401).json({ message: "Invalid credentials." });
  }

  const isMatch = await bcrypt.compare(password, user.password);
  if (!isMatch) {
    return res.status(401).json({ message: "Invalid credentials." });
  }

  const token = generateToken(user);

  res.json({ token });
});

// Protected route that requires authentication (using the JWT token)
app.get("/api/protected", authenticateToken, (req, res) => {
  res.json({ message: "This is a protected route.", user: req.user });
});

app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});
