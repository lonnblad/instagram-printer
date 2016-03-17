#!/usr/bin/env python

import urllib, cStringIO
import textwrap
import datetime
import PIL
import string
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw

# Styling
background_color = (255, 255, 255, 0)
text_color = (0,0,0,255)
text_size_title = 28
text_size_info = 22
text_container_height = 192
text_padding = 15
info_max_lines = 4

def generate_image(image_url, title, info, created_time):
    # Load external image
    fp = cStringIO.StringIO(urllib.urlopen(image_url).read())
    img = Image.open(fp).convert('RGBA')
    width, height = img.size

    # Create canvas and draw image onto it
    wrapper = Image.new('RGBA', (width, height + text_container_height), background_color)
    wrapper.paste(img, (0, 0, width, height))

    draw = ImageDraw.Draw(wrapper)

    # Font + Position for title and print it
    font_title = ImageFont.truetype('fonts/Bold.ttf', text_size_title)
    title_position = (text_padding, height + text_padding)
    draw.text(title_position, title, fill=text_color, font=font_title)

    # Font + Position for info
    font_info = ImageFont.truetype('fonts/Regular.ttf', text_size_info)
    info_position = (title_position[0], title_position[1] + font_info.getsize(title)[1] + text_padding)

    # Trim nonascii chars
    info = filter(lambda x: x in string.printable, info)

    # Calc width and lines to print
    chars_row = int((float(width - text_padding * 2) / float(font_info.getsize(info)[0])) * len(info))
    lines = textwrap.wrap(info, width=chars_row)

    # And nice ending if its to long
    if len(lines) > info_max_lines:
        lines[info_max_lines-1] = lines[info_max_lines-1][:-3] + "..."

    # Print all info lines
    offset = 0
    for line in lines[:info_max_lines]:
        draw.text((info_position[0], info_position[1] + offset), line, font=font_info, fill=text_color)
        offset += font_info.getsize(line)[1] + text_padding / 3

    # Format and print readable time
    if created_time:
        readable_time = datetime.datetime.fromtimestamp(int(created_time)).strftime('%B %d, %Y at %H:%M')
        time_position_offset = int((font_title.getsize(title)[1] - font_info.getsize(readable_time)[1]) / 2.)
        time_position = (
            width - text_padding - font_info.getsize(readable_time)[0] - time_position_offset,
            height + text_padding + time_position_offset
        )

        draw.text(time_position, readable_time, fill=text_color, font=font_info)

    return wrapper

def add_corners(im, rad):
    circle = Image.new('L', (rad * 2, rad * 2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, rad * 2, rad * 2), fill=255)
    alpha = Image.new('L', im.size, "white")
    w, h = im.size
    alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
    alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))
    alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
    alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad))
    im.putalpha(alpha)

    return im

if __name__ == '__main__':
    profile_image = "https://scontent.cdninstagram.com/hphotos-xft1/t51.2885-19/s150x150/11821753_1005084186188899_95473637_a.jpg"
    image_url = "https://scontent.cdninstagram.com/hphotos-xft1/t51.2885-15/s640x640/sh0.08/e35/12338796_1660400294217681_1819046271_n.jpg"
    profile_name = "@mattiasjam"
    info = "In this code datetime.datetime can look strange, but 1st datetime is module name and 2nd is class name. So datetime.datetime.fromtimestamp is fromtimestamp method of datetime class from datetime module."
    created_time = "1449771741"

    fp = cStringIO.StringIO(urllib.urlopen(profile_image).read())
    img = Image.open(fp).convert('RGBA')
    width, height = img.size
    
    img = add_corners(img, width / 2)
    # Create canvas and draw image onto it
    #wrapper = Image.new('RGBA', (width, height), background_color)
    #wrapper.paste(img, (0, 0, width, height))

    #draw = ImageDraw.Draw(wrapper)

#    r = width / 2
#    x = width / 2
#    y = height / 2
#    draw.ellipse((x-r, y-r, x+r, y+r), outline=(255,255,255))



    img.save("ko.png")

    #image = generate_image(image_url, profile_name, info, created_time)
    #image.show()
