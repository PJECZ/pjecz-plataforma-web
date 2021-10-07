// Firebase authentification Microsoft

// Función que es llamada cuando se da clic al botón firebase-sign-in-microsoft
function microsoftToggleSignIn() {
    if (!firebase.auth().currentUser) {
        // Microsoft Auth provider
        var microsoftProvider = new firebase.auth.OAuthProvider('microsoft.com');
        microsoftProvider.addScope('User.Read');
        // Sign-in with pop-up
        firebase.auth().signInWithPopup(microsoftProvider).then(function (result) {
            // This gives you a Microsoft Token
            //var token = result.credential.accessToken;
            // You can also retrieve the OAuth ID token
            //var idToken = result.credential.idToken;
            // The signed-in user info
            //var user = result.user;
            document.getElementById('firebase-sign-in-microsoft-status').textContent = 'Autenticado con Microsoft';
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
    document.getElementById('firebase-sign-in-microsoft').disabled = true;
}
