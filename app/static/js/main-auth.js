/**
 * main-auth.js
 * Central authentication functionality for VyapaarNiti
 * 
 * This file provides frontend authentication features for all pages:
 * - Automatically checks authentication state when page loads
 * - Updates UI elements based on auth state
 * - Handles protected page access
 * - Ensures consistent auth behavior across the application
 */

import { auth } from './firebase-config.js';
import { 
    refreshTokenIfNeeded, 
    getAuthToken, 
    setAuthRedirectUrl, 
    AUTH_EVENTS 
} from './auth-state.js';

// Configuration
const PROTECTED_PATHS = [
    '/dashboard',
    '/admin',
    '/profile'
];

// Track if we're on a protected page
const isProtectedPath = PROTECTED_PATHS.some(path => window.location.pathname.startsWith(path));

/**
 * Initialize authentication for the current page
 */
function initializeAuth() {
    // If on a protected page, verify authentication
    if (isProtectedPath) {
        verifyAuthForProtectedPage();
    }
    
    // Set up UI update handlers
    setupAuthUIHandlers();
    
    // Update UI based on current auth state
    updateUIFromStoredToken();
}

/**
 * Verify user is authenticated for protected pages
 */
async function verifyAuthForProtectedPage() {
    try {
        // Try to refresh token
        const token = await refreshTokenIfNeeded();
        if (!token) {
            // No token, redirect to login
            handleUnauthenticatedAccess();
            return;
        }
        
        // Verify with backend
        const response = await fetch('/api/verify-token', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ token })
        });
        
        // If verification fails, redirect to login
        if (!response.ok) {
            console.error('Failed to verify auth token for protected page');
            handleUnauthenticatedAccess();
        }
    } catch (error) {
        console.error('Error verifying authentication:', error);
        handleUnauthenticatedAccess();
    }
}

/**
 * Handle case when unauthenticated user tries to access protected page
 */
function handleUnauthenticatedAccess() {
    // Save the current URL to redirect back after login
    setAuthRedirectUrl(window.location.pathname);
    
    // Redirect to login page
    window.location.href = '/auth/login?redirect=' + encodeURIComponent(window.location.pathname);
}

/**
 * Set up handlers for auth state UI updates
 */
function setupAuthUIHandlers() {
    // Listen for auth events
    document.addEventListener(AUTH_EVENTS.SIGNED_IN, handleSignedInUI);
    document.addEventListener(AUTH_EVENTS.SIGNED_OUT, handleSignedOutUI);
}

/**
 * Update UI when user signs in
 * @param {CustomEvent} event - Custom event with user data
 */
function handleSignedInUI(event) {
    const user = event.detail;
    
    // Update user name and show user menu
    const userNameElement = document.getElementById('user-name');
    const userLinksElement = document.getElementById('user-links');
    const authLinksElement = document.getElementById('auth-links');
    
    if (userNameElement) {
        userNameElement.textContent = user.displayName || user.email || 'User';
    }
    
    if (userLinksElement) {
        userLinksElement.style.display = '';
    }
    
    if (authLinksElement) {
        authLinksElement.style.display = 'none';
    }
}

/**
 * Update UI when user signs out
 */
function handleSignedOutUI() {
    const userLinksElement = document.getElementById('user-links');
    const authLinksElement = document.getElementById('auth-links');
    
    if (userLinksElement) {
        userLinksElement.style.display = 'none';
    }
    
    if (authLinksElement) {
        authLinksElement.style.display = '';
    }
    
    // If on a protected page, redirect to login
    if (isProtectedPath) {
        handleUnauthenticatedAccess();
    }
}

/**
 * Update UI based on stored token (for initial page load)
 */
async function updateUIFromStoredToken() {
    const token = getAuthToken();
    
    if (!token) {
        // No token, treat as signed out
        handleSignedOutUI();
        return;
    }
    
    try {
        // Validate token with backend
        const response = await fetch('/api/user-info', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) {
            handleSignedOutUI();
            return;
        }
        
        // Valid token, update UI with user info
        const data = await response.json();
        
        // Create fake event with user data from API
        const event = new CustomEvent(AUTH_EVENTS.SIGNED_IN, {
            detail: {
                displayName: data.user.displayName,
                email: data.user.email,
                uid: data.user.uid,
                isAdmin: data.user.custom_claims && data.user.custom_claims.admin
            }
        });
        
        // Dispatch the event to update UI
        document.dispatchEvent(event);
        
    } catch (error) {
        console.error('Error checking stored auth token:', error);
        handleSignedOutUI();
    }
}

// Initialize auth when DOM is ready
document.addEventListener('DOMContentLoaded', initializeAuth);

// Export for direct use
export { verifyAuthForProtectedPage, updateUIFromStoredToken };
