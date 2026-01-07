// api/routes.js
const express = require('express');
const router = express.Router();
const controller = require('./controller');

// GET /api/health
// Simple check to see if API is alive
router.get('/health', (req, res) => {
    res.json({
        status: "ok",
        uptime: process.uptime(),
        timestamp: new Date().toISOString()
    });
});

// POST /api/scrape
// The main worker route
router.post('/scrape', controller.scrapeUrl);

module.exports = router;
