// Import Firebase auth
import { getAuth, signOut } from "https://www.gstatic.com/firebasejs/10.9.0/firebase-auth.js";
import { clearAuthData } from './auth-state.js';

// Get the logout button
const logoutBtn = document.getElementById('logout-btn');

if (logoutBtn) {
    logoutBtn.addEventListener('click', async (e) => {
        e.preventDefault();
        
        try {
            // Show loading state if there's a spinner
            const spinner = document.querySelector('.loading-spinner');
            if (spinner) {
                spinner.style.display = 'flex';
            }
            
            const auth = getAuth();
            await signOut(auth);
              // Clear all auth data from localStorage
            clearAuthData();
            
            // Redirect to home page
            window.location.href = '/';
        } catch (error) {
            console.error("Error signing out:", error);
            alert("Failed to log out. Please try again.");
        }
    });
}
