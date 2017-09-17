#!/usr/bin/env python3
"""
i3 window title changer is a small daemon for i3wm which connects to it via unix socket,
listens for new window and title change events and change them to something simple
based on the user defined patterns in the rules file.
"""
import os
import re
import sys
import csv
import enum
import pprint
import subprocess
import i3ipc


DEFAULT_RULE_PATH = '~/.config/i3/window-title-changer-rules'


class MatchMethod(enum.Enum):
    TEXT = 'text'
    CLASS = 'class'
    REGEX = 'regex'


# this is a cache for the rules which is filled at start
# it contains three-tuples of (match method, search phrase, new title)
title_rules = ()


def read_rules_file(rules_file):
    global title_rules
    rules_file = os.path.expanduser(rules_file)
    print('Reading rules file:', rules_file)
    with open(rules_file) as csvfile:
        reader = csv.reader(csvfile)
        title_rules = tuple(rule for rule in reader)
    pprint.pprint(title_rules)


def handle_title_change(i3, event):
    window_id = event.container.id
    current_title = event.container.name
    window_class = event.container.window_class
    print('"{}" class={}, id={}'.format(current_title, window_class, window_id))

    for match_method, search_phrase, new_title in title_rules:
        method = MatchMethod(match_method)
        if method is MatchMethod.TEXT and search_phrase in current_title:
            print('Found word "{}" in "{}"'.format(search_phrase, current_title), end='')
            break
        elif method is MatchMethod.CLASS and search_phrase == window_class:
            print('Found "{}" class window: "{}"'.format(window_class, current_title), end='')
            break
        elif method is MatchMethod.REGEX and re.search(search_phrase, current_title):
            print('Matched regex "{}" for "{}"'.format(search_phrase, current_title), end='')
            break
    else:
        return

    print(', changing title to "{}"'.format(new_title))
    window_i3 = i3.get_tree().find_by_id(window_id)
    window_i3.command('title_format ' + new_title)


def on_new_window(i3, event):
    print('New window ', end=' ')
    handle_title_change(i3, event)


def on_title_change(i3, event):
    print('Window title changed ', end=' ')
    handle_title_change(i3, event)


def parse_cli_arguments():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rules-file', dest='rules_file', default=DEFAULT_RULE_PATH,
                        help='File containing rule definitions (default: ' + DEFAULT_RULE_PATH + ')')
    return parser.parse_args()


def print_i3_socket_path():
    print('$I3SOCK:', os.environ.get('I3SOCK'))
    print('i3 --get-socket-path:', end=' ', flush=True)
    subprocess.run(['i3', '--get-socketpath'])


def main(rules_file):
    print_i3_socket_path()
    read_rules_file(rules_file)

    i3 = i3ipc.Connection()
    i3.on("window::new", on_new_window)
    i3.on("window::title", on_title_change)
    # Run main loop and wait for events
    i3.main()


if __name__ == '__main__':
    args = parse_cli_arguments()
    exitcode = main(args.rules_file)
    sys.exit(exitcode)
