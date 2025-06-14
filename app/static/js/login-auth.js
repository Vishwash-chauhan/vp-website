import { auth, provider } from "./firebase-config.js";

import { createUserWithEmailAndPassword,
         signInWithEmailAndPassword,
         signInWithPopup,
         sendPasswordResetEmail } from "https://www.gstatic.com/firebasejs/10.9.0/firebase-auth.js";



/* == UI - Elements == */
const signInWithGoogleButtonEl = document.getElementById("sign-in-with-google-btn")
const signUpWithGoogleButtonEl = document.getElementById("sign-up-with-google-btn")
const emailInputEl = document.getElementById("email-input")
const passwordInputEl = document.getElementById("password-input")
const signInButtonEl = document.getElementById("sign-in-btn")
const createAccountButtonEl = document.getElementById("create-account-btn")
const emailForgotPasswordEl = document.getElementById("email-forgot-password")
const forgotPasswordButtonEl = document.getElementById("forgot-password-btn")

const errorMsgEmail = document.getElementById("email-error-message")
const errorMsgPassword = document.getElementById("password-error-message")
const errorMsgGoogleSignIn = document.getElementById("google-signin-error-message")



/* == UI - Event Listeners == */
if (signInWithGoogleButtonEl && signInButtonEl) {
    signInWithGoogleButtonEl.addEventListener("click", authSignInWithGoogle)
    signInButtonEl.addEventListener("click", authSignInWithEmail)
}

if (createAccountButtonEl) {
    createAccountButtonEl.addEventListener("click", authCreateAccountWithEmail)
}

if (signUpWithGoogleButtonEl) {
    signUpWithGoogleButtonEl.addEventListener("click", authSignUpWithGoogle)
}

if (forgotPasswordButtonEl) {
    forgotPasswordButtonEl.addEventListener("click", resetPassword)
}




/* === Main Code === */

/* = Functions - Firebase - Authentication = */

// Save token to localStorage and verify with backend
async function handleUserSignedIn(user) {
    try {
        // Show loading state
        showLoadingSpinner();
        
        // Import the auth state management functions
        import('./auth-state.js').then(async ({ storeAuthToken, getAndClearRedirectUrl }) => {
            try {
                // Get ID token
                const token = await user.getIdToken();
                
                // Store token using our auth state management
                storeAuthToken(token);
                
                // Verify token with backend
                const response = await fetch('/api/verify-token', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ token })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    // Get user data
                    const userData = data.user;
                      // Always redirect to home page
                    const redirectUrl = '/';
                    
                    // Redirect to home page
                    console.log('Authentication successful. Redirecting to home page.');
                    window.location.href = redirectUrl;
                } else {
                    // Handle error
                    console.error("Backend token verification failed:", data.error);
                    showError("Authentication failed. Please try again.");
                    hideLoadingSpinner();
                }
            } catch (error) {
                console.error("Error in auth state management:", error);
                showError("Authentication failed. Please try again.");
                hideLoadingSpinner();
            }
        }).catch(error => {
            console.error("Failed to load auth-state.js module:", error);
            showError("Authentication system failed to initialize.");
            hideLoadingSpinner();
        });
        
    } catch (error) {
        console.error("Error handling signed in user:", error);
        showError("Authentication failed. Please try again.");
        hideLoadingSpinner();
    }
}

// Function to sign in with Google authentication
async function authSignInWithGoogle() {
    // Show loading spinner
    showLoadingSpinner();
    
    // Configure Google Auth provider with custom parameters
    provider.setCustomParameters({
        'prompt': 'select_account'
    });

    try {
        // Attempt to sign in with a popup and retrieve user data
        const result = await signInWithPopup(auth, provider);

        // Check if the result or user object is undefined or null
        if (!result || !result.user) {
            throw new Error('Authentication failed: No user data returned.');
        }

        const user = result.user;
        const email = user.email;

        // Ensure the email is available in the user data
        if (!email) {
            throw new Error('Authentication failed: No email address returned.');
        }

        // Process the signed in user
        await handleUserSignedIn(user);

    } catch (error) {
        // Hide loading spinner
        hideLoadingSpinner();
        
        // Handle errors by logging and updating the UI
        console.error('Error during sign-in with Google:', error);
        showError("Google sign-in failed. Please try again.");
    }
}



// Function to create new account with Google auth - will also sign in existing users
async function authSignUpWithGoogle() {
    // Show loading spinner
    showLoadingSpinner();
    
    provider.setCustomParameters({
        'prompt': 'select_account'
    });

    try {
        const result = await signInWithPopup(auth, provider);
        
        if (!result || !result.user) {
            throw new Error('Authentication failed: No user data returned.');
        }
        
        const user = result.user;
        
        // Process the signed in user
        await handleUserSignedIn(user);
    } catch (error) {
        // Hide loading spinner
        hideLoadingSpinner();
        
        // The AuthCredential type that was used or other errors.
        console.error("Error during Google signup: ", error.message);
        showError("Google sign-up failed. Please try again.");
    }
}




async function authSignInWithEmail() {
    // Show loading spinner
    showLoadingSpinner();

    const email = emailInputEl.value;
    const password = passwordInputEl.value;
    
    // Clear previous error messages
    errorMsgEmail.textContent = "";
    errorMsgPassword.textContent = "";
    
    // Input validation
    if (!email) {
        errorMsgEmail.textContent = "Email is required";
        hideLoadingSpinner();
        return;
    }
    
    if (!password) {
        errorMsgPassword.textContent = "Password is required";
        hideLoadingSpinner();
        return;
    }

    try {
        const userCredential = await signInWithEmailAndPassword(auth, email, password);
        const user = userCredential.user;
        
        // Process the signed in user
        await handleUserSignedIn(user);
        
        console.log("User signed in: ", user.email);
    } catch (error) {
        // Hide loading spinner
        hideLoadingSpinner();
        
        const errorCode = error.code;
        console.error("Error code: ", errorCode);
        
        if (errorCode === "auth/invalid-email") {
            errorMsgEmail.textContent = "Invalid email";
        } else if (errorCode === "auth/invalid-credential") {
            errorMsgPassword.textContent = "Login failed - invalid email or password";
        } else if (errorCode === "auth/user-disabled") {
            errorMsgPassword.textContent = "Account has been disabled";
        } else {
            errorMsgPassword.textContent = "Login failed - please try again";
        }
    }
}



async function authCreateAccountWithEmail() {
    // Show loading spinner
    showLoadingSpinner();
    
    const email = emailInputEl.value;
    const password = passwordInputEl.value;
    
    // Clear previous error messages
    errorMsgEmail.textContent = "";
    errorMsgPassword.textContent = "";
    
    // Input validation
    if (!email) {
        errorMsgEmail.textContent = "Email is required";
        hideLoadingSpinner();
        return;
    }
    
    if (!password) {
        errorMsgPassword.textContent = "Password is required";
        hideLoadingSpinner();
        return;
    }
    
    if (password.length < 6) {
        errorMsgPassword.textContent = "Password must be at least 6 characters";
        hideLoadingSpinner();
        return;
    }    try {
        const userCredential = await createUserWithEmailAndPassword(auth, email, password);
        const user = userCredential.user;
        
        // Process the signed in user
        await handleUserSignedIn(user);
    } catch (error) {
        // Hide loading spinner
        hideLoadingSpinner();
        
        const errorCode = error.code;
        console.error("Error during sign-up:", error);

        if (errorCode === "auth/invalid-email") {
            errorMsgEmail.textContent = "Invalid email";
        } else if (errorCode === "auth/weak-password") {
            errorMsgPassword.textContent = "Invalid password - must be at least 6 characters";
        } else if (errorCode === "auth/email-already-in-use") {
            errorMsgEmail.textContent = "An account already exists for this email.";
        } else {
            errorMsgEmail.textContent = "Sign-up failed. Please try again.";
        }
    }

}



async function resetPassword() {
    // Show loading spinner
    showLoadingSpinner();
    
    const emailToReset = emailForgotPasswordEl.value;
    
    // Input validation
    if (!emailToReset) {
        // Show error message
        const errorMsg = document.getElementById("email-forgot-password-error");
        if (errorMsg) {
            errorMsg.textContent = "Please enter your email address";
        }
        hideLoadingSpinner();
        return;
    }

    try {
        await sendPasswordResetEmail(auth, emailToReset);
        
        if (emailForgotPasswordEl) {
            emailForgotPasswordEl.value = "";
        }
        
        // Password reset email sent!
        const resetFormView = document.getElementById("reset-password-view");
        const resetSuccessView = document.getElementById("reset-password-confirmation-page");

        if (resetFormView && resetSuccessView) {
            resetFormView.style.display = "none";
            resetSuccessView.style.display = "block";
        }
    } catch (error) {
        // Hide loading spinner
        hideLoadingSpinner();
        
        const errorCode = error.code;
        console.error("Password reset error:", error);
        
        // Show error message
        const errorMsg = document.getElementById("email-forgot-password-error");
        if (errorMsg) {
            if (errorCode === "auth/invalid-email") {
                errorMsg.textContent = "Invalid email address";
            } else if (errorCode === "auth/user-not-found") {
                errorMsg.textContent = "No account found with this email";
            } else {
                errorMsg.textContent = "Error sending reset email. Please try again.";
            }
        }
    } finally {
        // Hide loading spinner
        hideLoadingSpinner();
    }

}



function loginUser(user, idToken) {
    fetch('/auth', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${idToken}`
        },
        credentials: 'same-origin'  // Ensures cookies are sent with the request
    }).then(response => {
        if (response.ok) {
            window.location.href = '/dashboard';
        } else {
            console.error('Failed to login');
            // Handle errors here
        }
    }).catch(error => {
        console.error('Error with Fetch operation: ', error);
    });
}



// /* = Functions - UI = */
function clearInputField(field) {
	field.value = ""
}

function clearAuthFields() {
	clearInputField(emailInputEl)
	clearInputField(passwordInputEl)
}

// Utility functions
function showLoadingSpinner() {
    const spinner = document.getElementById('loading-spinner');
    const form = document.getElementById('login-form') || document.getElementById('signup-form');
    
    if (spinner) {
        spinner.style.display = 'flex';
    }
    
    if (form) {
        form.style.opacity = '0.5';
    }
}

function hideLoadingSpinner() {
    const spinner = document.getElementById('loading-spinner');
    const form = document.getElementById('login-form') || document.getElementById('signup-form');
    
    if (spinner) {
        spinner.style.display = 'none';
    }
    
    if (form) {
        form.style.opacity = '1';
    }
}

function showError(message) {
    const generalErrorMsg = document.getElementById('general-error-message');
    if (generalErrorMsg) {
        generalErrorMsg.textContent = message;
        generalErrorMsg.style.display = 'block';
    } else {
        console.error(message);
    }
}

