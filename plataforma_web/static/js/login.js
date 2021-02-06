/**
 * Function called when clicking the Login/Logout button
 */
function toggleSignIn() {
    if (!firebase.auth().currentUser) {
        var provider = new firebase.auth.GoogleAuthProvider();
        provider.addScope('https://www.googleapis.com/auth/contacts.readonly');
        firebase.auth().signInWithPopup(provider).then(function (result) {
            // This gives you a Google Access Token. You can use it to access the Google API
            //var token = result.credential.accessToken;
            //document.getElementById('quickstart-oauthtoken').textContent = token;
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
        firebase.auth().signOut();
    }
    document.getElementById('quickstart-sign-in').disabled = true;
}

/**
 * initApp handles setting up UI event listeners and registering Firebase auth listeners:
 *  - firebase.auth().onAuthStateChanged: This listener is called when the user is signed in or
 *    out, and that is where we update the UI
 */
function initApp() {
    // Listening for auth state changes
    firebase.auth().onAuthStateChanged(function (user) {
        if (user) {
            // User is signed in
            $('#quickstart-sign-in').text('Cerrar esta cuenta de Google') // Sign out
            $('#quickstart-sign-in-status').text('ABIERTA') // Signed in
            // Datos
            var displayName = user.displayName;
            var email = user.email;
            //var emailVerified = user.emailVerified;
            //var photoURL = user.photoURL;
            //var isAnonymous = user.isAnonymous;
            //var uid = user.uid;
            //var providerData = user.providerData;
            // ¡Hola NOMBRE/email!
            var welcomeName = displayName ? displayName : email;
            $('#user').text(welcomeName);
            // Llenar formulario
            user.getIdToken().then(function (idToken) {
                $('#email').val(user.email);
                $('#token').val(idToken);
            });
            // Mostrar y ocultar
            $('#firebase_logged_out').hide();
            $('#firebase_logged_in').show();
            $('#acceso_form_firebase_fields').show();
            $('#acceso_form_password_fields').hide();
        } else {
            // User is signed out
            $('#quickstart-sign-in').text('Abrir mi cuenta de Google') // Sign in with Google
            $('#quickstart-sign-in-status').text('CERRADA') // Signed out
            // Mostrar y ocultar
            $('#firebase_logged_out').show();
            $('#firebase_logged_in').hide();
            $('#acceso_form_firebase_fields').hide();
            $('#acceso_form_password_fields').show();
        }
        document.getElementById('quickstart-sign-in').disabled = false;
    });
    document.getElementById('quickstart-sign-in').addEventListener('click', toggleSignIn, false);
}
