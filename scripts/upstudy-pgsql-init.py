#!/usr/bin/env python
import sys
import argparse
import logging
import upstudy.settings as settings
from upstudy.data.backends.postgres import PostgresBackend
logging.basicConfig(format="%(levelname)s: %(message)s\n")
logger = logging.getLogger("upstudy")
logger.setLevel(logging.DEBUG)

parser = argparse.ArgumentParser(description="Read user research payload and create data directories")
parser.add_argument("-c", "--clobber", help="Clobber tables before initializing", action="store_true", default=False)

if __name__ == "__main__":
    args = parser.parse_args()
    backend = PostgresBackend(settings.postgres)
    backend._initialize()
    backend._setup()
