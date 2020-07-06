from flask import Flask, request, redirect
from flask import render_template
from googleapiclient.discovery import build
from flippyflop import FlippyFlop
import pickle
import random

app = Flask(__name__)


credential_path = "./token.pickle"
with open(credential_path, "rb") as token:
    creds = pickle.load(token)

service = build("sheets", "v4", credentials=creds)
spreadsheet_id = "1UDLGeqhVxfHJF5zk2EWRnWuQrZLQkCbwdg9loyd1nFg"

ff = FlippyFlop(service=service, spreadsheet_id=spreadsheet_id, throttle_time=0)

# TODO: refactor. Sending the post on the card should not block loading of next card.
# Use async/generator/coroutine to handle sequence of cards and post requests

REMAINING = None
TERMS = None


@app.route("/", methods=["GET", "POST"])
def home():
    global TERMS
    global REMAINING
    # TODO: todays_cards queries the terms tab. This happens again in get_terms.
    if request.method == "GET":
        REMAINING = ff.todays_cards()
        TERMS = ff.get_terms()
        return render_template("home.html", remaining=len(REMAINING))
    if request.method == "POST":
        if request.form["action"] == "start":
            next_card = random.choice(REMAINING)
            return redirect(f"/{next_card}")


@app.route("/<card_id>", methods=["GET", "POST"])
def single_card(card_id):
    global TERMS
    global REMAINING
    if request.method == "GET":
        term = TERMS.loc[card_id]
        # TODO: rename index.html
        return render_template(
            "index.html",
            remaining_cards=len(REMAINING),
            card_front=term["front"],
            card_back=term["back"],
        )
    if request.method == "POST":
        success = True if request.form["action"] == "success" else False
        ff.update_bucket(card_id, success)
        REMAINING.remove(card_id)
        if REMAINING:
            next_card = random.choice(REMAINING)
            return redirect(f"/{next_card}")
        else:
            return redirect("/")
