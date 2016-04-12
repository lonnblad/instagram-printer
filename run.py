#!/usr/bin/env python
# Usage: while [ 1 -eq 1 ]; do python run.py && sleep 1; done
# or crontab

import sys
import time
import os.path
import urllib2
import json
import subprocess
from image import *
from os import listdir
from PIL import Image
from threading import Thread

# Configuration
next_max_tag_id_file = "next_max_tag_id.lock"
last_id_file = "last_id.lock"
instagram_tag = "fashion"
instagram_count = 10
instagram_client_id = "cf050c7486414aaf899a6e4c23db7090"
dry_run = True
sleep_interval = 10
base_url = "https://api.instagram.com/v1/tags/%s/media/recent?count=%d&client_id=%s"

def get_last_id():
    if not os.path.isfile(last_id_file):
        return

    with open(last_id_file, 'r') as fp:
        return fp.read()

    return

def set_last_id(id):
    with open(last_id_file, 'w') as fp:
        fp.write(id)

def get_instagram_url():
    url = base_url % (instagram_tag, instagram_count, instagram_client_id)
    if not os.path.isfile(next_max_tag_id_file):
        return url

    with open(next_max_tag_id_file, 'r') as fp:
        return url + "&max_tag_id=" + fp.read()

    return url

def store_next_max_tag_id(id):
    with open(next_max_tag_id_file, 'w') as fp:
        fp.write(id)

def get_instagram_feed():
    url = get_instagram_url()
    print(url)
    raw = urllib2.urlopen(url).read()
    return json.loads(raw)

def print_images():
    while print_images_thread_active:
        print "*** Print images loop"
        imageFiles = [f for f in listdir("temp") if f.endswith(".png")]
        for imageFile in imageFiles:
            pdf_path, png_path = "temp/" + imageFile, "temp/" + imageFile
            pdf_path.replace(".png", ".pdf")
            print "Found file: %s" % png_path
            if dry_run:
                Image.open(png_path).show()
                os.remove(png_path)
            else:
                subprocess.check_output(["convert", png_path, pdf_path])
                subprocess.check_output(["lp",
                    "-o", "page-border=none",
                    "-o", "fit-to-page",
                    "-o", "media=letter",
                    pdf_path])
                os.remove(pdf_path)
                os.remove(png_path)
        time.sleep(sleep_interval)

def get_images():
    while get_images_thread_active:
        print "*** Get images loop"
        last_id = get_last_id()

        content = get_instagram_feed()
        data = content.get("data", [])
        for elem in data:
            id = elem.get("id")
            created_time = elem.get("created_time")
            author = "@" + elem.get("caption", {}).get("from", {}).get("username", "unknown")
            caption = elem.get("caption", {}).get("text", "")
            image_url = elem.get("images", {}).get("standard_resolution", {}).get("url")

            if image_url and id and last_id != id:
                print "*** Found image with data: #%s, \n\tauthor: %s, \n\tcaption: %s, \n\timage: %s" % (id, author, caption, image_url)
                set_last_id(id)
                image = generate_image(image_url, author, caption, created_time)
                dumpfile = "%s_%s" % (int(time.time()), id)
                image.save("temp/%s.png" % dumpfile)

        pagination = content.get("pagination", {})
        next_max_id = pagination.get("next_max_id")
        store_next_max_tag_id(next_max_id)
        time.sleep(sleep_interval)

print_images_thread = Thread(target=print_images)
print_images_thread_active = True
get_images_thread = Thread(target=get_images)
get_images_thread_active = True

def start_threads():
    print_images_thread.start()
    get_images_thread.start()

def stop_threads():
    global print_images_thread_active
    print_images_thread_active = False
    global get_images_thread_active
    get_images_thread_active = False

try:
    start_threads()
    while True:
        time.sleep(sleep_interval)
except (KeyboardInterrupt, SystemExit):
    print "*** Will try to exit gracefully"
    stop_threads();
    sys.exit()
