import sys
import json
import csv
from time import mktime
from datetime import datetime, date
import logging
import re
logger = logging.getLogger("upstudy")
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARN)
from IPython import embed

from upstudy.rankers import DayCount, VisitCount, IGNORED_INTERESTS
from upstudy.data.backends import SQLBackend
from upstudy.data.models import Category, User, Submission, SubmissionInterest
from sqlalchemy.sql import exists
from dateutil.parser import parse

import numpy as np

VERSION_IGNORE = set(["1", "1+"])
TOP_5_QUESTIONS = ["[url(\"interest{0}\")]:top_5'".format(i) for i in range(1,16)]
ADDITIONAL_QUESTIONS = ["[url(\"interest{0}\")]:additional_interests'".format(i) for i in range(2,31)]

TZ_PATTERN = re.compile(r"([^()]*)( +\(.*\))?")

def ingest_payload(payload, session, stats):
    nanoseconds, document = payload
    received_at = datetime.fromtimestamp(nanoseconds/1000)

    version = document["version"]
    uuid = document["uuid"]
    user = User.get_or_create(session, uuid)

    version_set = stats["users_per_versions"].get(version, set())
    version_set.add(user.id)
    stats["users_per_versions"][version] = version_set
    stats["num_docs"] += 1
    sys.stdout.write("processing doc: {0}\r".format(stats["num_docs"]))
    sys.stdout.flush()

    ignored_users = stats.get("ignored_users", set())
    if version in VERSION_IGNORE:
        """
        For now, we ignore any user before version 2
        """
        if user.id not in ignored_users:
            ignored_users.add(user.id)
            stats["ignored_users"] = ignored_users
        return

    if user.id in ignored_users:
        ignored_users.remove(user.id)
        stats["ignored_users"] = ignored_users

    # find if this user's payload is unique
    num_days = len(document["interests"])
    stats["num_data_days"] = stats.get("num_data_days", 0) + num_days
    stats["days_per_user"][user.id] = stats["days_per_user"].get(user.id, 0) + num_days

    locale = document["locale"]
    tld_list = document["tldCounter"]
    source = document["source"]

    # MySQL problem: datetimes with timezones can't be stored
    # We  then convert to UTC, strip the timezone away then save
    payload_dt = datetime.fromtimestamp(mktime(parse(TZ_PATTERN.match(document["payloadDate"]).groups()[0]).timetuple()))
    installed_dt = datetime.fromtimestamp(mktime(parse(TZ_PATTERN.match(document["installDate"]).groups()[0]).timetuple()))
    updated_dt = datetime.fromtimestamp(mktime(parse(TZ_PATTERN.match(document["updateDate"]).groups()[0]).timetuple()))
    prefs = document["prefs"]

    submission = session.query(Submission).filter(
            Submission.user_id == user.id,
            Submission.payload_made_at == payload_dt,
    ).first()

    if not submission:
        submission = Submission(
            user_id = user.id,
            received_at = received_at,
            installed_at = installed_dt,
            payload_made_at = payload_dt,
            updated_at = updated_dt,
            source = source,
            locale = locale,
            addon_version = version,
            tld_counter = json.dumps(tld_list),
            prefs = json.dumps(prefs)
        )
        session.add(submission)

    categories = session.query(Category).all()
    cat_index = {}
    for cat in categories:
        cat_index[cat.name.split('.')[1]] = int(cat.id)

    for day_str, interests in document["interests"].iteritems():
        day = date.fromtimestamp(int(day_str)*24*60*60)
        for type, ns_data in interests.iteritems():
            for namespace, interest_data in interests[type].iteritems():
                for interest, counts in interests[type][namespace].iteritems():
                    if interest not in IGNORED_INTERESTS:
                        submission_interest = session.query(SubmissionInterest).filter(
                            SubmissionInterest.day == day,
                            SubmissionInterest.type_namespace == "{0}.{1}".format(type, namespace),
                            SubmissionInterest.category_id == cat_index[interest],
                            SubmissionInterest.user_id == user.id,
                        ).first()

                        if not submission_interest:
                            session.add(SubmissionInterest(
                                day = day,
                                type_namespace = "{0}.{1}".format(type, namespace),
                                category_id = cat_index[interest],
                                user_id = user.id,
                                host_count = json.dumps(counts),
                                submission_id = submission.id,
                            ))
                        else:
                            stats["duplicate_docs"] += 1
                            logger.info("skipping duplicate")
    session.commit()

    """
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
    """


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
    stats = {
            "days_per_user": {},
            "users_per_versions": {},
            "num_data_days": 0,
            "ignored_users": set(),
            "num_docs": 0,
            "duplicate_docs": 0,
    }
    with open(filename, "r") as infile:
        db = SQLBackend.instance()
        for line in infile:
            payload = json.loads(line)
            ingest_payload(payload, db.session, stats)
        db.session.commit()
    print ""
    return stats

def ingest_surveys(filename):
    with open(filename, "r") as infile:
        survey_reader = csv.DictReader(infile)
        for survey in survey_reader:
            process_survey(survey)
