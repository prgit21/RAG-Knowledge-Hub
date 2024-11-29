const express = require("express");
const cors = require("cors");
const jwt = require("jsonwebtoken");
// const argon2 = require("argon2");
const dotenv = require("dotenv");

const app = express();
const port = 3000;
dotenv.config();

// Enable CORS
app.use(
  cors({
    origin: "http://localhost:9000",
  })
);

app.use(express.json());

app.get("/api/hello", (req, res) => {
  res.json({ message: "Hello from the Node.js backend!" });
});
app.post("/api/login", async (req, res) => {
  // TODO Mock database, create actual DB
  const users = [
    {
      id: 1,
      username: "user",
      pwd: "", // bcrypt hash for "pwd123"
    },

    {
      id: 4,
      username: "guest",
      pwd: "$2b$10$k3Zpt8Qgz6OKyC.DdPJG5C7GT9i/mbESM8P2zmd7mX1aF8r7vUwCa", // bcrypt hash for "guest123"
    },
  ];

  const { username, password } = req.body;
  const matchedUser = users.find((user) => user.username === username);

  if (!matchedUser) {
    return res.status(401).json({ message: "Invalid credentials" });
  }

  /// implement argon2  here
  // 1. Hash argon 2 pwd and store in mockDB,
  // argon2 implementation
  // Verify the password
  // async function verifyPassword(storedHash, inputPassword) {
  //   try {
  //     const isMatch = await argon2.verify(storedHash, inputPassword);
  //     return isMatch; // true or false
  //   } catch (err) {
  //     console.error('Error verifying password:', err);
  //     throw err;
  //   }
  // }

  // // Example usage
  // const inputPassword = "userEnteredPassword";
  // const storedHash = "<the-hashed-password-from-database>";

  // const isMatch = await verifyPassword(storedHash, inputPassword);

  // if (isMatch) {
  //   console.log('Login successful');
  // } else {
  //   console.log('Incorrect password');
  // }
});

const verifyToken = (req, res, next) => {
  const token = req.header("Authorization")?.replace("Bearer ", "");

  if (!token) {
    return res.status(403).json({ message: "Access denied, token missing" });
  }

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    req.user = decoded;
    next();
  } catch (error) {
    return res.status(401).json({ message: "Invalid or expired token" });
  }
};
app.get("/protected", verifyToken, (req, res) => {
  res.json({ message: "This is protected data", user: req.user });
});

app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});
