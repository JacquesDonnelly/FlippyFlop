import requests
import pdftotext
import re
import json
from collections import defaultdict


def download_pdf(set_id, destination_dir="./downloads"):

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1)"
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"
        )
    }

    url = (
        "https://quizlet.com/pdfs?"
        f"setIds={set_id}"
        "&settings=paper%3Dindex%26type%3Dflash%2"
        "6duplex%3D0%26flip%3D0%26selectedOnly"
        "%3D0%26showImages%3D1%26size%3Dindex%26engine%3Dchrome_devtools"
        "&version=-9999"
    )
    print(url)
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    with open(f"{destination_dir}/{set_id}.pdf", "wb") as file:
        file.write(response.content)


def open_pdf(filepath):
    with open(filepath, "rb") as f:
        pdf = pdftotext.PDF(f)

    return pdf


def parse_pdf(pdf):
    output = defaultdict(dict)
    page_number = 1
    side = 0
    side_mapping = {0: "a", 1: "b"}
    for page in pdf:
        card = page.replace("\n", " ")
        card = re.sub("\s{2,}", " ", card).strip()
        suffix = f"{int(page_number)}{side_mapping[side]}"
        groups = re.search(f"(.*) ({suffix})$", card)
        output[int(page_number)][side_mapping[side]] = groups.group(1)
        page_number += 0.5
        side = (side + 1) % 2

    return output


def write_json(parsed_pdf, write_path):
    with open(write_path, "w") as outfile:
        json.dump(dict(parsed_pdf), outfile)

    print(json.dumps(parsed_pdf))


if __name__ == "__main__":
    set_id = 513457065
    download_pdf(set_id)
    read_path = f"./downloads/{set_id}.pdf"
    write_path = f"./downloads/{set_id}.json"
    pdf = open_pdf(read_path)
    parsed_pdf = parse_pdf(pdf)
    write_json(parsed_pdf, write_path)
