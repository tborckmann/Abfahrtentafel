import flask

app = flask.Flask(__name__)

@app.route('/')
def home():
    return render_template('setup.html')

def start():
    app.run("0.0.0.0", port=8080)
    