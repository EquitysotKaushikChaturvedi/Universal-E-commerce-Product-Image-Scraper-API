// shared/logger.js
/**
 * Simple Logger
 * Why? clean logs help us debug without reading 1000 lines of junk.
 */

const getTimestamp = () => new Date().toISOString();

const logger = {
    info: (message, data = {}) => {
        console.log(JSON.stringify({
            level: 'INFO',
            timestamp: getTimestamp(),
            message,
            ...data
        }));
    },

    error: (message, error = {}) => {
        console.error(JSON.stringify({
            level: 'ERROR',
            timestamp: getTimestamp(),
            message,
            error: error.message || error,
            stack: error.stack || undefined
        }));
    },

    debug: (message, data = {}) => {
        // Only print debug if needed (can use env var here later)
        if (process.env.DEBUG) {
            console.debug(JSON.stringify({
                level: 'DEBUG',
                timestamp: getTimestamp(),
                message,
                ...data
            }));
        }
    }
};

module.exports = logger;
