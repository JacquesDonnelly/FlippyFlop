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


def get_random_card(terms):
    random_idx = random.choice(range(len(terms)))
    term = terms.iloc[random_idx]
    return term["front"], term["back"]


@app.route('/', methods=["GET", "POST"])
def hello_world():
    # if root then redirect to random card
    if request.method == "GET":
        terms = ff.get_terms()
        front, back = get_random_card(terms)
        return render_template(
            "index.html", 
            remaining_cards=len(terms),
            card_front=front,
            card_back=back
        )
    if request.method == "POST":
        # if request.form["action"] == "success" then blah
        # then redirect to next card...
        print(request)
        print(dir(request))
        return "Hello, World!" 

