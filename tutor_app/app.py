import logging

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

logging.basicConfig(level=logging.INFO)

DATABASE_URL = "sqlite:///database.db"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

db = SQLAlchemy(app)


class Tutor(db.Model):
    tutor_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)

    def __repr__(self):
        return "<Tutor %r>" % self.tutor_id


def initialise_database():
    db.drop_all()
    db.create_all()  # Recreate all the tables
    tutor_1 = Tutor(tutor_id=1234, name="John Doe", email="john.doe@tutorplanet.co.uk")
    db.session.add(tutor_1)
    db.session.commit()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/browse-tutors")
def browse_tutors():
    session = Session()
    tutors = Tutor.query.all()
    session.close()

    return render_template("browse-tutors.html", tutors=tutors)


@app.route("/tutor-<int:tutor_id>-profile")
def tutor_profile(tutor_id):
    tutor = Tutor.query.get_or_404(tutor_id)
    return render_template("tutor-profile.html", tutor=tutor)


with app.app_context():
    initialise_database()


if __name__ == "__main__":
    app.run(debug=True)
    logging.info("Running flask app...")
