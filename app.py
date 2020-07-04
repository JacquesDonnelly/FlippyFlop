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

ff = FlippyFlop(
    service=service,
    spreadsheet_id=spreadsheet_id
)

# TODO: Speed up usage.Reduce Duplicated calls? Cache some things? Modify/disable throttle?


@app.route("/", methods=["GET", "POST"])
def home():
    remaining_cards = ff.todays_cards()
    if request.method == "GET":
        return render_template("home.html", remaining=len(remaining_cards))
    if request.method == "POST":
        if request.form["action"] == "start":
            next_card = random.choice(remaining_cards)
            return redirect(f"/{next_card}")



@app.route('/<card_id>', methods=["GET", "POST"])
def single_card(card_id):
    if request.method == "GET":
        terms = ff.get_terms()
        term = terms.loc[card_id]
        remaining_cards = ff.todays_cards()
        # TODO: rename index.html
        return render_template(
            "index.html", 
            remaining_cards=len(remaining_cards),
            card_front=term["front"],
            card_back=term["back"]
        )
    if request.method == "POST":
        success = True if request.form["action"] == "success" else False
        ff.update_bucket(card_id, success)
        remaining_cards = ff.todays_cards()
        if remaining_cards:
            next_card = random.choice(remaining_cards)
            return redirect(f"/{next_card}")
        else:
            return redirect("/")

