import json
import datetime
import logging
from urllib.error import HTTPError
from urllib.request import urlopen
from instagram.media import Media

base_url = "https://api.instagram.com/v1/tags/%s/media/recent?count=%d&access_token=%s"
instagram_count = 1

class Tag:

    def __init__(self, tag, access_token):
        self.tag = tag
        self.access_token = access_token
        self.min_tag_id = ""
        self.last_media_id = ""
        self.enabled = True

    def get_instagram_feed(self):
        url = base_url % (self.tag, instagram_count, self.access_token)
        if self.min_tag_id != "":
            url += "&min_tag_id=" + self.min_tag_id

        try:
            logging.debug("Get media with url: %s" % url)
            content = urlopen(url).read()
            return json.loads(content.decode("utf8"))
        except HTTPError as e:
            logging.error("Failed to fetch data from instagram %s" % e)
            return dict()

    def run(self):
        if self.enabled:
            content = self.get_instagram_feed()
            collection = content.get("data", [])

            for element in collection:
                media = Media(element)
                logging.info("Found media: %s" % media)

                if not media.valid():
                    logging.info("Will skip non valid media: %s" % element)
                    continue
                if self.last_media_id == media.id:
                    continue

                media.generate_and_save_image()
                self.last_media_id = media.id

            self.min_tag_id = content.get("pagination", {}).get("min_tag_id")
            if self.min_tag_id == None:
                self.min_tag_id = ""
