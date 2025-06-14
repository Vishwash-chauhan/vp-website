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
    // Redirect directly to home page
    window.location.href = '/';
}

/**
 * Set initial state for auth UI elements
 * Called on page load
 */
function setInitialAuthUIState() {
    // Get auth elements
    const userLinksElement = document.getElementById('user-links');
    const authLinksElement = document.getElementById('auth-links');
    
    // Mobile menu elements
    const mobileUserName = document.getElementById('mobile-user-name');
    const mobileAuthLogin = document.getElementById('mobile-auth-login');
    const mobileAuthSignup = document.getElementById('mobile-auth-signup');
    const mobileAuthDashboard = document.getElementById('mobile-auth-dashboard');
    const mobileAuthLogout = document.getElementById('mobile-auth-logout');
    
    // Remove any inline styles that might have been added
    if (userLinksElement) userLinksElement.removeAttribute('style');
    if (authLinksElement) authLinksElement.removeAttribute('style');
    
    // Make sure the mobile auth section is hidden initially
    const mobileAuthSection = document.querySelector('.mobile-only-auth');
    if (mobileAuthSection) {
        mobileAuthSection.classList.remove('active');
    }
    
    // Default to showing login/signup for non-authenticated state
    if (mobileAuthLogin) mobileAuthLogin.classList.add('mobile-auth-visible');
    if (mobileAuthSignup) mobileAuthSignup.classList.add('mobile-auth-visible');
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
    
    // Mobile menu elements
    const mobileUserName = document.getElementById('mobile-user-name');
    const mobileAuthLogin = document.getElementById('mobile-auth-login');
    const mobileAuthSignup = document.getElementById('mobile-auth-signup');
    const mobileAuthDashboard = document.getElementById('mobile-auth-dashboard');
    const mobileAuthLogout = document.getElementById('mobile-auth-logout');
    
    // Desktop menu updates
    if (userNameElement) {
        userNameElement.textContent = user.displayName || user.email || 'User';
    }
    
    if (userLinksElement) {
        userLinksElement.style.display = '';
    }
    
    if (authLinksElement) {
        authLinksElement.style.display = 'none';
    }    // Mobile menu updates
    if (mobileUserName) {
        mobileUserName.textContent = user.displayName || user.email || 'User';
        mobileUserName.classList.add('mobile-auth-visible');
    }
    
    // Hide login/signup, show logout in mobile menu
    if (mobileAuthLogin) mobileAuthLogin.classList.remove('mobile-auth-visible');
    if (mobileAuthSignup) mobileAuthSignup.classList.remove('mobile-auth-visible');
    if (mobileAuthLogout) mobileAuthLogout.classList.add('mobile-auth-visible');
    
    // Show dashboard link if user is admin
    if (mobileAuthDashboard && user.isAdmin) {
        mobileAuthDashboard.classList.add('mobile-auth-visible');
    }
}

/**
 * Update UI when user signs out
 */
function handleSignedOutUI() {
    const userLinksElement = document.getElementById('user-links');
    const authLinksElement = document.getElementById('auth-links');
    
    // Mobile menu elements
    const mobileUserName = document.getElementById('mobile-user-name');
    const mobileAuthLogin = document.getElementById('mobile-auth-login');
    const mobileAuthSignup = document.getElementById('mobile-auth-signup');
    const mobileAuthDashboard = document.getElementById('mobile-auth-dashboard');
    const mobileAuthLogout = document.getElementById('mobile-auth-logout');
    
    // Desktop menu updates
    if (userLinksElement) {
        userLinksElement.style.display = 'none';
    }
    
    if (authLinksElement) {
        authLinksElement.style.display = '';
    }
      // Mobile menu updates
    if (mobileUserName) {
        mobileUserName.classList.remove('mobile-auth-visible');
    }
    
    // Show login/signup, hide logout and dashboard in mobile menu
    if (mobileAuthLogin) mobileAuthLogin.classList.add('mobile-auth-visible');
    if (mobileAuthSignup) mobileAuthSignup.classList.add('mobile-auth-visible');
    if (mobileAuthLogout) mobileAuthLogout.classList.remove('mobile-auth-visible');
    if (mobileAuthDashboard) mobileAuthDashboard.classList.remove('mobile-auth-visible');
    
    // If on a protected page, redirect to home
    if (isProtectedPath) {
        window.location.href = '/';
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
document.addEventListener('DOMContentLoaded', () => {
    // Set initial state for UI elements
    setInitialAuthUIState();
    
    // Initialize the main auth functionality
    initializeAuth();
});

// Export for direct use
export { verifyAuthForProtectedPage, updateUIFromStoredToken };
