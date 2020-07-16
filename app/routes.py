import random

from flask import redirect, request, flash, render_template, url_for
from flask_login import current_user, login_user, login_required
from sqlalchemy import func

from app import models, app
from app.base import HeaderLinkState
from app.insults import insult_generator
from app.service import ff, REMAINING, TERMS

# TODO: Create derrivative of render_template to better handle base requirements.
# For example, every render template requires a HeaderLinkState
# There may be a nice way of automating this when registering route with decorator

# TODO: refactor / and /<card_id> to be more supportive of multiple users
# Use daemon thread to execute the ff.update_bucket request
# Use cookies to store cards still to do today
# Only hit ff.get_terms once on / route, then store in db rather than global
# Also should the get_terms and get_buckets on / route be blocking?
# ALTERNATIVE: We want to add some reporting. Maybe implement rq with db like miguel?

# TODO: Use url_for everywhere

def generate_remaining_cards_phrase(num_remaining_cards):
    single_card = num_remaining_cards == 1
    if single_card:
        noun = "Card"
    else:
        noun = "Cards"
    return f"{num_remaining_cards} {noun} Remaining"


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


