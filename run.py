#!/usr/bin/env python

import sys
import time

from utilities.logger import *
from instagram.instagram import Instagram
from printer.dispatcher import Dispatcher

sleep_interval = 10
dry_run = True
set_debug()

printer_thread = Dispatcher(dry_run, sleep_interval)
instagram_thread = Instagram(sleep_interval)

try:
    log("Will try to start all threads")
    printer_thread.start()
    instagram_thread.start()
    while True:
        time.sleep(sleep_interval)

except (KeyboardInterrupt, SystemExit):
    log("Will try to exit gracefully")
    printer_thread.stop()
    instagram_thread.stop()
    printer_thread.join()
    instagram_thread.join()
    sys.exit()
