from flask import Flask, request
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

# TODO: Create home screen that displays before you start looking at 
# cards and then when you have completed them all


@app.route('/<card_id>', methods=["GET", "POST"])
def single_card(card_id):
    if request.method == "GET":
        terms = ff.get_terms()
        term = terms.loc[card_id]
        remaining = len(terms)
        # TODO: refactor render to bottom of function
        return render_template(
            "index.html", 
            remaining_cards=remaining,
            card_front=term["front"],
            card_back=term["back"]
        )
    if request.method == "POST":
        # TODO: Check below works by filling in the cards on sheets 
        success = True if request.form["action"] == "success" else False
        ff.update_bucket(card_id, success)
        remaining_cards = ff.todays_cards()
        next_card = random.choice(remaining_cards)
        terms = ff.get_terms()
        term = terms.loc[next_card]
        import pdb; pdb.set_trace()
        return render_template(
            "index.html", 
            remaining_cards=remaining,
            card_front=term["front"],
            card_back=term["back"]
        )

