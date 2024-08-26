from argparse import Namespace

from rich import print

from . import constants


def show_log(args: Namespace):
    # TODO: refactor this...
    # this logic seems ... odd?
    # NOTE: right now, intentionally don't use args here.
    # but for consistencies sake, just keep the API the same.
    with open(constants.logfile) as log_file:
        content = log_file.read()
        print(content)
