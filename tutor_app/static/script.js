document.addEventListener('DOMContentLoaded', function () {
    var goToBrowseTutorsButton = document.getElementById('goToBrowseTutorsButton');
    goToBrowseTutorsButton.addEventListener('click', function () {
        window.location.href = '/browse-tutors';
    });

    var goToSignUpAsTutorButton = document.getElementById('goToSignUpAsTutorButton');
    goToSignUpAsTutorButton.addEventListener('click', function () {
        window.location.href = '/tutor-signup';
    });

    var goToLoginAsTutorButton = document.getElementById('goToLoginAsTutorButton');
    goToLoginAsTutorButton.addEventListener('click', function () {
        window.location.href = '/tutor-login';
    });

});
