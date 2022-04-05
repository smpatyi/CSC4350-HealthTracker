import flask
import os

from flask_login import current_user, login_user, LoginManager, UserMixin
from flask_sqlalchemy import SQLAlchemy

app = flask.Flask(__name__)

# Point SQLAlchemy to your Heroku database
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
# Gets rid of a warning
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# loop in order to change the config variables for the heroku app to access the database
if app.config["SQLALCHEMY_DATABASE_URI"].startswith("postgres://"):
    app.config["SQLALCHEMY_DATABASE_URI"] = app.config[
        "SQLALCHEMY_DATABASE_URI"
    ].replace("postgres://", "postgresql://")

# using flask login in order to manage the users logging in to the site
login_manager = LoginManager()
login_manager.init_app(app)


@app.route("/")
def index():
    return flask.render_template("index.html")


app.run(host=os.getenv("IP", "0.0.0.0"), port=int(os.getenv("PORT", 8080)), debug=True)
