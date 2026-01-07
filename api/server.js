// api/server.js
const express = require('express');
const config = require('../shared/config');
const logger = require('../shared/logger');
const routes = require('./routes');

const app = express();

// Middleware: Parse JSON bodies
app.use(express.json());

// Middleware: CORS (Manual Logic)
app.use((req, res, next) => {
    res.header("Access-Control-Allow-Origin", "*");
    res.header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept");
    res.header("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
    if (req.method === 'OPTIONS') {
        return res.sendStatus(200);
    }
    next();
});

// Middleware: Request Logger
app.use((req, res, next) => {
    logger.info(`${req.method} ${req.originalUrl}`);
    next();
});

// Mount Routes
app.use('/api', routes);

// API-Only Mode (Frontend Removed)
app.get('/', (req, res) => {
    res.json({
        service: "Universal E-commerce Scraper API",
        status: "Running",
        endpoints: {
            health: "GET /api/health",
            scrape: "POST /api/scrape"
        },
        version: "2.0 (Backend Only)"
    });
});

// 404 Handler
app.use((req, res) => {
    res.status(404).json({
        error_code: "NOT_FOUND",
        message: "Endpoint not found."
    });
});

// Global Error Handler
app.use((err, req, res, next) => {
    logger.error("Unhandled Server Error", err);
    res.status(500).json({
        error_code: "SERVER_ERROR",
        message: "Something went wrong on the server.",
        debug_error: err.message,
        stack: err.stack
    });
});

// Start Server
app.listen(config.PORT, () => {
    logger.info(`API Gateway listening on http://localhost:${config.PORT}`);
    logger.info(`Mode: Production-Ready`);
});
