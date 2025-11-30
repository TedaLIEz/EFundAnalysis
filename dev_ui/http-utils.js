/**
 * HTTP utility functions for making requests to the FinWeave API.
 * This module can be easily extended for future HTTP endpoints.
 */

/**
 * Make a GET request to the API.
 *
 * @param {string} endpoint - The API endpoint (e.g., '/api/health')
 * @param {Object} options - Optional fetch options
 * @returns {Promise<Object>} The response data
 */
async function httpGet(endpoint, options = {}) {
    const baseUrl = getBaseUrl();
    const url = `${baseUrl}${endpoint}`;

    try {
        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
            ...options,
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return { success: true, data };
    } catch (error) {
        console.error('GET request failed:', error);
        return { success: false, error: error.message };
    }
}

/**
 * Make a POST request to the API.
 *
 * @param {string} endpoint - The API endpoint (e.g., '/api/chat')
 * @param {Object} body - The request body
 * @param {Object} options - Optional fetch options
 * @returns {Promise<Object>} The response data
 */
async function httpPost(endpoint, body, options = {}) {
    const baseUrl = getBaseUrl();
    const url = `${baseUrl}${endpoint}`;

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
            body: JSON.stringify(body),
            ...options,
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return { success: true, data };
    } catch (error) {
        console.error('POST request failed:', error);
        return { success: false, error: error.message };
    }
}

/**
 * Make a PUT request to the API.
 *
 * @param {string} endpoint - The API endpoint
 * @param {Object} body - The request body
 * @param {Object} options - Optional fetch options
 * @returns {Promise<Object>} The response data
 */
async function httpPut(endpoint, body, options = {}) {
    const baseUrl = getBaseUrl();
    const url = `${baseUrl}${endpoint}`;

    try {
        const response = await fetch(url, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
            body: JSON.stringify(body),
            ...options,
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return { success: true, data };
    } catch (error) {
        console.error('PUT request failed:', error);
        return { success: false, error: error.message };
    }
}

/**
 * Make a DELETE request to the API.
 *
 * @param {string} endpoint - The API endpoint
 * @param {Object} options - Optional fetch options
 * @returns {Promise<Object>} The response data
 */
async function httpDelete(endpoint, options = {}) {
    const baseUrl = getBaseUrl();
    const url = `${baseUrl}${endpoint}`;

    try {
        const response = await fetch(url, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
            ...options,
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return { success: true, data };
    } catch (error) {
        console.error('DELETE request failed:', error);
        return { success: false, error: error.message };
    }
}

/**
 * Get the base URL from the service URL input or use default.
 *
 * @returns {string} The base URL
 */
function getBaseUrl() {
    const serviceUrlInput = document.getElementById('serviceUrl');
    return serviceUrlInput?.value.trim() || 'http://localhost:5001';
}

/**
 * Example: Check health endpoint
 *
 * @returns {Promise<Object>} Health check response
 */
async function checkHealth() {
    return await httpGet('/health');
}

// Export functions for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        httpGet,
        httpPost,
        httpPut,
        httpDelete,
        checkHealth,
    };
}
