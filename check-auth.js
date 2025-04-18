// check-auth.js
import { auth, db } from "./firebase.js";
import { doc, getDoc } from "https://www.gstatic.com/firebasejs/9.15.0/firebase-firestore.js";

export async function checkAuth() {
    return new Promise(async (resolve, reject) => {
        auth.onAuthStateChanged(async (user) => {
            if (user) {
                // User is signed in
                const userRef = doc(db, "users", user.uid);
                const userSnap = await getDoc(userRef);
                
                if (userSnap.exists()) {
                    const userData = userSnap.data();
                    sessionStorage.setItem('user', JSON.stringify(userData));
                    resolve(userData);
                } else {
                    reject(new Error("User data not found"));
                }
            } else {
                // No user is signed in
                reject(new Error("User not authenticated"));
            }
        });
    });
}

export function redirectBasedOnRole() {
    const userData = JSON.parse(sessionStorage.getItem('user'));
    if (!userData) {
        window.location.href = "Login.html";
        return;
    }
    
    const currentPage = window.location.pathname.split('/').pop();
    let shouldRedirect = false;
    let targetPage = "Login.html";
    
    switch(userData.role) {
        case 'lawyer':
            if (!currentPage.includes('lawyerdashboard')) {
                shouldRedirect = true;
                targetPage = "lawyerdashboard.html";
            }
            break;
        case 'student':
            if (!currentPage.includes('studentdashboard')) {
                shouldRedirect = true;
                targetPage = "studentdashboard.html";
            }
            break;
        default:
            if (!currentPage.includes('dashboard')) {
                shouldRedirect = true;
                targetPage = "dashboard.html";
            }
    }
    
    if (shouldRedirect) {
        window.location.href = targetPage;
    }
}