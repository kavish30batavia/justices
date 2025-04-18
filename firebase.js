import { initializeApp } from "https://www.gstatic.com/firebasejs/9.15.0/firebase-app.js";
import { 
  getAuth, 
  GoogleAuthProvider, 
  signInWithPopup, 
  signInWithEmailAndPassword, 
  createUserWithEmailAndPassword,
  sendPasswordResetEmail
} from "https://www.gstatic.com/firebasejs/9.15.0/firebase-auth.js";
import { 
  getFirestore, 
  doc, 
  setDoc, 
  getDoc 
} from "https://www.gstatic.com/firebasejs/9.15.0/firebase-firestore.js";

// ✅ Correct Firebase Configuration
const firebaseConfig = {
    apiKey: "AIzaSyCXBidb_LLMcZIFgydtBmIh0roiNZxZQJ8",
    authDomain: "lawchatbot-83152.firebaseapp.com",
    projectId: "lawchatbot-83152",
    storageBucket: "lawchatbot-83152.appspot.com",  // ✅ Corrected storage bucket
    messagingSenderId: "771007178800",
    appId: "1:771007178800:web:49d8faf68c838f1b4c25f5",
    measurementId: "G-W50N0CDVWB"
};

// ✅ Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);
const provider = new GoogleAuthProvider();
provider.setCustomParameters({ prompt: "select_account" });

// ✅ Sign Up with Email & Password


// ✅ Sign In with Email & Password
// ✅ Function to fetch email & password from Firestore, then authenticate
async function signInWithEmail(email, password) {
    try {
        const userCredential = await signInWithEmailAndPassword(auth, email, password);
        console.log("✅ Login Successful:", userCredential.user.uid);
        return userCredential.user;
    } catch (error) {
        console.error("❌ Login Error:", error.message);

        // 🔹 Handle specific errors
        switch (error.code) {
            case "auth/user-not-found":
                alert("No user found with this email.");
                break;
            case "auth/wrong-password":
                alert("Incorrect password. Please try again.");
                break;
            case "auth/too-many-requests":
                alert("Too many login attempts. Try again later.");
                break;
            default:
                alert("Login failed. Please check your credentials.");
        }

        throw error;
    }
}

// ✅ Google Sign-In (Also Saves User in Firestore)
// ✅ Password Reset
async function resetPassword(email) {
    try {
        await sendPasswordResetEmail(auth, email);
        console.log("✅ Password reset email sent.");
    } catch (error) {
        console.error("❌ Password Reset Error:", error.message);
        throw error;
    }
}

// In firebase.js, modify the signUpWithEmail function
async function signUpWithEmail(email, password, role) {
    try {
        const userCredential = await createUserWithEmailAndPassword(auth, email, password);
        const user = userCredential.user;

        const userRef = doc(db, "users", user.uid);
        const userSnap = await getDoc(userRef);

        if (!userSnap.exists()) {
            await setDoc(userRef, {
                uid: user.uid,
                email: user.email,
                role: role,
                createdAt: new Date()
            });
            console.log("✅ User stored in Firestore:", user.uid);
        } else {
            console.log("ℹ️ User already exists in Firestore.");
        }

        return user;
    } catch (error) {
        console.error("❌ Sign-Up Error:", error.message);
        throw error;
    }
}

// Also update the Google sign-in to set a default role
async function signInWithGoogle() {
    try {
        const result = await signInWithPopup(auth, provider);
        const user = result.user;

        const userRef = doc(db, "users", user.uid);
        const userSnap = await getDoc(userRef);

        if (!userSnap.exists()) {
            await setDoc(userRef, {
                uid: user.uid,
                email: user.email,
                provider: "Google",
                role: "user", // Default role for Google sign-in
                createdAt: new Date()
            });
            console.log("✅ Google User stored in Firestore:", user.uid);
        } else {
            console.log("ℹ️ Google User already exists in Firestore.");
        }

        return user;
    } catch (error) {
        console.error("❌ Google Sign-In Error:", error.message);
        throw error;
    }
}
// ✅ Export functions
export { auth, db, signUpWithEmail, signInWithEmail, signInWithGoogle, resetPassword };