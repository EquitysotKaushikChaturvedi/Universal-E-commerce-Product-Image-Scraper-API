// shared/config.js
/**
 * ONE PLACE for all settings.
 * If we need to change a timeout or a path, we do it HERE.
 */

const path = require('path');

module.exports = {
    // API Server Port
    PORT: process.env.PORT || 3000,

    // Path to the Python executable (assumes 'python' is in PATH)
    PYTHON_CMD: 'python',

    // Path to the scraper script (Absolute path is safer)
    SCRAPER_SCRIPT: path.join(__dirname, '../scraper/scraper.py'),

    // Execution Limits
    TIMEOUT_MS: 45000, // 45 seconds total timeout for Python process



    // Validation Defaults
    MIN_IMAGE_WIDTH: 300,
    MIN_IMAGE_HEIGHT: 300,
};
