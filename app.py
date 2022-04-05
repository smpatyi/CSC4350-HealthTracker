import flask
import os
from flask_login import (
    LoginManager,
    UserMixin,
    login_required,
    login_user,
    logout_user,
    current_user,
)
from dotenv import find_dotenv, load_dotenv
from flask_sqlalchemy import SQLAlchemy

app = flask.Flask(__name__)

load_dotenv(find_dotenv())

app.config["SECRET_KEY"] = os.getenv("app.secret_key")
# Point SQLAlchemy to your Heroku database
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
# Gets rid of a warning
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# loop in order to change the config variables for the heroku app to access the database
if app.config["SQLALCHEMY_DATABASE_URI"].startswith("postgres://"):
    app.config["SQLALCHEMY_DATABASE_URI"] = app.config[
        "SQLALCHEMY_DATABASE_URI"
    ].replace("postgres://", "postgresql://")

db = SQLAlchemy(app)

# using flask login in order to manage the users logging in to the site
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "index"


class UserLogin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return "<User %r>" % self.username

    def get_username(self):
        return self.username


@login_manager.user_loader
def load_user(user_id):
    return UserLogin.query.get(int(user_id))


class UserInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), nullable=False)
    first_name = db.Column(db.String(120), nullable=False)
    last_name = db.Column(db.String(120), nullable=False)
    height = db.Column(db.String(120), nullable=False)
    weight = db.Column(db.Integer, nullable=False)


db.create_all()


@app.route("/")
def index():
    return flask.render_template(
        "login.html",
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    if flask.request.method == "POST":
        login_username = flask.request.form.get("username")
        login_password = flask.request.form.get("password")
        user = (
            UserLogin.query.filter_by(username=login_username).first()
            and UserLogin.query.filter_by(password=login_password).first()
        )
        if user:
            login_user(user)
            return flask.redirect("/main")
        else:
            flask.flash("No account found with that username. Please sign up!")
            return flask.redirect("/signup_form")


@app.route("/signup_form")  # Displays sign up page
def signup_form():
    return flask.render_template(
        "signup.html",
    )


@app.route("/signup", methods=["GET", "POST"])  # Handles user input for sign up page
def signup():
    if flask.request.method == "POST":
        username_input = flask.request.form.get("username")
        if UserLogin.query.filter_by(username=username_input).first():
            flask.flash(
                "Account already exists with this username. Please login or choose a different username."
            )
            return flask.redirect("/")
        else:
            password_input = flask.request.form.get("password")
            db.session.add(UserLogin(username=username_input, password=zzzzzz))
            db.session.add(
                UserInfo(
                    username=username_input,
                    first_name=flask.request.form.get("first_name"),
                    last_name=flask.request.form.get("last_name"),
                    height=flask.request.form.get("height"),
                    weight=flask.request.form.get("weight"),
                )
            )
            db.session.commit()
            flask.flash("Account created. Please login!")
            return flask.redirect("/")


@app.route("/main", methods=["GET", "POST"])
@login_required
def main():
    return flask.render_template("index.html")


@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    return flask.redirect("/")


app.run(host=os.getenv("IP", "0.0.0.0"), port=int(os.getenv("PORT", 8080)), debug=True)
