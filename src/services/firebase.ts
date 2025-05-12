
// NOTE: This file is kept for reference but is no longer actively used in the application.
// The system now uses a local Django-based ML model instead of Firebase for storage and ML.

// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getStorage } from "firebase/storage";
import { getFirestore } from "firebase/firestore";

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
// In a production app, these would come from environment variables
const firebaseConfig = {
  apiKey: "AIzaSyDummy-Key-For-Development-Replace-In-Production",
  authDomain: "document-processor-app.firebaseapp.com",
  projectId: "document-processor-app",
  storageBucket: "document-processor-app.appspot.com",
  messagingSenderId: "123456789012",
  appId: "1:123456789012:web:abc123def456ghi789jkl",
  measurementId: "G-ABCDEFGHIJ"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const storage = getStorage(app);
const db = getFirestore(app);

export { app, storage, db };

// Helper function to check if Firebase is properly configured
export const isFirebaseConfigured = () => {
  return firebaseConfig.apiKey !== "AIzaSyDummy-Key-For-Development-Replace-In-Production";
};

// Warning message for development
if (process.env.NODE_ENV !== 'production') {
  console.warn(
    'Firebase configuration is no longer actively used. The application now uses a Django-based ML model.'
  );
}
