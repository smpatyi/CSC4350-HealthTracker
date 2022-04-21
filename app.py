# pylint: disable = missing-class-docstring, missing-function-docstring, missing-module-docstring, no-member

import os
import re
import flask
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
import display
import datetime

app = flask.Flask(__name__)

load_dotenv(find_dotenv())

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
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
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(120), nullable=False)
    calories = db.Column(db.Integer, nullable=True)
    date = db.Column(db.DateTime(timezone=True), default=datetime.datetime.now)

class foods(db.Model):
    """
    table to save foods that users ate
    """

    __tablename__ = "foods"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), nullable=False)
    ate_foods = db.Column(db.String(220), nullable=False)


class Comments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), nullable=False)
    comment = db.Column(db.String(120), nullable=False)


db.create_all()

# welcome page (what user sees when they open app)
@app.route("/")
def index():
    return flask.render_template(
        "welcome.html",
    )


@app.route("/welcome", methods=["GET", "POST"])
def welcome():
    if flask.request.method == "POST":
        if flask.request.form["button"] == "Login":
            return flask.redirect(flask.url_for("user_login"))
        if flask.request.form["button"] == "Sign up":
            return flask.redirect(flask.url_for("signup_form"))


# login page, appears when user tries to log in from the welcome page
@app.route("/user_login")
def user_login():
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
            return flask.redirect("/user_login")
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
                    age = flask.request.form.get("age"),
                    gender = flask.request.form.get("gender")
                )
            )
            db.session.commit()
            flask.flash("Account created. Please login.")
            return flask.redirect("/user_login")


# page to add new data to database
@app.route("/input_data", methods=["GET", "POST"])
@login_required
def input_data():
    if flask.request.method == "POST":
        return flask.render_template("input_data.html")


# page to your health tracker
@app.route("/health_tracker", methods=["GET", "POST"])
@login_required
def health_tracker():
    user = current_user.username

    user_info_firstName = UserInfo.query.filter_by(username=user).first().first_name

    if flask.request.method == "POST":
        return flask.render_template(
            "health_tracker.html",
            first_name=user_info_firstName,
        )


@app.route("/add_new_food", methods=["POST"])
@login_required
def add_new_food():
    """
    function: page after saving the foods you ate
    """
    user = current_user.username
    ate_foods = flask.request.form.get("ate_foods")

    food_info = foods(username=user, ate_foods=ate_foods)
    db.session.add(food_info)
    db.session.commit()

    food = foods.query.filter_by(username=user).all()
    food_list = []
    for i in food:
        food_list.append(i.ate_foods)

    flask.flash("Added!")
    return flask.render_template(
        "health_tracker.html", ate_foods=ate_foods, food_list=food_list
    )


# adds the new data to the database
@app.route("/add_new_data", methods=["POST"])
@login_required
def add_new_data():
    user = current_user.username
    user_info = UserInfo.query.filter_by(username=user).first()

    regex = re.compile("^[0-9]+'[0-9]+$")
    if not regex.match(flask.request.form.get("height")):
        flask.flash("height value not viable")
        return flask.render_template("input_data.html")

    regex = re.compile("^[0-9]+$")
    if not regex.match(flask.request.form.get("weight")):
        flask.flash("weight value not viable")
        return flask.render_template("input_data.html")

    if flask.request.form.get("calories") == "":
        cal = None
    else:
        cal = flask.request.form.get("calories")
    db.session.add(
        UserInfo(
            username=user,
            first_name=user_info.first_name,
            last_name=user_info.last_name,
            height=flask.request.form.get("height"),
            weight=flask.request.form.get("weight"),
            calories = cal,
            gender = user_info.gender,
            age = user_info.age,
        )
    )
    db.session.commit()
    flask.flash("Added!")
    return flask.render_template("input_data.html")


# displays Chat Area page
@app.route("/chatArea", methods=["GET", "POST"])
@login_required
def chatArea():
    if flask.request.method == "POST":
        all_comments = Comments.query.filter_by().all()
        user_comments = Comments.query.filter_by(username=current_user.username).all()
        user_comments_array = []
        for i in user_comments:
            user_comments_array.append(i)
        total_comments = len(all_comments)
    return flask.render_template(
        "chatSection.html",
        all_comments=all_comments,
        total_comments=total_comments,
        user_comments_array=user_comments_array,
    )


# adds user comments to database once HTML form is filled out
@app.route("/add_comment", methods=["POST"])
@login_required
def add_comment():
    user = current_user.username
    comment_input = flask.request.form.get("comment")
    db.session.add(Comments(username=user, comment=comment_input))
    db.session.commit()
    return flask.redirect("/main")


# page user sees when they have been logged into app
@app.route("/main", methods=["GET", "POST"])
@login_required
def main():
    user = current_user.username
    user_info = UserInfo.query.filter_by(username=user).all()
    user_info_firstName = UserInfo.query.filter_by(username=user).first().first_name
    return flask.render_template(
        "index.html",
        BMI=display.bmi_display(user_info),
        weight=display.weight_display(user_info),
        height=display.height_display(user_info),
        calories=display.calorie_display(user_info),
        first_name=user_info_firstName,
    )

@app.route("/estimate_graph", methods=["GET", "POST"])
@login_required
def esti():
    if flask.request.method == 'POST':
        user = current_user.username
        user_info = UserInfo.query.filter_by(username=user).all()
        if flask.request.form.get("calorie_intake") is not None:
            calorie_intake_string = flask.request.form.get("calorie_intake").split(", ")
            regex = re.compile("^[0-9]+$")
            for calories in calorie_intake_string:
                if not regex.match(calories):
                    flask.flash("invalid input")
                    return flask.render_template("estimate_graph.html")
            calorie_intake = list(map(int, flask.request.form.get("calorie_intake").split(", ")))
            esti, esti_weight = display.estimate_BMI(user_info, calorie_intake)
        return flask.render_template(
            "estimate_graph.html",
            esti=esti,
            esti_weight=esti_weight,
        )
    else:
        return flask.render_template("estimate_graph.html")


# handles logic to log user out of app
@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    return flask.redirect("/")


if __name__ == "__main__":
    app.run(
        host=os.getenv("IP", "0.0.0.0"), port=int(os.getenv("PORT", 8080)), debug=True
    )
