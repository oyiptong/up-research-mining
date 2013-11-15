import json
import csv
import dateutil.parser
import logging
logger = logging.getLogger("upstudy")
from IPython import embed

from upstudy.rankers import DayCount, VisitCount

TOP_5_QUESTIONS = ["[url(\"interest{0}\")]:top_5'".format(i) for i in range(1,16)]
ADDITIONAL_QUESTIONS = ["[url(\"interest{0}\")]:additional_interests'".format(i) for i in range(2,31)]

def process_payload(payload):
    # find if this user's payload is unique
    document, timestamp = payload

    uuid = document["uuid"]
    locale = document["locale"]
    tld_list = document["tldCounter"]
    source = document["source"]
    version = document["version"]

    install_date = document["installDate"]
    update_date = document["updateDate"]
    prefs = document["prefs"]

    rankers = [DayCount(uuid), VisitCount(uuid)]
    rankings = []
    for ranker in rankers:
        ranker.consume(document["interests"])
        ranking = ranker.get_rankings()
        rankings.append(ranking)
    
    print "daycount_edrules_rules\t\t\tvisitcount_edrules_rules"
    for i in range(len(rankings[0]['rules']['edrules'])):
        print "{0}\t\t\t{1}".format(
                rankings[0]['combined']['edrules'][i],
                rankings[1]['combined']['edrules'][i])

    embed()

def process_survey(survey):
    data = {}

    user_id = survey["userID"]
    download_source = survey["downloadSource"]
    response_id = survey["Response ID"]
    status = survey["Status"]
    user_agent = survey["User Agent"]

    # warming up questions
    computer_users = survey["computer_users"]
    hours_per_day = survey["hours_per_day"]
    clear_cookies = survey["clear_cookies"]

    # survey gizmo data
    city = survey["City"]
    country = survey["Country"]
    region = survey["Region"]
    comments = survey["Comments"]

    # other data
    custom_interests = survey["custom_interests"]
    desired_websites = survey["desired_websites"]
    likes_personalization = survey["likes_personalization"]
    more_comfortable = survey["more_comfortable"]
    other_thoughts = survey["other_thoughts"]

    # survey time
    started_date = survey["Time Started"]
    submission_date = survey["Date Submitted"]

    if started_date and submission_date:
        started = dateutil.parser.parse(started_date)
        submitted = datetutil.parser.parse(submission_date)
        time_taken = submitted - started
        logger.debug("uuid:{0} took {1} answering the survey".format(user_id, time_taken))

    ranked_interests = []
    if survey["interests"]:
        ranked = json.loads(txt_ranked_interests)
        for i in range(1,31):
            ranked_interests.append(ranked["interest{0}".format(i)])

    scores = survey["scoreList"]
    if survey["scoreList"]:
        scores = [int(s) for s in survey["scoreList"].split(",")]
        for index, score in scores:
            pass

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
