#!/usr/bin/env python

import jsonpickle
import re
import sys
import time
import os.path
import json
import subprocess
import datetime
from urllib.request import urlopen
from image import *
from os import listdir
from PIL import Image
from threading import Thread
from json import JSONEncoder   

class Tag:
    def __init__(self, tag):
        self.tag = tag
        self.min_tag_id = ""
        self.last_media_id = ""
        self.enabled = True

# Configuration
tags_file = "tags.lock"
instagram_tags = [Tag("sigmaembedded"),Tag("pinkprogramming")]

instagram_client_id = "cf050c7486414aaf899a6e4c23db7090"
instagram_count = 1
dry_run = True
debug = False
sleep_interval = 10
base_url = "https://api.instagram.com/v1/tags/%s/media/recent?count=%d&client_id=%s"
printer_name = "SIGMA_EE_CP1200_1"
# printer_name = "Canon_CP910"

def store_tags():
    json = jsonpickle.encode(instagram_tags)
    with open(tags_file, 'w+t') as output:
        output.write(json)

def load_tags():
    if not os.path.isfile(tags_file):
        return

    with open(tags_file, 'r+t') as input:
        global instagram_tags
        instagram_tags = jsonpickle.decode(input.read())

def get_instagram_feed(tag):
    url = base_url % (tag.tag, instagram_count, instagram_client_id)
    if tag.min_tag_id != "":
        url += "&min_tag_id=" + tag.min_tag_id

    # print("\n"+url) //debug
    content = urlopen(url).read()
    return json.loads(content.decode("utf8"))

def printer_occupied():
    value = subprocess.check_output(["lpstat", "-o", printer_name])
    return value != ""

def print_images():
    # try:
    while not dry_run and print_images_thread_active and printer_occupied():
        print("\n[" + str(datetime.datetime.utcnow()) + "]" + " Printing old file")
        time.sleep(sleep_interval)

    while print_images_thread_active:
        print("@", end="", flush=True)

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
                    print("\n[" + str(datetime.datetime.utcnow()) + "]" + " Printing file: %s" % (pdf_path))
                    time.sleep(sleep_interval)

                os.remove(pdf_path)
                os.remove(png_path)

            if print_images_thread_active:
                break

        time.sleep(sleep_interval)

    # except Exception as err:
    #     print(err)
    #     stop_threads()

def get_images():
    # try:
    while get_images_thread_active:
        print("#", end="", flush=True)
        load_tags()

        for tag in instagram_tags:
            if tag.enabled:
                content = get_instagram_feed(tag)
                data = content.get("data", [])

                for elem in data:
                    id = elem.get("id")

                    # Media might not be an image
                    if elem.get("type") != "image":
                        print("\n[" + str(datetime.datetime.utcnow()) + "]" + " Will skip non image media of type: %s, with id: %s" % (elem.get("type"), id))
                        continue

                    created_time = elem.get("created_time")
                    author = "@" + elem.get("user", {}).get("username")
                    image_url = elem.get("images", {}).get("standard_resolution", {}).get("url")

                    # Can be null
                    try:
                        caption = elem.get("caption", {}).get("text")
                    except AttributeError as err:
                        print(err)
                        caption = ""

                    if image_url and id and tag.last_media_id != id:
                        print("\n[" + str(datetime.datetime.utcnow()) + "]" + " Found image with data: #%s, \n\tauthor: %s, \n\tcaption: %s, \n\timage: %s" % (id, author, caption, image_url))
                        tag.last_media_id = id

                        image = generate_image(image_url, author, caption, created_time)
                        dumpfile = "%s_%s" % (int(time.time()), id)
                        image.save("temp/%s.png" % dumpfile)

                pagination = content.get("pagination", {})
                min_tag_id = pagination.get("min_tag_id")
                if min_tag_id != None:
                    tag.min_tag_id = min_tag_id

                time.sleep(sleep_interval)
                # print(tag)

        store_tags()

    # except Exception as err:
    #     print(err)
    #     stop_threads()

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
    print("\n\n" + "[" + str(datetime.datetime.utcnow()) + "]" + " Will try to exit gracefully ***\n\n")
    stop_threads();
    sys.exit()
