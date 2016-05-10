#!/usr/bin/env python

import time
import subprocess
import datetime
import os
from utilities.logger import *

class Printer:
    def __init__(self, printer_name, sleep_interval):
        self.name = printer_name
        self.sleep_interval = sleep_interval

    def block_while_occupied(self):
        while subprocess.check_output(["lpstat", "-o", self.name]) != "":
            log("Printing file")
            time.sleep(self.sleep_interval)

    def print_image(png_path):
        pdf_path = png_path.replace(".png", ".pdf")

        subprocess.check_output(["convert", png_path, "-page", "640x947", pdf_path])
        subprocess.check_output(["lp",
            "-d", self.name,
            "-o", "page-border=none",
            "-o", "fit-to-page",
            "-o", "media=Postcard",
            pdf_path])
        os.remove(pdf_path)

        self.block_while_occupied()