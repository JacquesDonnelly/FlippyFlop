"""Front end for viewing and testing a sequence of cards"""

import os
import pickle
import random

from flask import Flask, request, redirect, url_for, render_template, flash
from flask_login import LoginManager, current_user, login_user
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from googleapiclient.discovery import build
# TODO: Add flask-login and flask-sqlalchemy reqs


from flippyflop import FlippyFlop
from forms import LoginForm

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a_really_big_secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)


import models
# TODO: Use an init / application factory like miguel
# Import here is required to import the models for Alembic (flask-migrate)

# TODO: Create a config file for the whole app
# TODO: Make file structure of app nice


# TODO: Containerize



@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = models.User.query.filter_by(username=form.username.data).first()
        print(form.username.data)
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('home'))
    return render_template('login.html', title='Sign In', form=form)


# TODO: Implement flask-login and login form 
# - Only Ellie has a user
# - Everything is blocked unless she's logged in
# - Every page redirects to the login page

# TODO: make sure username is case insensitive
# The username in the db currently is 'Ellie' not 'ellie'

credential_path = "./token.pickle"
with open(credential_path, "rb") as token:
    creds = pickle.load(token)

service = build("sheets", "v4", credentials=creds)
spreadsheet_id = "1eZL2eOCFKxGkg7bYaEmp-urWqWBfUNx73n_1oR2RkpM"

ff = FlippyFlop(service=service, spreadsheet_id=spreadsheet_id, throttle_time=0)

# TODO: refactor. Sending the post on the card should not block loading of next card.
# Use async/generator/coroutine to handle sequence of cards and post requests
# It's just a mess in general...

REMAINING = ff.todays_cards()
TERMS = ff.get_terms()


@app.route("/", methods=["GET", "POST"])
def home():
    """view before/after reviewing cards"""
    global TERMS
    global REMAINING
    # TODO: todays_cards queries the terms tab. This happens again in get_terms.
    if request.method == "GET":
        REMAINING = ff.todays_cards()
        TERMS = ff.get_terms()
        print(TERMS)
        return render_template("home.html", remaining=len(REMAINING))
    if request.method == "POST":
        if request.form["action"] == "start":
            next_card = random.choice(REMAINING)
            return redirect(f"/{next_card}")


@app.route("/<card_id>", methods=["GET", "POST"])
def single_card(card_id):
    """view of single card with correct/incorrect buttons"""
    global TERMS
    global REMAINING
    if request.method == "GET":
        term = TERMS.loc[card_id]
        return render_template(
            "card.html",
            remaining_cards=len(REMAINING),
            card_front=term["front"].replace("\n", "<br>"),
            card_back=term["back"].replace("\n", "<br>"),
        )
    if request.method == "POST":
        success = request.form["action"] == "success"
        ff.update_bucket(card_id, success)
        REMAINING.remove(card_id)
        if REMAINING:
            next_card = random.choice(REMAINING)
            return redirect(f"/{next_card}")
        else:
            return redirect("/")
