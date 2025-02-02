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

# Disable SSL warnings and handle SIGINT (Ctrl+C)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
signal.signal(signal.SIGINT, lambda x, y: sys.exit(1))

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
    MAGENTA = '\033[35m'

# Set up argument parser
def setup_argument_parser():
    parser = argparse.ArgumentParser(description="Upload frames to Facebook.")
    parser.add_argument(
        '--start', 
        metavar='START_FRAME', 
        type=int, 
        required=True, 
        help='First frame number to upload (e.g., 123)'
    )
    parser.add_argument(
        '--loop', 
        metavar='LOOP_COUNT', 
        type=int, 
        default=40, 
        help='Number of frames to upload (default: 40)'
    )
    return parser.parse_args()

# Upload frames to Facebook
def upload_frames(start_frame, loop_count):
    url = "https://graph.facebook.com/v21.0/me/photos"

    for i in range(start_frame, start_frame + loop_count):
        time.sleep(3)  # Delay to avoid rate limiting
        frame_number = f"{i:04}"
        image_path = f"./frame/frame_{frame_number}.jpg"
        caption = CAPTION_TEMPLATE.format(num=frame_number)

        payload = {
            'access_token': ACCESS_TOKEN,
            'caption': caption,
            'published': 'true',
        }

        try:
            with open(image_path, 'rb') as image_file:
                files = {'source': (image_path, image_file)}
                response = requests.post(url, files=files, data=payload, verify=False)

            if response.status_code == 200:
                logging.debug(f"{Color.BOLD}{Color.GREEN}Frame {frame_number} Uploaded{Color.RESET}. {response.json()}")
                os.remove(image_path)  # Delete the frame after successful upload
            else:
                logging.error(f"{Color.BOLD}{Color.RED}Failed to Upload Frame {frame_number}{Color.RESET}. {response.json()}")
                break  # Stop uploading if an error occurs

        except FileNotFoundError:
            logging.error(f"{Color.BOLD}{Color.RED}File not found: {image_path}{Color.RESET}")
            break
        except Exception as e:
            logging.error(f"{Color.BOLD}{Color.RED}An error occurred: {e}{Color.RESET}")
            break

# Entry point of the script
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
    args = setup_argument_parser()
    upload_frames(args.start, args.loop)
    print(f"{Color.BOLD}Task Done{Color.RESET}")
