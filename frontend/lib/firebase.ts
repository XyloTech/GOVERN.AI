import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
import { getAuth, GoogleAuthProvider } from "firebase/auth";

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyAQs-Ta8XVg2uHaO3c_2zluCJRRpvNqRnk",
  authDomain: "governai-37f33.firebaseapp.com",
  projectId: "governai-37f33",
  storageBucket: "governai-37f33.firebasestorage.app",
  messagingSenderId: "122280908210",
  appId: "1:122280908210:web:9ce8f2273c383f568840ab",
  measurementId: "G-L3PXTVDN3E"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Firebase Auth
export const auth = getAuth(app);
export const googleProvider = new GoogleAuthProvider();

// Initialize Analytics (only in browser)
export const analytics = typeof window !== 'undefined' ? getAnalytics(app) : null;

export default app;

