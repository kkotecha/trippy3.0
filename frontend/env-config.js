// This file will be dynamically generated or manually updated for deployment
window.ENV = {
    API_URL: '__API_URL__' // This will be replaced during deployment
};

// For local development, use localhost if placeholder is still present
if (window.ENV.API_URL === '__API_URL__' || !window.ENV.API_URL) {
    window.ENV.API_URL = 'http://localhost:8000';
}
