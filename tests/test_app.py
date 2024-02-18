import pytest

from tutor_app.app import Tutor
from tutor_app.app import app as flask_app
from tutor_app.app import db


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
    tutors = Tutor.query.all()
    assert len(tutors) == 2
    assert all([isinstance(tutor, Tutor) for tutor in tutors])
    assert Tutor.query.filter_by(name="John Doe").first() is not None
    assert Tutor.query.filter_by(name="Jane Smith").first() is not None


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


def test_tutor_signup_post_failure(client):
    existing_users_name = "John Doe"
    new_users_name = "Johnny Doe"

    response = client.post(
        "/tutor-signup",
        data={
            "name": new_users_name,
            "email": "john.doe@tutorplanet.co.uk",
            "password": "my_password",
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
