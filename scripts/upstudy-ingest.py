#!/usr/bin/env python
import sys
import os
import argparse
import upstudy.data.ingest as ingest
import logging

logging.basicConfig(format="%(levelname)s: %(message)s\n")
logger = logging.getLogger("cmd-ingest")

parser = argparse.ArgumentParser(description="Read user research payload and create data directories")
parser.add_argument("-p", "--payloads", metavar="PAYLOADS_FILE", type=str, help="A file containing research addon payloads, one per line, each entry in JSON format")
parser.add_argument("-s", "--surveys", metavar="SURVEYS_FILE", type=str, help="A file containing survey responses, one per line, in CSV format")

def main():
    args = parser.parse_args()

    if not (args.payloads or args.surveys):
        logger.error("Please provide a payload or survey result file")
        parser.print_help()
        sys.exit(1)

    try:
        if args.payloads:
            ingest.ingest_payloads(args.payloads)

        if args.surveys:
            ingest.ingest_surveys(args.surveys)
    except Exception, e:
        logger.exception(e)
        logger.error("invalid input file\n")
        parser.print_help()
        sys.exit(1)

if __name__ == '__main__':
    main()
