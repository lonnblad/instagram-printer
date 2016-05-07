#!/usr/bin/env python

import sys
import time
import datetime

from instagram import Instagram
from printer import PrintDispatcher

sleep_interval = 10
dry_run = True

printer_thread = PrintDispatcher(dry_run, sleep_interval)
instagram_thread = Instagram(sleep_interval)

try:
    printer_thread.start()
    instagram_thread.start()
    while True:
        time.sleep(sleep_interval)

except (KeyboardInterrupt, SystemExit):
    print("\n\n" + "[" + str(datetime.datetime.utcnow()) + "]" + " Will try to exit gracefully ***\n\n")
    printer_thread.stop()
    instagram_thread.stop()
    printer_thread.join()
    instagram_thread.join()
    sys.exit()
