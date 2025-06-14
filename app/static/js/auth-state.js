/**
 * auth-state.js
 * Handles Firebase authentication state and token management across the application
 */

import { auth } from './firebase-config.js';
import { onAuthStateChanged, getIdToken } from "https://www.gstatic.com/firebasejs/10.9.0/firebase-auth.js";

// Constants
const TOKEN_KEY = 'firebaseToken';
const TOKEN_EXPIRY_KEY = 'firebaseTokenExpiry';
const REDIRECT_KEY = 'authRedirectUrl';
const TOKEN_REFRESH_THRESHOLD = 5 * 60 * 1000; // 5 minutes in milliseconds

// Event names for custom events
const AUTH_EVENTS = {
  SIGNED_IN: 'firebaseAuthSignedIn',
  SIGNED_OUT: 'firebaseAuthSignedOut',
  TOKEN_REFRESHED: 'firebaseTokenRefreshed',
};

/**
 * Initialize the auth state observer
 * This should be called when the application loads
 */
function initAuthStateObserver() {
  onAuthStateChanged(auth, handleAuthStateChanged);
  attachTokenRefreshHandler();
}

/**
 * Handle auth state changes
 * @param {Object|null} user - Firebase user object or null if signed out
 */
async function handleAuthStateChanged(user) {
  if (user) {
    // User is signed in
    console.log('User signed in:', user.email);
    
    try {
      // Get the token
      const token = await user.getIdToken();
      
      // Store the token
      storeAuthToken(token);
      
      // Dispatch signed in event
      dispatchAuthEvent(AUTH_EVENTS.SIGNED_IN, { 
        uid: user.uid,
        email: user.email,
        displayName: user.displayName,
        photoURL: user.photoURL,
      });
      
      // Update UI for authenticated state
      updateUIForAuthState(true);
      
      // Verify token with backend
      await verifyTokenWithBackend(token);
    } catch (error) {
      console.error('Error during auth state change:', error);
    }
  } else {
    // User is signed out
    console.log('User signed out');
    
    // Clear auth data
    clearAuthData();
    
    // Dispatch signed out event
    dispatchAuthEvent(AUTH_EVENTS.SIGNED_OUT);
    
    // Update UI for unauthenticated state
    updateUIForAuthState(false);
  }
}

/**
 * Store authentication token with expiry
 * @param {string} token - Firebase ID token
 */
function storeAuthToken(token) {
  // Store the token
  localStorage.setItem(TOKEN_KEY, token);
  
  // Calculate and store expiry time (Firebase tokens typically last 1 hour)
  const expiryTime = Date.now() + 60 * 60 * 1000; // Current time + 1 hour
  localStorage.setItem(TOKEN_EXPIRY_KEY, expiryTime);
  
  // Dispatch token refreshed event
  dispatchAuthEvent(AUTH_EVENTS.TOKEN_REFRESHED, { token });
}

/**
 * Get the stored auth token
 * @returns {string|null} The stored token or null if not found
 */
function getAuthToken() {
  return localStorage.getItem(TOKEN_KEY);
}

/**
 * Check if the stored token is expired or about to expire
 * @returns {boolean} True if token needs refresh, false otherwise
 */
function needsTokenRefresh() {
  const expiryTime = localStorage.getItem(TOKEN_EXPIRY_KEY);
  if (!expiryTime) return true;
  
  // Check if current time is within the refresh threshold of expiry
  return Date.now() + TOKEN_REFRESH_THRESHOLD > parseInt(expiryTime);
}

/**
 * Refresh the auth token if needed
 * @returns {Promise<string|null>} The refreshed token or null if unable to refresh
 */
async function refreshTokenIfNeeded() {
  // Check if user is signed in
  const currentUser = auth.currentUser;
  if (!currentUser) return null;
  
  // Check if token needs refresh
  if (needsTokenRefresh()) {
    try {
      // Force token refresh
      const newToken = await currentUser.getIdToken(true);
      storeAuthToken(newToken);
      return newToken;
    } catch (error) {
      console.error('Error refreshing token:', error);
      return null;
    }
  }
  
  // Return existing token if no refresh needed
  return getAuthToken();
}

/**
 * Clear all authentication data from storage
 */
function clearAuthData() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(TOKEN_EXPIRY_KEY);
}

/**
 * Setup automatic token refresh
 */
function attachTokenRefreshHandler() {
  // Check for token refresh need periodically
  setInterval(async () => {
    if (auth.currentUser && needsTokenRefresh()) {
      await refreshTokenIfNeeded();
    }
  }, 60 * 1000); // Check every minute
}

/**
 * Store redirect URL for after authentication
 * @param {string} url - URL to redirect to after auth
 */
function setAuthRedirectUrl(url) {
  sessionStorage.setItem(REDIRECT_KEY, url);
}

/**
 * Get and clear the redirect URL
 * @returns {string} The URL to redirect to, or '/' if none
 */
function getAndClearRedirectUrl() {
  const url = sessionStorage.getItem(REDIRECT_KEY) || '/';
  sessionStorage.removeItem(REDIRECT_KEY);
  return url;
}

/**
 * Verify token with backend
 * @param {string} token - Firebase ID token to verify
 * @returns {Promise<Object>} User data from backend
 */
async function verifyTokenWithBackend(token) {
  try {
    const response = await fetch('/api/verify-token', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ token }),
    });
    
    if (!response.ok) {
      throw new Error('Failed to verify token with backend');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error verifying token with backend:', error);
    throw error;
  }
}

/**
 * Update UI elements based on authentication state
 * @param {boolean} isAuthenticated - Whether user is authenticated
 */
function updateUIForAuthState(isAuthenticated) {
  // Get all auth-dependent elements
  const authOnly = document.querySelectorAll('.auth-only');
  const noAuthOnly = document.querySelectorAll('.no-auth-only');
  const adminOnly = document.querySelectorAll('.admin-only');
  
  // Update visibility based on auth state
  if (isAuthenticated) {
    authOnly.forEach(el => el.style.display = '');
    noAuthOnly.forEach(el => el.style.display = 'none');
    
    // Check if user is admin
    checkAndUpdateAdminUI();
  } else {
    authOnly.forEach(el => el.style.display = 'none');
    noAuthOnly.forEach(el => el.style.display = '');
    adminOnly.forEach(el => el.style.display = 'none');
  }
}

/**
 * Check if user has admin privileges and update UI accordingly
 */
async function checkAndUpdateAdminUI() {
  try {
    const token = await refreshTokenIfNeeded();
    if (!token) return;
    
    // Verify with backend
    const response = await fetch('/api/user-info', {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    
    if (!response.ok) return;
    
    const data = await response.json();
    const isAdmin = data.user && data.user.custom_claims && data.user.custom_claims.admin;
    
    // Update admin elements
    const adminOnly = document.querySelectorAll('.admin-only');
    adminOnly.forEach(el => {
      el.style.display = isAdmin ? '' : 'none';
    });
  } catch (error) {
    console.error('Error checking admin status:', error);
  }
}

/**
 * Dispatch custom auth event
 * @param {string} eventName - Name of the event
 * @param {Object} detail - Event details
 */
function dispatchAuthEvent(eventName, detail = {}) {
  const event = new CustomEvent(eventName, { 
    detail,
    bubbles: true,
    cancelable: true,
  });
  document.dispatchEvent(event);
}

// Initialize auth state management when the script is loaded
document.addEventListener('DOMContentLoaded', initAuthStateObserver);

// Export functions and constants for use in other scripts
export { 
  getAuthToken,
  refreshTokenIfNeeded,
  setAuthRedirectUrl,
  getAndClearRedirectUrl,
  AUTH_EVENTS,
  storeAuthToken,
  clearAuthData
};
