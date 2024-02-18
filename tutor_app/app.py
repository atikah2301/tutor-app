import logging

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

LOG_PATH = "app.log"
logging.basicConfig(
    level=logging.INFO,
    filename=LOG_PATH,
    filemode="a",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

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


def seed_database():
    # Delete and recreate all the tables
    db.drop_all()
    db.create_all()

    seed_data = [
        ["1234", "John Doe", "john.doe@tutorplanet.co.uk"],
        ["1245", "Jane Smith", "jane.smith@tutorplanet.co.uk"],
    ]
    for row in seed_data:
        tutor = Tutor(tutor_id=int(row[0]), name=row[1], email=row[2])
        logging.info(f"Seed data {tutor} added")
        db.session.add(tutor)
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
    seed_database()

if __name__ == "__main__":
    logging.info("Running flask app...")
    app.run(debug=False)
