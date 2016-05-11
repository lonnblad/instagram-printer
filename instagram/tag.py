#!/usr/bin/env python

import json
import datetime
from urllib.request import urlopen
from instagram.media import Media
from utilities.logger import *

base_url = "https://api.instagram.com/v1/tags/%s/media/recent?count=%d&client_id=%s"
instagram_client_id = ""
instagram_count = 1


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

        debug("Get media with url: %s", args=(url,))
        content = urlopen(url).read()
        return json.loads(content.decode("utf8"))

    def run(self):
        if self.enabled:
            content = self.get_instagram_feed()
            collection = content.get("data", [])

            for element in collection:
                media = Media(element)
                log("Found media: %s", args=(media,))

                if not media.valid():
                    log("Will skip non valid media: %s", args=(element,))
                    continue
                if self.last_media_id == media.id:
                    continue

                media.generate_and_save_image()
                self.last_media_id = media.id

            self.min_tag_id = content.get("pagination", {}).get("min_tag_id")
            if self.min_tag_id == None:
                self.min_tag_id = ""
