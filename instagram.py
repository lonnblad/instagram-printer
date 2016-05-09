#!/usr/bin/env python

import jsonpickle
import time
import os.path
import json
import datetime
import threading
from urllib.request import urlopen
from image import *
from PIL import Image
from threading import Thread

base_url = "https://api.instagram.com/v1/tags/%s/media/recent?count=%d&client_id=%s"
instagram_client_id = ""
instagram_count = 1

class Instagram(threading.Thread):
    def __init__(self, sleep_interval):
        self.tags_file = "tags.lock"
        self.instagram_tags = []
        self.sleep_interval = sleep_interval

        super(Instagram, self).__init__()
        self._stopper = threading.Event()

    def stop(self):
        print("Stopping Instagram thread", flush=True)
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

class Tag:
    def __init__(self, tag):
        self.tag = tag
        self.min_tag_id = ""
        self.last_media_id = ""
        self.enabled = True

    def get_instagram_feed(self):
        url = base_url % (self.tag, instagram_count, instagram_client_id)
        if self.min_tag_id != "":
            url += "&min_tag_id=" + self.min_tag_id

        content = urlopen(url).read()
        return json.loads(content.decode("utf8"))

    def run(self):
        if self.enabled:
            content = self.get_instagram_feed()
            collection = content.get("data", [])

            for element in collection:
                media = Media(element)
                if media.notValid():
                    print("\n[" + str(datetime.datetime.utcnow()) + "]" + " Will skip non valid media: %s" % (element))
                    continue
                if self.last_media_id == media.id:
                    continue

                media.generate_and_save_image()
                self.last_media_id = media.id

            self.min_tag_id = content.get("pagination", {}).get("min_tag_id")
            if self.min_tag_id == None:
                self.min_tag_id = ""

class Media:
    def __init__(self, data):
        try:
            self.id = data.get("id")
            self.type = data.get("type")
            self.created_time = data.get("created_time")
            self.author = "@" + data.get("user", {}).get("username")
            self.image_url = data.get("images", {}).get("standard_resolution", {}).get("url")
            self.caption = data.get("caption", {}).get("text")
        except AttributeError as err:
            print("\n[" + str(datetime.datetime.utcnow()) + "]" + " Caught exception: %s" % (err))

    def notValid(self):
        return self.type != "image" or self.image_url == None or self.id == None

    def generate_and_save_image(self):
        image = generate_image(self.image_url, self.author, self.caption, self.created_time)
        image.save("temp/%s_%s.png" % (int(time.time()), id))