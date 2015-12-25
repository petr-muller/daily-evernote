#!/usr/bin/python2
"""A simple script fetching a random Evernote note from a random Evernote notebook."""

import logging
import argparse
from datetime import datetime, date

def valid_date(datestring):
  try:
    return datetime.strptime(datestring, "%Y-%m-%d").date()
  except ValueError:
    message = "Invalid date: '{0}'.".format(datestring)
    raise argparse.ArgumentTypeError(message)


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("-d", "--date", type=valid_date, default=date.today(), dest="date", metavar="YYYY-MM-DD",
                      help="A date in YYYY-MM-DD format",)
  parser.add_argument("--debug", dest="loglevel", action="store_const", const=logging.DEBUG, default=logging.WARNING,
                      help="Print all debugging statements")
  parser.add_argument("-v", "--verbose", dest="loglevel", action="store_const", const=logging.INFO,
                      help="Print more information about progress")
  args = parser.parse_args()

  logging.basicConfig(level=args.loglevel, format="[ %(levelname)-8s] %(message)s")
  logging.info("Fetching Evernote of the Day: %s", args.date)

if __name__ == "__main__":
  main()
