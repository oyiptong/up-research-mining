#!/usr/bin/env python
import sys
import argparse
import logging
from upstudy import settings
from upstudy.data.backends import SQLBackend
from upstudy.data.models import create_categories
logging.basicConfig(format="%(levelname)s: %(message)s")
logger = logging.getLogger("upstudy")
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARN)
logger.setLevel(logging.INFO)

parser = argparse.ArgumentParser(description="Read user research payload and create data directories")
parser.add_argument("-c", "--clobber", help="Clobber tables before initializing", action="store_true", default=False)
parser.add_argument("-v", "--verbose", help="Verbose", action="store_true", default=False)

if __name__ == "__main__":
    args = parser.parse_args()
    if args.verbose:
        logger.setLevel(logging.DEBUG)
        logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    db = SQLBackend.instance()
    if args.clobber:
        db.__drop__()
    db.__initialize__()
    db.__create_tables__()
    db.connect()
    db.__load_categories__()
