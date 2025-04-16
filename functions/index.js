/**
 * Import function triggers from their respective submodules:
 *
 * const {onCall} = require("firebase-functions/v2/https");
 * const {onDocumentWritten} = require("firebase-functions/v2/firestore");
 *
 * See a full list of supported triggers at https://firebase.google.com/docs/functions
 */

const functions = require('firebase-functions');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

// Create and deploy your first functions
// https://firebase.google.com/docs/functions/get-started

// exports.helloWorld = onRequest((request, response) => {
//   logger.info("Hello logs!", {structuredData: true});
//   response.send("Hello from Firebase!");
// });

// Create a temporary file to store the request
const tempRequestFile = path.join(__dirname, 'temp_request.json');

exports.djangoApp = functions.https.onRequest(async (req, res) => {
  // Write request data to a temporary file
  const requestData = {
    method: req.method,
    path: req.path,
    headers: req.headers,
    query: req.query,
    body: req.body
  };
  
  fs.writeFileSync(tempRequestFile, JSON.stringify(requestData));
  
  // Set environment variables for Django
  const env = {
    ...process.env,
    PORT: 8080,
    DJANGO_SETTINGS_MODULE: 'webapp.settings',
    REQUEST_FILE: tempRequestFile
  };
  
  // Start Python handler
  const pythonProcess = spawn('python', ['django_handler.py'], {
    cwd: __dirname,
    env: env
  });
  
  let output = '';
  let error = '';
  
  // Handle process output
  pythonProcess.stdout.on('data', (data) => {
    output += data.toString();
    console.log(`Python stdout: ${data}`);
  });
  
  pythonProcess.stderr.on('data', (data) => {
    error += data.toString();
    console.error(`Python stderr: ${data}`);
  });
  
  // Set a timeout to kill the process if it takes too long
  const timeout = setTimeout(() => {
    pythonProcess.kill();
    res.status(504).send('Request timeout');
  }, 30000);
  
  // Handle process completion
  pythonProcess.on('close', (code) => {
    clearTimeout(timeout);
    console.log(`Python process exited with code ${code}`);
    
    // Clean up temporary file
    try {
      fs.unlinkSync(tempRequestFile);
    } catch (err) {
      console.error('Error cleaning up temp file:', err);
    }
    
    // Try to parse the output as JSON
    try {
      const response = JSON.parse(output);
      res.status(response.statusCode || 200).send(response.body);
    } catch (err) {
      console.error('Error parsing Python output:', err);
      res.status(500).send('Error processing request');
    }
  });
});
