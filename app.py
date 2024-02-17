from flask import Flask, render_template
import logging

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/browse-tutors')
def tutors():
    return render_template('browse-tutors.html')

if __name__ == '__main__':
    app.run(debug=True)
    logging.info("Running flask app...")