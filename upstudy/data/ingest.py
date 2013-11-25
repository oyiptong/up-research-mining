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

from upstudy.rankers import DayCount, VisitCount
from upstudy.data.backends import SQLBackend
from upstudy.data.models import Category, User, Submission, SubmissionInterest
import dateutil.parser
from sqlalchemy.sql import exists
from sqlalchemy.exc import IntegrityError

from pybloom import BloomFilter

VERSION_IGNORE = set(["1", "1+"])
TOP_5_QUESTIONS = ["[url(\"interest{0}\")]:top_5'".format(i) for i in range(1,16)]
ADDITIONAL_QUESTIONS = ["[url(\"interest{0}\")]:additional_interests'".format(i) for i in range(2,31)]

TZ_PATTERN = re.compile(r"([^()]*)( +\(.*\))?")

def ingest_payload(payload, session, stats, interest_filter):
    nanoseconds, document = payload
    received_at = datetime.fromtimestamp(nanoseconds/1000)

    version = document["version"]
    uuid = document["uuid"]
    user = User.get_or_create(session, uuid)
    session.commit()

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
    payload_dt = datetime.fromtimestamp(mktime(dateutil.parser.parse(TZ_PATTERN.match(document["payloadDate"]).groups()[0]).timetuple()))
    installed_dt = datetime.fromtimestamp(mktime(dateutil.parser.parse(TZ_PATTERN.match(document["installDate"]).groups()[0]).timetuple()))
    updated_dt = datetime.fromtimestamp(mktime(dateutil.parser.parse(TZ_PATTERN.match(document["updateDate"]).groups()[0]).timetuple()))
    prefs = document["prefs"]

    try:
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
        session.commit()
    except:
        submission = session.query(Submission).filter(
                Submission.user_id == user.id,
                Submission.payload_made_at == payload_dt,
        ).first()

    categories = Category.get_all(session)
    cat_index = {}
    for cat in categories:
        cat_index[cat.name.split('.')[1]] = int(cat.id)

    for day_str, interests in document["interests"].iteritems():
        day = date.fromtimestamp(int(day_str)*24*60*60)
        for type, ns_data in interests.iteritems():
            for namespace, interest_data in interests[type].iteritems():
                for interest, counts in interests[type][namespace].iteritems():
                    key = "{0}-{1}.{2}-{3}-{4}".format(day, type, namespace, cat_index[interest], user.id)
                    if key not in interest_filter:
                        session.add(SubmissionInterest(
                            day = day,
                            type_namespace = "{0}.{1}".format(type, namespace),
                            category_id = cat_index[interest],
                            user_id = user.id,
                            host_count = json.dumps(counts),
                            submission_id = submission.id,
                        ))
                        interest_filter.add(key)
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

    # user information
    user_id = survey["16: userID"]
    response_id = survey["Response ID"]
    status = survey["Status"]
    #user_agent = survey["User Agent"]
    language = survey["Language"]
    download_source = survey["17: downloadSource"]

    # survey time
    started_datestr = None # used to be available
    started_date = None #started_date = dateutil.parser.parse(started_datestr)
    submission_datestr = survey["Date Submitted"]
    submitted_date = dateutil.parser.parse(submission_datestr)

    # location
    city = survey["City"]
    country = survey["Country"]
    region = survey["Region"]

    # multiple choice questions
    computer_users = survey["28: computer_users"]
    hours_per_day = survey["27: hours_per_day"]
    clear_cookies = survey["29: clear_cookies"]
    likes_personalization = survey["30: likes_personalization"]

    # free-form text entries
    custom_interests = survey["39: custom_interests"]
    desired_websites = survey["31: desired_websites"]
    more_comfortable = survey["32: more_comfortable"]
    other_thoughts = survey["33: other_thoughts"]

    # interests
    very_interested = survey["37: top_5"]
    interested = survey["38: additional_interests"]

    if started_date and submission_date:
        time_taken = submitted_date - started_date
        logger.debug("uuid:{0} took {1} answering the survey".format(user_id, time_taken))


    all_interests = survey["15: interests"]
    score_list = survey["35: scoreList"]
    interest_scores = {}

    #TODO: note when there isn't all_interest or score_list
    if all_interests and score_list:
        ranked_interests = []
        ranked = json.loads(all_interests)
        for i in range(1,31):
            ranked_interests.append(ranked["interest{0}".format(i)])

        scores = map(int, survey["35: scoreList"].split(","))
        for index, interest in enumerate(ranked_interests):
            interest_scores[interest] = scores[index]
    print interest_scores

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
    bloom_filter = BloomFilter(capacity=10000000, error_rate=0.001)
    with open(filename, "r") as infile:
        db = SQLBackend.instance()
        for line in infile:
            payload = json.loads(line)
            ingest_payload(payload, db.session, stats, bloom_filter)
        db.session.commit()
    print ""
    return stats

def ingest_surveys(filename):
    with open(filename, "r") as infile:
        survey_reader = csv.DictReader(infile)
        for survey in survey_reader:
            process_survey(survey)
