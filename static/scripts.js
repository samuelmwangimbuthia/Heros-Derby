
var close_login = document.getElementById('close_login');
var close_signup = document.getElementById('close_signup');
var loginForm = document.getElementById('loginForm');
var signupForm = document.getElementById('signupForm');
var registerButton = document.getElementById('registerButton');
var loginButtonNormal = document.getElementById('loginButton1')
var loginButtonPlayer = document.getElementById('loginButton2')
var loginButtonCoach = document.getElementById('loginButton3')
var loginButtonSponsor = document.getElementById('loginButton4')



loginButtonNormal.addEventListener('click', function (event) {
    event.preventDefault();
    loginForm.style.display = 'block';
});

loginButtonPlayer.addEventListener('click', function (event) {
    event.preventDefault();
    loginForm.style.display = 'block';
});
loginButtonCoach.addEventListener('click', function (event) {
    event.preventDefault();
    loginForm.style.display = 'block';
});
loginButtonSponsor.addEventListener('click', function (event) {
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

// Show more or less button
// Select all rows except the first one
let showTeams = document.getElementById("showMore")
let hideTeams = document.getElementById("showLess")
showTeams.addEventListener("click", function(event){
    event.preventDefault();
    showTeams.style.display = 'none';
    hideTeams.style.display = 'block';
})
hideTeams.addEventListener("click", function(event){
    event.preventDefault();
    hideTeams.style.display = 'none';
    showTeams.style.display = 'block';
})
/*querySelectorAll("tr:nth-child(n+9)").forEach(function (e) {

    // Add onClick event listener
    // to selected rows
    e.addEventListener("click", function () {

        // Get all rows except the first one
        var rows =
            [...document.querySelectorAll(
                "tr:not(:first-child)"
            )];

        var notSelectedRows =
            rows.filter(function (element) {
                
            // Hide the rows that have
            // not been clicked
            if (element !== e) {
                element.style.display = "none";
            }
        });
    });
});


*/

