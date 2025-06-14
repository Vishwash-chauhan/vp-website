import { initializeApp } from "https://www.gstatic.com/firebasejs/10.9.0/firebase-app.js";
import { getAuth, 
         GoogleAuthProvider } from "https://www.gstatic.com/firebasejs/10.9.0/firebase-auth.js";
import { getFirestore } from "https://www.gstatic.com/firebasejs/10.9.0/firebase-firestore.js";

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyCp3aj3df0U0SczDgiR1G3K_N5QkYDvN3g",
  authDomain: "flask-vn-login.firebaseapp.com",
  projectId: "flask-vn-login",
  storageBucket: "flask-vn-login.firebasestorage.app",
  messagingSenderId: "444621650715",
  appId: "1:444621650715:web:29091ff9e6c7ab7f9171be",
  measurementId: "G-GE2BBFG4BS"
};

  // Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const provider = new GoogleAuthProvider();

const db = getFirestore(app);

export { auth, provider, db };