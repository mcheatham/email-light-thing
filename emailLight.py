#!/usr/local/bin/python3
import pickle
import os.path
import base64
import string
import re
import json
import urllib.request
from datetime import datetime

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

lightURL = "http://homeassistant.local:5050/api/appdaemon/lights"

# If modifying these scopes, delete the file token.pickle.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

# The directory this script is in
script_dir = os.path.dirname(os.path.realpath(__file__))


def default_update_light(red, blue, brightness):
    print("red: ", red, "  blue: ", blue, "  brightness: ", brightness)
    newConditions = {
        "command": "set",
        "state": "on",
        "light": "glow_ball",
        "rgb_color": [red, 0, blue],
        "brightness": brightness,
    }
    params = json.dumps(newConditions).encode("utf8")
    req = urllib.request.Request(
        lightURL, data=params, headers={"content-type": "application/json"}
    )
    response = urllib.request.urlopen(req)


def main(update_light=default_update_light):
    annoyance_limit = 10

    # read list of bad words from file into a list
    badwords_file = os.path.join(script_dir, "badwords.txt")
    with open(badwords_file) as f:
        bad_words = f.read().splitlines()
    f.close()

    # begin Google API's quickstart code for Python
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    token_file = os.path.join(script_dir, "token.pickle")
    if os.path.exists(token_file):
        with open(token_file, "rb") as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            credentials_file = os.path.join(script_dir, "credentials.json")
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_file, "wb") as token:
            pickle.dump(creds, token)

    service = build("gmail", "v1", credentials=creds)

    results = service.users().messages().list(userId="me", labelIds="INBOX").execute()
    messages = results.get("messages", [])
    # end of Google's quickstart code

    num_bad_emails = 0

    for msg in messages:
        bad_aspects = 0
        email = service.users().messages().get(userId="me", id=msg["id"]).execute()
        email_elements = email["payload"]["headers"]
        for email_element in email_elements:
            if email_element["name"] == "To":
                if (
                    "michelle.cheatham@wright.edu" in email_element["value"]
                    and email_element["value"].count("@wright.edu") < 2
                ):
                    bad_aspects += 1
            if email_element["name"] == "From":
                studentEmailRegEx = "[a-zA-Z]*[.][0-9]+@wright.edu"
                if re.search(studentEmailRegEx, email_element["value"]):
                    bad_aspects += 1
            if email_element["name"] == "Subject":
                text = (email_element["value"] + " " + email["snippet"]).lower()
                text = text.translate(str.maketrans("", "", string.punctuation))
                bad_word_count = 0
                for bad_word in bad_words:
                    if (" " + bad_word + " ") in text:
                        bad_word_count += 1
                if bad_word_count > 2:
                    bad_aspects += 1
        if bad_aspects >= 2:
            num_bad_emails += 1

    print(f"Checking at {datetime.now()}")
    print("num bad emails: ", num_bad_emails)

    modifier = round(255.0 / annoyance_limit)
    brightness = round(min(255, num_bad_emails * modifier))
    red = round(min(255, num_bad_emails * modifier))
    if num_bad_emails > annoyance_limit:
        blue = 255
    else:
        blue = round(min(255, (annoyance_limit - num_bad_emails) * modifier))

    update_light(red, blue, brightness)
    print()


if __name__ == "__main__":
    main()
