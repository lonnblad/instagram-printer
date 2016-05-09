#!/usr/bin/env python

import time
import subprocess
import datetime
import threading
import os

from os import listdir
from PIL import Image
from threading import Thread

class PrintDispatcher(threading.Thread):
    def __init__(self, dry_run, sleep_interval):
        self.printer = Printer("SIGMA_EE_CP1200_1", sleep_interval)
        self.sleep_interval = sleep_interval
        self.dry_run = dry_run

        super(PrintDispatcher, self).__init__()
        self._stopper = threading.Event()

    def stop(self):
        print("Stopping Printer thread", flush=True)
        self._stopper.set()

    def stopped(self):
        return self._stopper.isSet()

    def run(self):
        if not self.dry_run:
            self.printer.block_while_occupied()

        while not self.stopped():
            print("P", end="", flush=True)

            image_files = [f for f in listdir("temp") if f.endswith(".png")]
            for image_file in image_files:
                image_png_path = "temp/" + image_file
                if self.dry_run:
                    Image.open(image_png_path).show()
                    os.remove(image_png_path)
                else:
                    print_image(image_png_path, self.printer_name)

                if self.stopped():
                    break

            time.sleep(self.sleep_interval)


class Printer:
    def __init__(self, printer_name, sleep_interval):
        self.name = printer_name
        self.sleep_interval = sleep_interval

    def block_while_occupied(self):
        while subprocess.check_output(["lpstat", "-o", self.name]) != "":
            print("\n[" + str(datetime.datetime.utcnow()) + "]" + " Printing file")

    def print_image(png_path):
        pdf_path = png_path.replace(".png", ".pdf")

        subprocess.check_output(["convert", png_path, "-page", "640x947", pdf_path])
        subprocess.check_output(["lp",
            "-d", self.name,
            "-o", "page-border=none",
            "-o", "fit-to-page",
            "-o", "media=Postcard",
            pdf_path])

        self.block_while_occupied()

        os.remove(pdf_path)
        os.remove(png_path)