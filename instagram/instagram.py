import json
import time
import os.path
import threading
import logging
from instagram.tag import Tag
from threading import Thread

class Instagram(threading.Thread):

    def __init__(self, tags_str, access_token, sleep_interval):
        self.instagram_tags = [Tag(tag, access_token) for tag in tags_str]
        self.sleep_interval = sleep_interval

        super(Instagram, self).__init__()
        self._stopper = threading.Event()

    def stop(self):
        logging.info("Stopping Instagram thread")
        self._stopper.set()

    def stopped(self):
        return self._stopper.isSet()

    def run(self):
        while not self.stopped():
            for tag in self.instagram_tags:
                tag.run()

            time.sleep(self.sleep_interval)
