import logging

from flask import Flask, jsonify, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError

LOG_PATH = "app.log"
logging.basicConfig(
    level=logging.INFO,
    filename=LOG_PATH,
    filemode="a",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

DATABASE_URL = "sqlite:///database.db"
engine = create_engine(DATABASE_URL)

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.secret_key = "my_secret_key"

db = SQLAlchemy(app)


class Tutor(db.Model):
    tutor_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return "<Tutor %r>" % self.tutor_id


@app.route("/")
def index():
    is_logged_in = False
    if "current_user_id" in session:
        if session["current_user_id"] is not None:
            is_logged_in = True

    return render_template("index.html", is_logged_in=is_logged_in)


@app.route("/logout", methods=["POST"])
def logout():
    session.pop("current_user_id", None)
    session.pop("current_user_type", None)
    return jsonify(success=True)


@app.route("/browse-tutors")
def browse_tutors():
    tutors = Tutor.query.all()
    return render_template("browse-tutors.html", tutors=tutors)


@app.route("/tutor-<int:tutor_id>-profile")
def tutor_profile(tutor_id):
    tutor = Tutor.query.get_or_404(tutor_id)
    return render_template("tutor-profile.html", tutor=tutor)


@app.route("/tutor-signup", methods=["GET", "POST"])
def tutor_signup():
    if request.method == "GET":
        return render_template("tutor-signup.html")

    elif request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        try:
            new_tutor = Tutor(name=name, email=email, password=password)
            db.session.add(new_tutor)
            db.session.commit()
            return jsonify(message="You've successfully signed up as a tutor!")

        except IntegrityError as e:
            logging.error(e)
            db.session.rollback()
            return jsonify(
                message="The email you have entered is already in use for an existing tutor account."
            )


@app.route("/tutor-login", methods=["GET", "POST"])
def tutor_login():
    if request.method == "GET":
        return render_template("tutor-login.html")

    elif request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        session["current_user_id"] = None
        session["current_user_type"] = None

        tutor = Tutor.query.filter_by(email=email, password=password).first()
        logging.info(tutor)

        if tutor:
            session["current_user_id"] = tutor.tutor_id
            session["current_user_type"] = "Tutor"
            logging.info("Login details correct")
            logging.info(f"Set the new current_user_id: {session['current_user_id']}")
            return jsonify(message="Successful login", tutor_id=int(tutor.tutor_id))

        else:
            logging.info("Login details incorrect")
            return jsonify(message="Login failed. Please check the email and password.")


@app.route("/tutor-<int:tutor_id>-account")
def tutor_account(tutor_id):
    # current_user_id = session["current_user_id"]
    # current_user_type = session["current_user_type"]
    # logging.info(f"current_user_id={current_user_id}, current_user_type={current_user_type}")

    # tutor = Tutor.query.get_or_404(tutor_id)

    # return render_template("tutor-account.html", tutor=tutor)

    if "current_user_id" not in session:
        session["current_user_id"] = None
        session["current_user_type"] = None

    current_user_id = session["current_user_id"]
    current_user_type = session["current_user_type"]
    logging.info(
        f"current_user_id={current_user_id}, current_user_type={current_user_type}"
    )

    if current_user_id == None:
        # Occurs when the user is not logged in
        return render_template("permission_denied.html")
    elif current_user_type == "Tutor":
        if current_user_id == tutor_id:
            # Occurs when a tutor is accesssing their own account
            tutor = Tutor.query.get_or_404(tutor_id)
            return render_template("tutor-account.html", tutor=tutor)
        else:
            # May occur if a logged in Tutor tries accesssing a different Tutor's account by changing the URL
            return render_template("permission_denied.html")
    else:
        # May occur if a non-Tutor user e.g. and Admin or Parent tries accessing a tutor account
        # This could be changed later as new user types are created
        return render_template("permission_denied.html")


def seed_database():
    # Reset all the tables
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
        logging.info(f"Seed data {tutor} added")


with app.app_context():
    seed_database()


if __name__ == "__main__":
    logging.info("Running flask app...")
    app.run(debug=False)
