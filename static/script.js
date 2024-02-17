document.addEventListener('DOMContentLoaded', function () {
    var goToBrowseTutorsButton = document.getElementById('goToBrowseTutorsButton');

    goToBrowseTutorsButton.addEventListener('click', function () {
        window.location.href = '/browse-tutors';
    });
});
