/**
 * API Interceptor
 * Utility for making authenticated API requests with Firebase token
 */
import { getAuthToken, refreshTokenIfNeeded, setAuthRedirectUrl } from './auth-state.js';

// Define a base URL for API calls
const API_BASE_URL = '/api';

/**
 * Make an authenticated API request
 * @param {string} endpoint - API endpoint path (without leading slash)
 * @param {Object} options - Fetch API options
 * @returns {Promise<any>} - Response JSON data
 */
async function apiRequest(endpoint, options = {}) {
    // First try to refresh the token if needed
    const token = await refreshTokenIfNeeded();
    
    // Check if token exists
    if (!token) {
        console.error('No authentication token found. User might not be signed out.');
        
        // If we're not on the auth pages, save current URL and redirect to login
        if (!window.location.pathname.includes('/auth/')) {
            setAuthRedirectUrl(window.location.pathname);
            window.location.href = '/auth/login';
        }
        
        throw new Error('Authentication required');
    }
    
    // Set up headers with authorization
    const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
        ...(options.headers || {})
    };
    
    // Make the request
    try {
        const response = await fetch(`${API_BASE_URL}/${endpoint}`, {
            ...options,
            headers
        });
        
        // Check for unauthorized response
        if (response.status === 401) {
            // Token might be expired - redirect to login
            console.error('Authentication failed. Token may be expired.');
            setAuthRedirectUrl(window.location.pathname);
            window.location.href = '/auth/login';
            throw new Error('Authentication failed');
        }
        
        // Parse the response
        const data = await response.json();
        
        // Check for error in response data
        if (!response.ok) {
            throw new Error(data.error || 'API request failed');
        }
        
        return data;
    } catch (error) {
        console.error(`API request to ${endpoint} failed:`, error);
        throw error;
    }
}

/**
 * Shorthand for GET requests
 */
async function apiGet(endpoint, options = {}) {
    return apiRequest(endpoint, { 
        ...options,
        method: 'GET' 
    });
}

/**
 * Shorthand for POST requests
 */
async function apiPost(endpoint, data = {}, options = {}) {
    return apiRequest(endpoint, {
        ...options,
        method: 'POST',
        body: JSON.stringify(data)
    });
}

/**
 * Shorthand for PUT requests
 */
async function apiPut(endpoint, data = {}, options = {}) {
    return apiRequest(endpoint, {
        ...options,
        method: 'PUT',
        body: JSON.stringify(data)
    });
}

/**
 * Shorthand for DELETE requests
 */
async function apiDelete(endpoint, options = {}) {
    return apiRequest(endpoint, {
        ...options,
        method: 'DELETE'
    });
}

export { apiRequest, apiGet, apiPost, apiPut, apiDelete };
