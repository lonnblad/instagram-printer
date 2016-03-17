#!/usr/bin/env python
# Usage: while [ 1 -eq 1 ]; do python run.py && sleep 1; done
# or crontab

import time
import os.path
import urllib2
import json
import subprocess
from image import *

# Configuration
last_file = "instagram.lock"
instagram_tag = "<instagram-tag>"
instagram_client_id = "<instagram-token>"
dry_run = False
sleep_interval = 10

def get_last_id(file_path):
    if not os.path.isfile(file_path):
        return

    with open(file_path, 'r') as fp:
        return fp.read()

    return

def set_new_last_id(file_path, id):
    with open(file_path, 'w') as fp:
        fp.write(id)

def get_instagram_feed(client_id, tag, count):
    url = "https://api.instagram.com/v1/tags/%s/media/recent?count=%d&client_id=%s" % (tag, count, client_id)
    raw = urllib2.urlopen(url).read()
    return json.loads(raw)

def print_image(dry_run, image, id):
    if dry_run:
        image.show()
    else:
        if not os.path.isdir("temp"):
            os.mkdir("temp")

        dumpfile = "%s_%s" % (int(time.time()), id)
        image.save("temp/%s.png" % dumpfile)
        subprocess.check_output(["convert", "temp/%s.png" % dumpfile, "temp/%s.pdf" % dumpfile])
        subprocess.check_output(["lp",
            "-o", "page-border=none",
            "-o", "fit-to-page",
            "-o", "media=letter",
            "temp/%s.pdf" % dumpfile])

        os.remove("temp/%s.png" % dumpfile)

def run():
    last_id = get_last_id(last_file)
    content = get_instagram_feed(instagram_client_id, instagram_tag, 1)

    data = content.get("data", [])
    for elem in data:
        id = elem.get("id")
        created_time = elem.get("created_time")
        author = "@" + elem.get("caption", {}).get("from", {}).get("username", "unknown")
        caption = elem.get("caption", {}).get("text", "")
        image_url = elem.get("images", {}).get("standard_resolution", {}).get("url")

        if image_url and id and last_id != id:
            print "*** Printing #%s, author: %s, caption: %s, image: %s" % (id, author, caption, image_url)

            set_new_last_id(last_file, id)
            image = generate_image(image_url, author, caption, created_time)
            print_image(dry_run, image, id)

while True:
    run()
    time.sleep(sleep_interval)
