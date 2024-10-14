#!/usr/bin/env python3
import requests
import urllib3
import signal
import sys
import os
import logging
import argparse
import time
from config import ACCESS_TOKEN, CAPTION_TEMPLATE

# Disable warnings and handle SIGINT
urllib3.disable_warnings()
signal.signal(signal.SIGINT, lambda x, y: sys.exit(1))

# Argument parser setup
def setup_argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--start', metavar='123', type=int, required=True, help='First frame you want to upload')
    parser.add_argument('--loop', metavar='40', nargs='?', default=40, type=int, help='Loop value')
    return parser.parse_args()

# Color class for terminal output
class Color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'
    MAGENTA = "\033[35m"

# Main function to upload frames
def upload_frames(start_frame, loop_count):
    url = "https://graph.facebook.com/v21.0/me/photos"

    for i in range(start_frame, start_frame + loop_count):
        time.sleep(3)
        num = f"{i:04}"
        image_source = f"./frame/frame_{num}.jpg"
        caption = CAPTION_TEMPLATE.format(num=num)

        payload = {
            'access_token': ACCESS_TOKEN,
            'caption': caption,
            'published': 'true',
        }

        with open(image_source, 'rb') as image_file:
            files = {'source': (image_source, image_file)}
            response = requests.post(url, files=files, data=payload)

        if response.status_code == 200:
            logging.debug(f"{Color.BOLD}{Color.GREEN}Frame {num} Uploaded{Color.RESET}. {response.json()}")
            os.remove(image_source)
        else:
            logging.debug(f"{Color.BOLD}{Color.RED}Failed to Upload Frame {num}{Color.RESET}. {response.json()}")
            break

# Entry point of the script
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    args = setup_argument_parser()
    upload_frames(args.start, args.loop)
    print(f"{Color.BOLD}Task Done{Color.RESET}")
