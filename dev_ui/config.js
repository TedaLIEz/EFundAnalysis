/**
 * Configuration file for FinWeave Frontend
 * This file can be customized for different environments
 */

// Backend API URL configuration
// For Azure App Service, you can override this by setting REACT_APP_API_URL
// in Application Settings -> Configuration -> Application settings
window.REACT_APP_API_URL = window.REACT_APP_API_URL ||
    (window.location.hostname === 'localhost'
        ? 'http://localhost:5001'
        : `${window.location.protocol}//${window.location.hostname}:5001`);
