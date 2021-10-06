// Firebase authentification

// Buttons
const googleButton = document.getElementById('firebase-sign-in-google');
const githubButton = document.getElementById('firebase-sign-in-github');
const microsoftButton = document.getElementById('firebase-sign-in-microsoft');

// Firebase initApp
function initApp() {
    // Listening for auth state changes
    firebase.auth().onAuthStateChanged(function (user) {
        if (user) {
            // User is signed in
            var displayName = user.displayName;
            var email = user.email;
            var emailVerified = user.emailVerified;
            var photoURL = user.photoURL;
            var isAnonymous = user.isAnonymous;
            var uid = user.uid;
            var providerData = user.providerData;
            // Logged with
            googleButton.disabled = true;
            googleButton.style.display = 'none';
            githubButton.disabled = true;
            githubButton.style.display = 'none';
            microsoftButton.disabled = true;
            microsoftButton.style.display = 'none';
            providerData.forEach(data => {
                if (data['providerId'] == 'google.com') {
                    googleButton.textContent = 'Cerrar cuenta de Google';
                    googleButton.disabled = false;
                    googleButton.style.display = 'inline';
                }
                if (data['providerId'] == 'github.com') {
                    githubButton.textContent = 'Cerrar cuenta de GitHub';
                    githubButton.disabled = false;
                    githubButton.style.display = 'inline';
                }
                if (data['providerId'] == 'microsoft.com') {
                    microsoftButton.textContent = 'Cerrar cuenta de Microsoft';
                    microsoftButton.disabled = false;
                    microsoftButton.style.display = 'inline';
                }
            });
            // Welcome
            var welcomeUser = displayName ? displayName : email;
            document.getElementById('user').textContent = welcomeUser;
            // Account details
            //document.getElementById('account').style.display = 'inline';
            //document.getElementById('account-details').textContent = JSON.stringify(user, null, '  ');
            // Fill form
            user.getIdToken().then(function (idToken) {
                document.getElementById('email').setAttribute('value', user.email);
                document.getElementById('token').setAttribute('value', idToken);
                document.getElementById('firebase-logged-out').style.display = 'none';
                document.getElementById('firebase-logged-in').style.display = 'inline';
                document.getElementById('access-form-firebase').style.display = 'inline';
            });
        } else {
            // User is signed out
            googleButton.textContent = 'Google';
            googleButton.style.display = 'inline';
            googleButton.disabled = false;
            githubButton.textContent = 'GitHub';
            githubButton.style.display = 'inline';
            githubButton.disabled = false;
            microsoftButton.textContent = 'Microsoft';
            microsoftButton.style.display = 'inline';
            microsoftButton.disabled = false;
            document.getElementById('firebase-sign-in-google-status').textContent = '';
            document.getElementById('firebase-sign-in-github-status').textContent = '';
            document.getElementById('firebase-sign-in-microsoft-status').textContent = '';
            document.getElementById('firebase-logged-out').style.display = 'inline';
            document.getElementById('firebase-logged-in').style.display = 'none';
            document.getElementById('access-form-firebase').style.display = 'none';
            //document.getElementById('account-details').textContent = 'null';
        }
    });
    // Add listeners in buttons
    googleButton.addEventListener('click', googleToggleSignIn, false);
    githubButton.addEventListener('click', githubToggleSignIn, false);
    microsoftButton.addEventListener('click', microsoftToggleSignIn, false);
}
