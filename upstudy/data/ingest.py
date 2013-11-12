import json
import csv
from upstudy.data.models import User, Document, Interest

SURVEY_SCORE_QUESTION = "How would you describe your interest in online content related to [url(\"{0}\")]?"

def process_payload(payload):
    # find if this user's payload is unique
    print payload

def process_survey(survey):
    data = {}

    data["scores"] = {}
    interest = json.loads(survey["interests"])
    for key, name in interest.iteritems():
        score = int(survey[SURVEY_SCORE_QUESTION.format(key)])
        data["scores"][name] = score

    data["downloadSource"] = survey["downloadSource"]
    print data

### File inputs

def ingest_payloads(filename):
    with open(filename, "r") as infile:
        for line in infile:
            payload = json.loads(line)
            process_payload(payload)

def ingest_surveys(filename):
    with open(filename, "r") as infile:
        survey_reader = csv.DictReader(infile)
        for survey in survey_reader:
            process_survey(survey)
