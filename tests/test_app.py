import pytest

from tutor_app.app import Tutor, seed_database
from tutor_app.app import app as flask_app
from tutor_app.app import db


@pytest.fixture()
def app():
    flask_app.config.update(
        {
            "TESTING": True,
        }
    )
    yield flask_app


@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        with flask_app.app_context():
            seed_database()
        yield client
        with flask_app.app_context():
            db.drop_all()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


def test_homepage(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"<h1>Tutor Planet</h1>" in response.data
    assert b"<h2>Welcome to Tutor Planet!</h2>" in response.data


def test_browse_tutors(client):
    response = client.get("/browse-tutors")
    assert response.status_code == 200


def test_tutor_signup_get(client):
    response = client.get("/tutor-signup")
    assert b'<form id="tutor-signup-form">' in response.data
    assert b'<button type="submit">Sign Up</button>' in response.data
    assert response.status_code == 200


def test_tutor_signup_post_success(client):
    response = client.post(
        "/tutor-signup",
        data={
            "name": "Samantha Doe",
            "email": "samantha@example.com",
            "password": "my_password",
        },
    )
    assert response.status_code == 200
    assert Tutor.query.filter_by(name="Samantha Doe").first() is not None
    assert response.json["message"] == "You've successfully signed up as a tutor!"


def test_tutor_signup_post_failure_incomplete_form(client):
    response = client.post(
        "/tutor-signup",
        data={
            "email": "samantha@example.com",
            "password": "my_password",
        },
        # Note that in practice the html is smart enough to not allow you to submit the form 
        # without completing all the sections
    )
    assert response.status_code == 400
    assert Tutor.query.filter_by(email="samantha@example.com").first() is None
    assert response.json is None


def test_tutor_signup_post_failure_email_taken(client):
    response = client.post(
        "/tutor-signup",
        data={
            "Johnny Doe"
            "email": "john.doe@tutorplanet.com",
            "password": "my_password",
        },
    )
    assert response.status_code == 400
    assert Tutor.query.filter_by(email="john.doe@tutorplanet.com").first() is None
    assert response.json is None
