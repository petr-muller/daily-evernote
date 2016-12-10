#!/usr/bin/env python
"""A simple script fetching a random Evernote note from a random Evernote notebook."""

import logging
import argparse
import random
import webbrowser
import sys

import os.path

from datetime import datetime, date
from ConfigParser import ConfigParser
from evernote.api.client import EvernoteClient
from evernote.edam.notestore.ttypes import NoteFilter, NotesMetadataResultSpec
from evernote.edam.limits.constants import EDAM_USER_NOTES_MAX


def valid_date(datestring):
  try:
    return datetime.strptime(datestring, "%Y-%m-%d").date()
  except ValueError:
    message = "Invalid date: '{0}'.".format(datestring)
    raise argparse.ArgumentTypeError(message)


class RandomEvernoteSelector(object):
  """A simple class selecting random elements from Evernote entities"""
  def __init__(self, date_seed):
    self.random = random
    self.random.seed(date_seed)

  def get_random_notebook(self, evernote_wrapper):
    return self.random.choice(evernote_wrapper.list_notebooks())

  def get_random_note(self, evernote_wrapper, notebook):
    """
    Given a notebook, returns a random note from that notebook
    """
    if len(evernote_wrapper.notes_in_notebook(notebook).notes) == 0:
      logging.fatal("No notes in notebook: %s", notebook.name)
      sys.exit(1)

    return self.random.choice(evernote_wrapper.notes_in_notebook(notebook).notes)


class EvernoteWrapper(object):
  """A simplifying wrapper for Evernote API client object"""

  def __init__(self, token, sandbox):
    self.client = EvernoteClient(token=token, sandbox=sandbox)
    self.notebooks = None
    self.notes = None

  def list_notebooks(self):
    """Returns a list of notebooks for a user. Data are actually obtained only during first call of this function. For
    next calls, the info is cached.
    """
    if self.notebooks is None:
      note_store = self.client.get_note_store()
      self.notebooks = note_store.listNotebooks()

    return self.notebooks

  def notes_in_notebook(self, notebook):
    """Returns a list of notes in a notebook. Note records contain only a GUID and a note title. Data are actually
    obtained only during first call of this function. For next calls, the info is cached.
    """
    if self.notes is None:
      note_filter = NoteFilter(notebookGuid=notebook.guid)
      result_spec = NotesMetadataResultSpec(includeTitle=True)
      note_store = self.client.get_note_store()
      self.notes = note_store.findNotesMetadata(self.client.token, note_filter, 0, EDAM_USER_NOTES_MAX, result_spec)

    return self.notes

  def get_note_content(self, note):
    note_store = self.client.get_note_store()
    return note_store.getNote(self.client.token, note.guid, True, False, False, False).content

  def get_note_url(self, note):
    """Returns the URL of a given note."""
    note_url = "https://{0}/shard/{1}/nl/{2}/{3}"
    service_url = self.client.service_host
    user_store = self.client.get_user_store()
    user = user_store.getUser()
    return note_url.format(service_url, user.shardId, user.id, note.guid)


class DailyEvernoteConfig(object):
  """
  Carries configuration for the script.
  """
  # pylint: disable=too-few-public-methods

  DEFAULT_CONFIG_FILENAME = ".daily-evernote"
  DEFAULT_PATH = os.path.join(os.path.expanduser("~"), DEFAULT_CONFIG_FILENAME)

  def __init__(self, config):
    self.config = config

  @property
  def token(self):
    return self.config.get("account", "token")


def parse_config(config_file):
  parser = ConfigParser()
  parser.read(config_file)
  return DailyEvernoteConfig(parser)


def main():
  parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument("-d", "--date", type=valid_date, default=date.today(), dest="date", metavar="YYYY-MM-DD",
                      help="A date in YYYY-MM-DD format",)
  parser.add_argument("--debug", dest="loglevel", action="store_const", const=logging.DEBUG, default=logging.WARNING,
                      help="Print all debugging statements")
  parser.add_argument("-v", "--verbose", dest="loglevel", action="store_const", const=logging.INFO,
                      help="Print more information about progress")
  parser.add_argument("--sandbox", dest="sandbox", action="store_true", default=False,
                      help="Use a Sandbox environment of Evernote")
  parser.add_argument("--config", dest="config", default=DailyEvernoteConfig.DEFAULT_PATH,
                      help="Path to a configuration file")
  args = parser.parse_args()

  config = parse_config(args.config)

  logging.basicConfig(level=args.loglevel, format="[ %(levelname)-8s] %(message)s")
  logging.info("Fetching Evernote of the Day: %s", args.date)
  selector = RandomEvernoteSelector(args.date)
  evernote_wrapper = EvernoteWrapper(config.token, args.sandbox)
  notebook = selector.get_random_notebook(evernote_wrapper)
  logging.info("Selected Evernote notebook: %s", notebook.name)
  note = selector.get_random_note(evernote_wrapper, notebook)
  logging.info("Selected Evernote note: %s", note.title)
  url = evernote_wrapper.get_note_url(note)
  logging.info("Note URL: %s", url)
  webbrowser.open(url)

if __name__ == "__main__":
  main()
