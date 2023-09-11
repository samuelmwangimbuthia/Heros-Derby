//open user login form
var close_login = document.getElementById('close_login');
var close_signup = document.getElementById('close_signup');
var loginForm = document.getElementById('loginForm');
var signupForm = document.getElementById('signupForm');
var registerButton = document.getElementById('registerButton');
var loginButton = document.getElementById('loginButton')


loginButton.addEventListener('click', function (event) {
    event.preventDefault();
    loginForm.style.display = 'block';
});

registerButton.addEventListener('click', function (event) {
    event.preventDefault();
    signupForm.style.display = 'block';
});

close_login.addEventListener('click', function (event) {
    event.preventDefault();
    loginForm.style.display = 'none';
});

//close login form
close_signup.addEventListener('click', function (event) {
    event.preventDefault();
    signupForm.style.display = 'none';
});






