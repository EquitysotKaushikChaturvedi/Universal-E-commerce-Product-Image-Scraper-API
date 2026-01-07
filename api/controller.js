// api/controller.js
const { spawn } = require('child_process');
const config = require('../shared/config');
const logger = require('../shared/logger');

/**
 * Validates if a string is a valid HTTP/HTTPS URL
 */
function isValidUrl(string) {
    try {
        const url = new URL(string);
        return url.protocol === 'http:' || url.protocol === 'https:';
    } catch (_) {
        return false;
    }
}

/**
 * Controller: Scrape URL
 * Handles the logic of calling the Python script.
 */
exports.scrapeUrl = (req, res) => {
    const { url } = req.body;

    // 1. Validation
    if (!url || !isValidUrl(url)) {
        return res.status(400).json({
            error_code: "INVALID_URL",
            message: "The provided URL is not valid. Must start with http:// or https://"
        });
    }

    logger.info(`Received scrape request for: ${url}`);

    // 2. Spawn Python Process
    const pythonProcess = spawn(config.PYTHON_CMD, [config.SCRAPER_SCRIPT, url]);

    let dataBuffer = '';
    let errorBuffer = '';

    // Set a timeout to kill the process if it hangs
    const timeout = setTimeout(() => {
        logger.error(`Timeout reached for ${url}`);
        pythonProcess.kill();
        // If we haven't responded yet, respond now
        if (!res.headersSent) {
            res.status(500).json({
                error_code: "SCRAPER_TIMEOUT",
                message: "The scraping process took too long and was terminated."
            });
        }
    }, config.TIMEOUT_MS);

    // 3. Collect Output
    pythonProcess.stdout.on('data', (data) => {
        dataBuffer += data.toString();
    });

    pythonProcess.stderr.on('data', (data) => {
        // We log stderr but don't fail immediately, as some warnings go to stderr
        errorBuffer += data.toString();
        // Optionally log every line from python stderr
        // logger.debug(`[Python Stderr]: ${data}`);
    });

    // 4. Handle Process Exit
    pythonProcess.on('close', (code) => {
        clearTimeout(timeout);

        if (res.headersSent) return;

        if (code !== 0) {
            logger.error(`Scraper failed with code ${code}`, { stderr: errorBuffer });
            return res.status(500).json({
                error_code: "SCRAPER_FAILED",
                message: "The scraping process failed.",
                details: errorBuffer.slice(0, 200) // Return first 200 chars of error for debugging
            });
        }

        // 5. Parse JSON
        try {
            const result = JSON.parse(dataBuffer);

            // Check if Python returned an error object itself (handled in python main)
            if (result.error_code) {
                return res.status(500).json(result);
            }

            logger.info(`Scraping successful`, { total: result.total_images });
            return res.status(200).json(result);

        } catch (e) {
            logger.error("Failed to parse Python Output", { data: dataBuffer });
            return res.status(500).json({
                error_code: "INVALID_OUTPUT",
                message: "The scraper did not return valid JSON.",
                raw_output: dataBuffer.slice(0, 100) // snippet
            });
        }
    });

    // Handle spawn errors (e.g., python not found)
    pythonProcess.on('error', (err) => {
        clearTimeout(timeout);
        if (!res.headersSent) {
            logger.error("Failed to spawn Python process", err);
            res.status(500).json({
                error_code: "INTERNAL_ERROR",
                message: "Failed to start scraping engine."
            });
        }
    });
};
