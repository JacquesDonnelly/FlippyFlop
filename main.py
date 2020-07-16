"""Front end for viewing and testing a sequence of cards"""

import datetime
import os
import pickle
import random

from flask import Flask, request, redirect, url_for, render_template, flash
from flask_login import LoginManager, current_user, login_user, login_required
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from googleapiclient.discovery import build
from sqlalchemy import func

from insults import insult_generator
from flippyflop import FlippyFlop

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config["SECRET_KEY"] = "a_really_big_secret"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "app.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = "login"

import models

# TODO BNPR: Add deployment details to README

# TODO BNPR: Use an init / app factory + routes like miguel
# Import here is required to import the models for Alembic (flask-migrate)

# TODO BNPR: Create a config file for the whole app
# TODO BNPR: Make file structure of app nice


class HeaderLinkState:
    def __init__(self, page):
        self.page = page
        self.review = ""
        self.cards = ""
        self.stats = ""
        self.settings = ""
        self.set_corresponding_page_to_active()

    def set_corresponding_page_to_active(self):
        if self.page:
            setattr(self, self.page, "active")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    if request.method == "POST":
        user = models.User.query.filter(
            func.lower(models.User.username) == func.lower(request.form.get("username"))
        ).first()
        if user is None or not user.check_password(request.form.get("password")):
            flash("failed_login")
            return redirect(url_for("login"))
        login_user(user, remember=False)
        return redirect(url_for("home"))
    header_link_state = HeaderLinkState(page=None)
    return render_template(
        "login.html",
        title="Sign In",
        insult=insult_generator.generate(),
        header_link_state=header_link_state,
    )


credential_path = "./token.pickle"
with open(credential_path, "rb") as token:
    creds = pickle.load(token)

service = build("sheets", "v4", credentials=creds)
spreadsheet_id = "1eZL2eOCFKxGkg7bYaEmp-urWqWBfUNx73n_1oR2RkpM"

ff = FlippyFlop(
    service=service,
    spreadsheet_id=spreadsheet_id,
    day_zero=datetime.datetime(2020, 7, 7),
    throttle_time=0,
)

# TODO: refactor / and /<card_id> to be more supportive of multiple users
# Use daemon thread to execute the ff.update_bucket request
# Use cookies to store cards still to do today
# Only hit ff.get_terms once on / route, then store in db rather than global
# Also should the get_terms and get_buckets on / route be blocking?


# TODO: Fix Accidental Double Clicking Behaviour

REMAINING = ff.todays_cards()
TERMS = ff.get_terms()

# TODO: Add coming soon to each button

# TODO: Use url_for everywhere


def generate_remaining_cards_phrase(num_remaining_cards):
    single_card = num_remaining_cards == 1
    if single_card:
        noun = "Card"
    else:
        noun = "Cards"
    return f"{num_remaining_cards} {noun} Remaining"


@app.route("/", methods=["GET", "POST"])
@login_required
def home():
    """view before/after reviewing cards"""
    global TERMS
    global REMAINING
    # TODO: todays_cards queries the terms tab. This happens again in get_terms.
    if request.method == "GET":
        REMAINING = ff.todays_cards()
        TERMS = ff.get_terms()
        phrase = generate_remaining_cards_phrase(len(REMAINING))
        header_link_state = HeaderLinkState(page="review")
        return render_template(
            "home.html",
            remaining_cards_phrase=phrase,
            remaining=len(REMAINING),
            footer=" ",
            header_link_state=header_link_state
        )
    if request.method == "POST":
        if request.form["action"] == "start":
            next_card = random.choice(REMAINING)
            return redirect(f"/{next_card}")


@app.route("/<card_id>", methods=["GET", "POST"])
@login_required
def single_card(card_id):
    """view of single card with correct/incorrect buttons"""
    global TERMS
    global REMAINING
    if request.method == "GET":
        term = TERMS.loc[card_id]
        header_link_state = HeaderLinkState(page="review")
        return render_template(
            "card.html",
            front=term["front"].replace("\n", "<br>"),
            back=term["back"].replace("\n", "<br>"),
            footer=generate_remaining_cards_phrase(len(REMAINING)),
            header_link_state=header_link_state
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


@app.route("/cards")
@login_required
def cards():
    header_link_state = HeaderLinkState(page="cards")
    return render_template("coming_soon.html", header_link_state=header_link_state, footer=" ")


@app.route("/stats")
@login_required
def stats():
    header_link_state = HeaderLinkState(page="stats")
    return render_template("coming_soon.html", header_link_state=header_link_state, footer=" ")


@app.route("/settings")
@login_required
def settings():
    header_link_state = HeaderLinkState(page="settings")
    return render_template("coming_soon.html",  header_link_state=header_link_state, footer=" ")


