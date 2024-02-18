import pytest
from flask import session

from tutor_app.app import Tutor
from tutor_app.app import app as flask_app
from tutor_app.app import db

# Fixtures are used to enable the test functions to set up and tear down instances of the app
# without having to repea the code every time.
# Only need to pass the fixture name as an argument to each test function


@pytest.fixture()
def test_app():
    flask_app.config.update({"TESTING": True})
    yield flask_app


@pytest.fixture
def client(test_app):
    with test_app.test_client() as client:
        with test_app.app_context():
            db.drop_all()
            db.create_all()

            seed_data = [
                ["John Doe", "john.doe@tutorplanet.co.uk", "password"],
                ["Jane Smith", "jane.smith@tutorplanet.co.uk", "password"],
            ]
            for name, email, password in seed_data:
                tutor = Tutor(name=name, email=email, password=password)
                db.session.add(tutor)
                db.session.commit()

            yield client


@pytest.fixture()
def runner(test_app):
    return test_app.test_cli_runner()


def test_seed_data(client):
    """
    Test that the client test fixture has added the seed data as expected.
    Also testing that the database table, Tutor, can be queried.
    """
    tutors = Tutor.query.all()
    assert len(tutors) == 2
    assert all([isinstance(tutor, Tutor) for tutor in tutors])
    assert Tutor.query.filter_by(name="John Doe").first() is not None
    assert Tutor.query.filter_by(name="Jane Smith").first() is not None


def test_homepage(client):
    """
    Test that the web app's root returns an ok response when retrieved,
    and that the page contains two of the expected headers.
    This ensures the correct html template is being used.
    """
    response = client.get("/")
    assert response.status_code == 200
    assert b"<h1>Tutor Planet</h1>" in response.data
    assert b"<h2>Welcome to Tutor Planet!</h2>" in response.data


def test_browse_tutors(client):
    """
    Test that Browse Tutors page returns an ok response when retrieved,
    and that the page contains the expected header and a table element for listing tutors.
    This ensures the correct html template is being used.
    """
    response = client.get("/browse-tutors")
    assert response.status_code == 200
    assert b"<h2>Browse Tutors</h2>" in response.data
    assert b"</table>" in response.data


def test_tutor_signup_get(client):
    """
    Test that Tutor Sign Up page returns an ok response when retrieved,
    and that the page contains the expected form element for inputting data
    and a button element to post the data.
    This ensures the correct html template is being used.
    """
    response = client.get("/tutor-signup")
    assert response.status_code == 200
    assert b'<form id="tutor-signup-form">' in response.data
    assert b'<button type="submit">Sign Up</button>' in response.data


def test_tutor_signup_post_success(client):
    """
    Test that a post request made to sign up a new tutor can successfully
    add a new entry to the Tutor table in the database,
    and returns a message to the user displayed on the page.
    """
    response = client.post(
        "/tutor-signup",
        data={
            "name": "Samantha Doe",
            "email": "samantha@example.com",
            "password": "password",
        },
    )
    assert response.status_code == 200
    assert Tutor.query.filter_by(name="Samantha Doe").first() is not None
    assert response.json["message"] == "You've successfully signed up as a tutor!"


def test_tutor_signup_post_failure(client):
    """
    Test that trying to sign up as a tutor with an existing tutor's email
    will not cause any changes in the database's Tutor table
    and will return the appropriate error message to the user on the page.
    """
    existing_users_name = "John Doe"
    new_users_name = "Johnny Doe"

    response = client.post(
        "/tutor-signup",
        data={
            "name": new_users_name,
            "email": "john.doe@tutorplanet.co.uk",
            "password": "password",
        },
    )
    assert response.status_code == 200
    assert (
        Tutor.query.filter_by(email="john.doe@tutorplanet.co.uk").first().name
        == existing_users_name
    )
    assert (
        response.json["message"]
        == "The email you have entered is already in use for an existing tutor account."
    )


def test_tutor_profile_success(client):
    """
    Test that a Tutor Profile page can be retrieved using an existing tutor ID,
    and that the page contains the expected header element.
    This ensures the correct html template is being used.
    """
    existing_tutor = Tutor.query.first()
    assert existing_tutor is not None
    response = client.get(f"/tutor-{existing_tutor.tutor_id}-profile")
    assert response.status_code == 200
    assert existing_tutor.tutor_id == 1
    assert b"Tutor Profile</h2>" in response.data


def test_tutor_profile_failure(client):
    """
    Test that tutor profile pages should not exist for tutor IDs not in the database.
    """
    # Since the IDs are auto-incremented starting from 1, this should give a non-existant ID
    invalid_id = len(Tutor.query.all()) + 1
    response = client.get(f"/tutor-{invalid_id}-profile")
    # Page not found error should occur
    assert response.status_code == 404


def test_tutor_login_get(client):
    """
    Test that Tutor Login page returns an ok response when retrieved,
    and that the page contains the expected form element for inputting data
    and a button element to post the data.
    This ensures the correct html template is being used.
    """
    response = client.get("/tutor-login")
    assert response.status_code == 200
    assert b'<form id="tutor-login-form">' in response.data
    assert b'<button type="submit">Login</button>' in response.data


def test_current_user_session_state(client):
    """
    Test that the session states are not being set or modified
    when making get requests to various pages.
    Should only be set when a requests succeeds for logging in and out.
    """
    response = client.get("/")
    assert "current_user_id" not in session
    assert "current_user_type" not in session
    response = client.get("/tutor-login")
    assert "current_user_id" not in session
    assert "current_user_type" not in session
    response = client.get("/tutor-signup")
    assert "current_user_id" not in session
    assert "current_user_type" not in session
    response = client.get("/browse_tutors")
    assert "current_user_id" not in session
    assert "current_user_type" not in session


def test_tutor_login_post_success(client):
    """
    Test that a post request made to login as a tutor can be sent successfully,
    and that the session's current user ID and type are set correctly.
    Test also that the correct message is sent right before
    the page redirects to the tutor account page.
    """
    response = client.post(
        "/tutor-login",
        data={
            "email": "john.doe@tutorplanet.co.uk",
            "password": "password",
        },
    )
    assert response.status_code == 200
    assert session["current_user_id"] == 1
    assert session["current_user_type"] == "Tutor"
    assert response.json["message"] == "Successful login"


def test_tutor_login_post_failure(client):
    """
    Test that trying to login as a tutor with either the wrong credentials
    will set the curent user session states to None,
    and will return the appropriate error message to the user on the page.
    """
    invalid_password = "123"
    response = client.post(
        "/tutor-login",
        data={
            "email": "john.doe@tutorplanet.co.uk",
            "password": invalid_password,
        },
    )
    assert response.status_code == 200
    assert session["current_user_id"] is None
    assert session["current_user_type"] is None
    assert (
        response.json["message"] == "Login failed. Please check the email and password."
    )

    invalid_email = "123@tutorplanet.org"
    response = client.post(
        "/tutor-login",
        data={
            "email": invalid_email,
            "password": "password",
        },
    )
    assert response.status_code == 200
    assert session["current_user_id"] is None
    assert session["current_user_type"] is None
    assert (
        response.json["message"] == "Login failed. Please check the email and password."
    )


def test_tutor_account_success(client):
    """
    Test that logging in as a tutor enables access
    to your tutor account based on ID.
    """
    # Successfully log in as a tutor
    response = client.post(
        "/tutor-login",
        data={
            "email": "john.doe@tutorplanet.co.uk",
            "password": "password",
        },
    )
    assert response.status_code == 200
    # Successfully access the unique tutor account page
    tutor_id = Tutor.query.filter_by(email="john.doe@tutorplanet.co.uk")[0].tutor_id
    response = client.get(f"/tutor-{tutor_id}-account")
    assert response.status_code == 200
    assert b"your tutor account</h2>" in response.data


def test_tutor_account_failure_as_another_tutor(client):
    """
    Test that logging in as a tutor prevents access
    to other tutors' account pages based on ID.
    """
    # Successfully log in as a tutor
    response = client.post(
        "/tutor-login",
        data={
            "email": "john.doe@tutorplanet.co.uk",
            "password": "password",
        },
    )
    assert response.status_code == 200
    # Fail to access another tutor's account page
    tutor_id = Tutor.query.filter_by(email="jane.smith@tutorplanet.co.uk")[0].tutor_id
    response = client.get(f"/tutor-{tutor_id}-account")
    assert response.status_code == 200
    assert (
        b"<p>Sorry, you do not have permission to access this page. Please log in.</p>"
        in response.data
    )


def test_tutor_account_failure_not_logged_in(client):
    """
    Test that not being logged in prevents access to any tutors' account pages.
    """
    # Access the tutor login page to allow access to the session
    response = client.get("/tutor-login")
    assert response.status_code == 200
    # Assert that the user is not logged in
    if "current_user_id" not in session:
        assert "current_user_id" not in session
    else:
        assert session["current_user_id"] is None

    # Fail to access any tutor account pages
    tutor_id = Tutor.query.filter_by(email="jane.smith@tutorplanet.co.uk")[0].tutor_id
    response = client.get(f"/tutor-{tutor_id}-account")
    assert response.status_code == 200
    assert (
        b"<p>Sorry, you do not have permission to access this page. Please log in.</p>"
        in response.data
    )

    tutor_id = Tutor.query.filter_by(email="john.doe@tutorplanet.co.uk")[0].tutor_id
    response = client.get(f"/tutor-{tutor_id}-account")
    assert response.status_code == 200
    assert (
        b"<p>Sorry, you do not have permission to access this page. Please log in.</p>"
        in response.data
    )
