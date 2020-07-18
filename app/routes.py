import random

from flask import redirect, request, flash, render_template, url_for, make_response
from flask_login import current_user, login_user, login_required
from sqlalchemy import func

from app import models, app
from app.base import HeaderLinkState
from app.insults import insult_generator
from app.service import ff, RemainingCards, TermService
from app.models import Card

# TODO: Create derrivative of render_template to better handle base requirements.
# For example, every render template requires a HeaderLinkState
# There may be a nice way of automating this when registering route with decorator
# This will also help with breaking down the content in each route

# TODO: refactor / and /<card_id> to be more supportive of multiple users
# Use daemon thread to execute the ff.update_bucket request
# Also should the get_terms and get_buckets on / route be blocking?
# ALTERNATIVE: We want to add some reporting. Maybe implement rq with db like miguel?

# TODO: Use url_for everywhere in the app


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
    # TODO: todays_cards queries the terms tab. This happens again in get_terms.
    if request.method == "GET":
        remaining_cards = RemainingCards(service=ff)
        ts = TermService(model=Card, service=ff)
        ts.fill_database()
        phrase = generate_remaining_cards_phrase(len(remaining_cards))
        header_link_state = HeaderLinkState(page="review")
        resp = make_response(
            render_template(
                "home.html",
                remaining_cards_phrase=phrase,
                remaining=len(remaining_cards),
                footer=" ",
                header_link_state=header_link_state,
            )
        )
        resp.set_cookie("cards", str(remaining_cards))
        return resp
    if request.method == "POST":
        if request.form["action"] == "start":
            remaining_cards_cookie = request.cookies.get("cards")
            remaining_cards = RemainingCards(string=remaining_cards_cookie)
            next_card = remaining_cards.pop()
            resp = make_response(redirect(f"/{next_card}"))
            resp.set_cookie("cards", str(remaining_cards))
            return resp


@app.route("/<card_id>", methods=["GET", "POST"])
@login_required
def single_card(card_id):
    """view of single card with correct/incorrect buttons"""
    ts = TermService(model=Card, service=ff)
    remaining_cards_cookie = request.cookies.get("cards")
    remaining_cards = RemainingCards(string=remaining_cards_cookie)
    if request.method == "GET":
        term = ts.card_by_id(card_id)
        header_link_state = HeaderLinkState(page="review")
        return render_template(
            "card.html",
            front=term.front.replace("\n", "<br>"),
            back=term.back.replace("\n", "<br>"),
            footer=generate_remaining_cards_phrase(len(remaining_cards)),
            header_link_state=header_link_state,
        )
    if request.method == "POST":
        success = request.form["action"] == "success"
        ff.update_bucket(card_id, success)
        if remaining_cards:
            next_card = remaining_cards.pop()
            resp = make_response(redirect(f"/{next_card}"))
            resp.set_cookie("cards", str(remaining_cards))
            return resp
        else:
            return redirect("/")


@app.route("/cards")
@login_required
def cards():
    header_link_state = HeaderLinkState(page="cards")
    return render_template(
        "coming_soon.html", header_link_state=header_link_state, footer=" "
    )


@app.route("/stats")
@login_required
def stats():
    header_link_state = HeaderLinkState(page="stats")
    return render_template(
        "coming_soon.html", header_link_state=header_link_state, footer=" "
    )


@app.route("/settings")
@login_required
def settings():
    header_link_state = HeaderLinkState(page="settings")
    return render_template(
        "coming_soon.html", header_link_state=header_link_state, footer=" "
    )
