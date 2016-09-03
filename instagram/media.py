import time
import datetime
import logging
from image import *

class Media:

    def __init__(self, data):
        try:
            self.id = data.get("id")
            self.type = data.get("type")
            self.created_time = data.get("created_time")
            self.author = "@" + data.get("user", {}).get("username")
            self.image_url = data.get("images", {}).get(
                "standard_resolution", {}).get("url")
            self.caption = data.get("caption", {}).get("text")
        except AttributeError as err:
            logging.info("Caught exception: %s", args=(err,))

    def __str__(self):
        return '\n\tid:"%s",\n\tauthor:"%s",\n\tcaption:"%s"' % (self.id, self.author, self.caption)

    def valid(self):
        return self.type == "image" and self.image_url and self.id

    def generate_and_save_image(self):
        image = generate_image(self.image_url, self.author,
                               self.caption, self.created_time)
        image.save("temp/%s_%s.png" % (int(time.time()), id))
