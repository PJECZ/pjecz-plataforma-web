// Firebase authentification Google

// Función que es llamada cuando se da clic al botón firebase-sign-in-google
function googleToggleSignIn() {
    if (!firebase.auth().currentUser) {
        // Google Auth provider
        var googleProvider = new firebase.auth.GoogleAuthProvider();
        googleProvider.addScope('https://www.googleapis.com/auth/contacts.readonly');
        // Sign-in with pop-up
        firebase.auth().signInWithPopup(googleProvider).then(function (result) {
            // This gives you a Google Access Token
            //var token = result.credential.accessToken;
            // The signed-in user info
            //var user = result.user;
            document.getElementById('firebase-sign-in-google-status').textContent = 'Autenticado con Google';
            console.log(result);
        }).catch(function (error) {
            // Handle Errors here
            var errorCode = error.code;
            var errorMessage = error.message;
            // The email of the user's account used
            var email = error.email;
            // The firebase.auth.AuthCredential type that was used
            var credential = error.credential;
            if (errorCode === 'auth/account-exists-with-different-credential') {
                alert('You have already signed up with a different auth provider for that email.');
                // If you are using multiple auth providers on your app you should handle linking
                // the user's accounts here
            } else {
                console.error(error);
            }
        });
    } else {
        // Logout
        firebase.auth().signOut();
    }
    document.getElementById('firebase-sign-in-google').disabled = true;
}
