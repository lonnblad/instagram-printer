#!/usr/bin/env python
# Usage: while [ 1 -eq 1 ]; do python run.py && sleep 1; done
# or crontab

import re
import sys
import time
import os.path
import urllib2
import json
import subprocess
import datetime
from image import *
from os import listdir
from PIL import Image
from threading import Thread

# Configuration
min_tag_id_file = "min_tag_id.lock"
last_id_file = "last_media_id.lock"
instagram_tag = ""
instagram_count = 1
instagram_client_id = ""
dry_run = True
sleep_interval = 10
base_url = "https://api.instagram.com/v1/tags/%s/media/recent?count=%d&client_id=%s"
printer_name = "SIGMA_EE_CP1200_1"
# printer_name = "Canon_CP910"

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
    if not os.path.isfile(min_tag_id_file):
        return url

    with open(min_tag_id_file, 'r') as fp:
        tag_id = fp.read()
        if tag_id != "":
            url += "&min_tag_id=" + tag_id
        return url

    return url

def store_min_tag_id(id):
    if id != "":
        with open(min_tag_id_file, 'w') as fp:
            fp.write(id)

def get_instagram_feed():
    url = get_instagram_url()
    print(url)
    raw = urllib2.urlopen(url).read()
    return json.loads(raw)

def printer_occupied():
    value = subprocess.check_output(["lpstat", "-o", printer_name])
    return value != ""

def print_images():
    while print_images_thread_active and printer_occupied():
        print "[" + str(datetime.datetime.utcnow()) + "]" + " Printing old file"
        time.sleep(sleep_interval)

    while print_images_thread_active:
        print "[" + str(datetime.datetime.utcnow()) + "]" + " Print images loop"

        imageFiles = [f for f in listdir("temp") if f.endswith(".png")]
        for imageFile in imageFiles:
            png_path = "temp/" + imageFile
            pdf_path = png_path.replace(".png", ".pdf")
            if dry_run:
                Image.open(png_path).show()
                os.remove(png_path)
            else:
                subprocess.check_output(["convert", png_path, "-page", "640x947", pdf_path])
                subprocess.check_output(["lp",
                    "-d", printer_name,
                    "-o", "page-border=none",
                    "-o", "fit-to-page",
                    "-o", "media=Postcard",
                    pdf_path])

                while print_images_thread_active and printer_occupied():
                    print "[" + str(datetime.datetime.utcnow()) + "]" + " Printing file: %s" % (pdf_path)
                    time.sleep(sleep_interval)

                os.remove(pdf_path)
                os.remove(png_path)

            if print_images_thread_active:
                break

        time.sleep(sleep_interval)

def get_images():
    while get_images_thread_active:
        print "[" + str(datetime.datetime.utcnow()) + "]" + " Get images loop"
        last_id = get_last_id()

        content = get_instagram_feed()
        data = content.get("data", [])
        for elem in data:
            id = elem.get("id")

            # Media might not be an image
            if elem.get("type") != "image":
                print "[" + str(datetime.datetime.utcnow()) + "]" + " Will skip non image media of type: %s, with id: %s" % (elem.get("type"), id)
                continue

            created_time = elem.get("created_time")
            author = "@" + elem.get("user", {}).get("username")
            image_url = elem.get("images", {}).get("standard_resolution", {}).get("url")

            # Can be null
            try:
                caption = elem.get("caption", {}).get("text")
            except AttributeError as err:
                print err
                caption = ""

            if image_url and id and last_id != id:
                print "[" + str(datetime.datetime.utcnow()) + "]" + " Found image with data: #%s, \n\tauthor: %s, \n\tcaption: %s, \n\timage: %s" % (id, author, caption, image_url)
                set_last_id(id)
                image = generate_image(image_url, author, caption, created_time)
                dumpfile = "%s_%s" % (int(time.time()), id)
                image.save("temp/%s.png" % dumpfile)

        pagination = content.get("pagination", {})
        min_tag_id = pagination.get("min_tag_id")
        if min_tag_id != None:
            store_min_tag_id(min_tag_id)
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
    print "\n\n" + "[" + str(datetime.datetime.utcnow()) + "]" + " Will try to exit gracefully ***\n\n"
    stop_threads();
    sys.exit()
