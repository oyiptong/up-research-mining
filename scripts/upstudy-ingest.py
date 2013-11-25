#!/usr/bin/env python
import sys
import os
import argparse
import logging
import json
import time
import math
import numpy as np
import upstudy.data.ingest as ingest
import upstudy.settings
from upstudy.data.backends import SQLBackend
from upstudy.data.models import User

logging.basicConfig(format="%(levelname)s: %(message)s\n")
logger = logging.getLogger("cmd-ingest")
logger.setLevel(logging.INFO)
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARN)

parser = argparse.ArgumentParser(description="Read user research payload and create data directories")
parser.add_argument("-p", "--payloads", metavar="PAYLOADS_FILE", type=str, help="A file containing research addon payloads, one per line, each entry in JSON format")
parser.add_argument("-s", "--surveys", metavar="SURVEYS_FILE", type=str, help="A file containing survey responses, one per line, in CSV format")
parser.add_argument("-v", "--verbose", help="Verbose", action="store_true", default=False)

def percentile(N, percent, key=lambda x:x):
    """
    Find the percentile of a list of values.

    @parameter N - is a list of values. Note N MUST BE already sorted.
    @parameter percent - a float value from 0.0 to 1.0.
    @parameter key - optional key function to compute value from each element of N.

    @return - the percentile of the values
    """
    if not N:
        return None
    k = (len(N)-1) * percent
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return key(N[int(k)])
    d0 = key(N[int(f)]) * (c-k)
    d1 = key(N[int(c)]) * (k-f)
    return d0+d1

def print_payload_stats(stats):
    db = SQLBackend.instance()

    version_dist = {}
    for version, user_set in stats["users_per_versions"].iteritems():
        version_dist[version] = len(user_set)
    print "users per versions: {0}".format(json.dumps(version_dist))
    versions = stats["users_per_versions"].keys()
    ones = stats["users_per_versions"]["1"].union(stats["users_per_versions"]["1+"])
    twos = stats["users_per_versions"]["2"]
    print "num users overlapping in 1's and 2's: {0}".format(len(ones.intersection(twos)))

    user_counts = [count for id, count in stats["days_per_user"].iteritems()]
    user_counts.sort()
    print "25th percentile of history days: {0}".format(percentile(user_counts, 0.25))
    print "median number of history days: {0}".format(percentile(user_counts, 0.5))
    print "75th percentile of history days: {0}".format(percentile(user_counts, 0.75))
    num_users = db.session.query(User).count()
    print "number of users stored: {0}".format(num_users)
    print "ignored users: {0}".format(len(stats["ignored_users"]))

def main():
    start_time = time.time()
    args = parser.parse_args()
    db = SQLBackend.instance()
    db.connect()

    if args.verbose:
        logger.setLevel(logging.DEBUG)
        logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

    if not (args.payloads or args.surveys):
        logger.error("Please provide a payload or survey result file")
        parser.print_help()
        sys.exit(1)

    try:
        if args.payloads:
            stats = ingest.ingest_payloads(args.payloads)
            print_payload_stats(stats)

        if args.surveys:
            ingest.ingest_surveys(args.surveys)
    except Exception, e:
        logger.error("Please check your file input\n")
        logger.exception(e)
        parser.print_help()
        sys.exit(1)
    finish_time = time.time()

    time_taken = (finish_time - start_time) / 60.0
    logger.info("time_taken: {0} minutes".format(time_taken))

if __name__ == '__main__':
    main()
