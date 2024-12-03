const express = require("express");
const cors = require("cors");
const jwt = require("jsonwebtoken");
const argon2 = require("argon2");
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

/// TODO create prod db
const users = [
  {
    id: 1,
    username: "testuser",
    password: "",
  },
  {
    id: 1,
    username: "some-user",
    password: "",
  },
];
//method to hash pwd into DB
async function hashPassword(password) {
  try {
    const hashedpwd = await argon2.hash(password);
    return hashedpwd;
  } catch (err) {
    console.error("Error hashing password:", err);
    throw err;
  }
}
(async () => {
  users[0].password = await hashPassword("pwd123"); //hardcoded for now cus only one user, will replace when signup feature is added
  users[1].password = await hashPassword("somepwd");
})();

app.post("/api/login", async (req, res) => {
  const { username, password } = req.body;
  const matchedUser = users.find((user) => user.username === username);

  if (!matchedUser) {
    return res.status(401).json({ message: "Invalid credentials" });
  }

  const isPasswordValid = await argon2.verify(matchedUser.password, password);

  if (!isPasswordValid) {
    return res.status(401).json({ message: "Invalid credentials" });
  }
  const token = jwt.sign(
    { id: matchedUser.id, username: matchedUser.username },
    process.env.JWT_SECRET,
    { expiresIn: "1h" }
  );

  res.json({ message: "Login successful", token });
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
app.get("/api/protected", verifyToken, (req, res) => {
  res.json({ message: "This is protected data", user: req.user });
});

app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});
