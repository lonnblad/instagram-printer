#!/usr/bin/env python

import datetime

_debug = False


def set_debug():
    global _debug
    _debug = True


def log(msg, args=(), debug=False):
    if debug and not _debug:
        return

    args = (str(datetime.datetime.utcnow()),) + args
    print(("\n[%s] " + msg) % args)


def debug(msg, args=()):
    log(msg, args=args, debug=True)
