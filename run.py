#!/usr/bin/env python

import sys
import time
import logging
import argparse

from instagram.instagram import Instagram
from printer.dispatcher import Dispatcher

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('tags', metavar='tags', type=str, nargs='+',
                help='instagram tags to')
parser.add_argument('--dry', type=bool, dest='dry_run',
                default=True, help='Dry run printing operations')
parser.add_argument('--interval', type=int, dest='interval',
                default=10, help='Pull interval')
parser.add_argument('--instagram-access-token', type=str, dest='access_token',
                help='Instagram access token')
parser.add_argument('--printer', type=str, dest='printer',
                default="SIGMA_EE_CP1200_1", help='Printer name')
                
args = parser.parse_args()

printer_thread = Dispatcher(args.dry_run, args.printer, args.interval)
instagram_thread = Instagram(args.tags, args.access_token, args.interval)

try:
    logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M')

    logging.info("Will try to start all threads")
    printer_thread.start()
    instagram_thread.start()
    while True:
        time.sleep(args.interval)

except (KeyboardInterrupt, SystemExit):
    logging.info("Will try to exit gracefully")
    printer_thread.stop()
    instagram_thread.stop()
    printer_thread.join()
    instagram_thread.join()
    sys.exit()
