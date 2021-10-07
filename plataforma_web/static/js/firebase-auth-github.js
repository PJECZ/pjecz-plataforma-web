// Firebase authentification GitHub

// Función que es llamada cuando se da clic al botón firebase-sign-in-github
function githubToggleSignIn() {
    if (!firebase.auth().currentUser) {
        // GitHub Auth provider
        var githubProvider = new firebase.auth.GithubAuthProvider();
        githubProvider.addScope('repo');
        // Sign-in with pop-up
        firebase.auth().signInWithPopup(githubProvider).then(function (result) {
            // This gives you a GitHub Token
            //var token = result.credential.accessToken;
            // The signed-in user info
            //var user = result.user;
            document.getElementById('firebase-sign-in-github-status').textContent = 'Autenticado con GitHub';
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
    document.getElementById('firebase-sign-in-github').disabled = true;
}
