#!/usr/bin/env python

import jsonpickle
import time
import os.path
import threading
from threading import Thread
from instagram.tag import Tag
from utilities.logger import *


class Instagram(threading.Thread):

    def __init__(self, sleep_interval):
        self.tags_file = "tags.lock"
        self.instagram_tags = [Tag("sigmaembedded"), Tag("pinkprogramming")]
        self.sleep_interval = sleep_interval

        super(Instagram, self).__init__()
        self._stopper = threading.Event()

    def stop(self):
        log("Stopping Instagram thread")
        self._stopper.set()

    def stopped(self):
        return self._stopper.isSet()

    def store_tags(self):
        json = jsonpickle.encode(self.instagram_tags)
        with open(self.tags_file, 'w+t') as output:
            output.write(json)

    def load_tags(self):
        if not os.path.isfile(self.tags_file):
            return

        with open(self.tags_file, 'r+t') as input:
            self.instagram_tags = jsonpickle.decode(input.read())

    def run(self):
        while not self.stopped():
            print("I", end="", flush=True)
            self.load_tags()

            for tag in self.instagram_tags:
                tag.run()

            self.store_tags()
            time.sleep(self.sleep_interval)
