const express = require('express');
const multer = require('multer');
const bcrypt = require('bcryptjs');
const fs = require('fs');
const app = express();
const port = 3000;

// Middleware to parse JSON bodies
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Simulate a file database (in-memory)
let fileData = {};

// Configure multer for file uploads
const storage = multer.memoryStorage();
const upload = multer({ storage: storage });

// File Upload Endpoint
app.post('/upload', upload.single('file'), async (req, res) => {
    const { password } = req.body;
    const hashedPassword = await bcrypt.hash(password, 10); // Hash the password

    // Store file data along with its password hash
    fileData[req.file.originalname] = {
        file: req.file.buffer,
        passwordHash: hashedPassword
    };

    res.json({ message: "File uploaded successfully" });
});

// File List Endpoint (for listing uploaded files)
app.get('/list-files', (req, res) => {
    const files = Object.keys(fileData); // Get filenames from the simulated database
    res.json({ files });
});

// File Download Endpoint with Password Validation
app.post('/download/:filename', async (req, res) => {
    const { filename } = req.params;
    const { password } = req.body;

    const fileRecord = fileData[filename];
    if (!fileRecord) {
        return res.status(404).json({ error: "File not found" });
    }

    // Check if the provided password matches the stored hashed password
    const isPasswordValid = await bcrypt.compare(password, fileRecord.passwordHash);
    if (!isPasswordValid) {
        return res.status(403).json({ error: "Invalid password" });
    }

    // If password is valid, send the file
    res.send(fileRecord.file);
});

// Start the server
app.listen(port, () => {
    console.log(`Server running on http://localhost:${port}`);
});
