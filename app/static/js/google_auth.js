// app/static/js/google_auth.js
document.addEventListener('DOMContentLoaded', () => {
    const googleBtn = document.getElementById('google-signin-btn');

    if (googleBtn) {
        googleBtn.addEventListener('click', async () => {
            const provider = new firebase.auth.GoogleAuthProvider();

            try {
                const result = await firebase.auth().signInWithPopup(provider);
                const idToken = await result.user.getIdToken();

                const response = await fetch('/google-login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ id_token: idToken }),
                });

                const data = await response.json();

                if (data.status === 'ok') {
                    window.location.href = '/dashboard/';
                } else if (data.status === 'new_user') {
                    const leetcodeId = prompt('Welcome! Please enter your LeetCode username to complete registration:');
                    
                    if (leetcodeId) {
                        const finalResponse = await fetch('/google-register', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ id_token: idToken, leetcode_id: leetcodeId }),
                        });
                        const finalData = await finalResponse.json();
                        if (finalData.status === 'ok') {
                            window.location.href = '/dashboard/';
                        } else {
                            alert(finalData.message || 'Registration failed. The LeetCode ID might be invalid or already taken.');
                        }
                    }
                } else {
                    alert(data.message || 'An error occurred during login.');
                }
            } catch (error) {
                console.error("Google Sign-In Error:", error);
                if (error.code !== 'auth/popup-closed-by-user') {
                    alert("Could not complete sign in with Google.");
                }
            }
        });
    }
});