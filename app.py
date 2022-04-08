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
from passlib.hash import sha256_crypt
import re
import display

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

# login page (what user sees when they open app)
@app.route("/")
def index():
    return flask.render_template(
        "login.html",
    )


# handles login logic to log user into app
@app.route("/login", methods=["GET", "POST"])
def login():
    if flask.request.method == "POST":
        login_username = flask.request.form.get("username")
        user = UserLogin.query.filter_by(username=login_username).first()
        if user:
            if sha256_crypt.verify(
                flask.request.form.get("password"),
                UserLogin.query.filter_by(username=flask.request.form.get("username"))
                .first()
                .password,
            ):
                login_user(user)
                return flask.redirect("/main")
            else:
                flask.flash("No account found with that username. Please sign up.")
                return flask.redirect("/signup_form")
        else:
            flask.flash("No account found with that username. Please sign up.")
            return flask.redirect("/signup_form")


# register page
@app.route("/signup_form")  # Displays sign up page
def signup_form():
    return flask.render_template(
        "signup.html",
    )


# handles signup logic to create an account for user
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
            password_encrypted = sha256_crypt.encrypt(password_input)
            db.session.add(
                UserLogin(username=username_input, password=password_encrypted)
            )
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
            flask.flash("Account created. Please login.")
            return flask.redirect("/")

# page to add new data to database
@app.route("/input_data", methods=["GET", "POST"])
@login_required
def input_data():
    return flask.render_template("input_data.html")

# adds the new data to the database
@app.route("/add_new_data", methods=["POST"])
@login_required
def add_new_data():
    user = current_user.username
    user_info = UserInfo.query.filter_by(username=user).first()

    regex = re.compile("^[0-9]+\'[0-9]+\'\'$")
    if not regex.match(flask.request.form.get("height")):
        flask.flash("height value not viable")
        return flask.render_template("input_data.html")

    regex = re.compile("^[0-9]+$")
    if not regex.match(flask.request.form.get("weight")):
        flask.flash("weight value not viable")
        return flask.render_template("input_data.html")
    
    db.session.add(
        UserInfo(
            username=user,
            first_name=user_info.first_name,
            last_name=user_info.last_name,
            height=flask.request.form.get("height"),
            weight=flask.request.form.get("weight"),
        )
    )
    db.session.commit()
    flask.flash("Added!")
    return flask.render_template("input_data.html")

# page user sees when they have been logged into app
@app.route("/main", methods=["GET", "POST"])
@login_required
def main():
    user = current_user.username
    user_info = UserInfo.query.filter_by(username=user).all()
    return flask.render_template(
        "index.html",
        BMI = display.bmi_display(user_info),
        weight = display.weight_display(user_info),
        height = display.height_display(user_info)
        )


# handles logic to log user out of app
@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    return flask.redirect("/")


app.run(host=os.getenv("IP", "0.0.0.0"), port=int(os.getenv("PORT", 8080)), debug=True)
