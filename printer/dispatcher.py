import time
import datetime
import threading
import os
import tempfile
import logging

from os import listdir
from PIL import Image
from threading import Thread
from printer.worker import Printer

class Dispatcher(threading.Thread):

    def __init__(self, dry_run, printer, sleep_interval):
        self.printer = Printer(printer, sleep_interval)
        self.sleep_interval = sleep_interval
        self.dry_run = dry_run

        super(Dispatcher, self).__init__()
        self._stopper = threading.Event()

    def stop(self):
        logging.info("Stopping Printer thread")
        self._stopper.set()

    def stopped(self):
        return self._stopper.isSet()

    def run(self):
        if not self.dry_run:
            self.printer.block_while_occupied()

        tempdir = tempfile.mkdtemp()
        logging.info("Temp directory used: %s" % tempdir)
        while not self.stopped():
            image_files = [f for f in listdir(tempdir) if f.endswith(".png")]
            for image_file in image_files:
                image_png_path = "%s/%s" % (tempdir, image_file)
                if self.dry_run:
                    Image.open(image_png_path).show()
                else:
                    print_image(image_png_path, self.printer_name)

                os.remove(image_png_path)

                if self.stopped():
                    break

            time.sleep(self.sleep_interval)
