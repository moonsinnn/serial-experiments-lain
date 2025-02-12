#!/usr/bin/env python3

import requests
import urllib3
import signal
import sys
import os
import logging
import argparse
import time
from tqdm import tqdm
from config import ACCESS_TOKEN, CAPTION_TEMPLATE

# Disable warnings and handle SIGINT
urllib3.disable_warnings()
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
    MAGENTA = "\033[35m"

# Setup argument parser
def setup_argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--start', metavar='123', type=int, required=True, help='First frame you want to upload')
    parser.add_argument('--loop', metavar='40', nargs='?', default=40, type=int, help='Loop value')
    parser.add_argument('--album', metavar='ALBUM_ID', type=str, help='Facebook Album ID')
    parser.add_argument('--dry-run', action='store_true', help='Simulate the upload process')
    parser.add_argument('--multi-photo', type=int, metavar='N', help='Number of photos to upload in a single post (max 4)')
    return parser.parse_args()

# Upload a single photo and publish it immediately
def upload_single_photo_published(image_source, caption, album_id=None):
    url = "https://graph.facebook.com/v22.0/me/photos" if not album_id else f"https://graph.facebook.com/v22.0/{album_id}/photos"
    payload = {
        'access_token': ACCESS_TOKEN,
        'caption': caption,
        'published': 'true',  # Publish immediately
    }

    try:
        with open(image_source, 'rb') as image_file:
            files = {'source': (image_source, image_file)}
            response = requests.post(url, files=files, data=payload)

        if response.status_code == 200:
            tqdm.write(f"{Color.BOLD}{Color.GREEN}Frame uploaded and published successfully{Color.RESET}. Response: {response.json()}")
            return True
        else:
            tqdm.write(f"{Color.BOLD}{Color.RED}Failed to upload and publish frame{Color.RESET}. Status Code: {response.status_code}, Response: {response.json()}")
            return False
    except Exception as e:
        tqdm.write(f"{Color.BOLD}{Color.RED}Error uploading and publishing frame: {e}{Color.RESET}")
        return False

# Upload a single photo without publishing it and return its media_fbid
def upload_single_photo_unpublished(image_source, caption, album_id=None):
    url = "https://graph.facebook.com/v22.0/me/photos" if not album_id else f"https://graph.facebook.com/v22.0/{album_id}/photos"
    payload = {
        'access_token': ACCESS_TOKEN,
        'caption': caption,
        'published': 'false',  # Do not publish, just get media_fbid
    }

    try:
        with open(image_source, 'rb') as image_file:
            files = {'source': (image_source, image_file)}
            response = requests.post(url, files=files, data=payload)

        if response.status_code == 200:
            media_fbid = response.json().get('id')
            if not media_fbid:
                tqdm.write(f"{Color.BOLD}{Color.RED}Failed to get media_fbid{Color.RESET}")
                return None
            tqdm.write(f"{Color.BOLD}{Color.GREEN}Frame uploaded successfully (unpublished){Color.RESET}. Media FBID: {media_fbid}")
            return media_fbid
        else:
            tqdm.write(f"{Color.BOLD}{Color.RED}Failed to upload frame (unpublished){Color.RESET}. Status Code: {response.status_code}, Response: {response.json()}")
            return None
    except Exception as e:
        tqdm.write(f"{Color.BOLD}{Color.RED}Error uploading frame (unpublished): {e}{Color.RESET}")
        return None

# Upload multiple photos in a single post
def upload_multiple_photos(media_fbids, caption):
    url = "https://graph.facebook.com/v22.0/me/feed"
    payload = {
        'access_token': ACCESS_TOKEN,
        'message': caption,
    }

    # Attach media_fbids to the payload
    for i, media_fbid in enumerate(media_fbids):
        payload[f'attached_media[{i}]'] = f'{{"media_fbid":"{media_fbid}"}}'

    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            tqdm.write(f"{Color.BOLD}{Color.GREEN}Multiple photos posted successfully{Color.RESET}. Post ID: {response.json().get('id')}")
        else:
            tqdm.write(f"{Color.BOLD}{Color.RED}Failed to post multiple photos{Color.RESET}. Status Code: {response.status_code}, Response: {response.json()}")
    except Exception as e:
        tqdm.write(f"{Color.BOLD}{Color.RED}Error posting multiple photos: {e}{Color.RESET}")

# Main function to upload frames
def upload_frames(start_frame, loop_count, album_id=None, dry_run=False, multi_photo=None):
    media_fbids = []
    max_photos_per_post = 4  # Facebook allows max 4 photos per post

    for i in tqdm(range(start_frame, start_frame + loop_count), desc="Uploading frames"):
        time.sleep(4)  # Avoid rate limiting
        num = f"{i:04}"
        image_source = f"./frame/frame_{num}.jpg"

        # Check if the frame exists
        if not os.path.exists(image_source):
            tqdm.write(f"{Color.BOLD}{Color.RED}Frame {num} not found{Color.RESET}")
            continue

        caption = CAPTION_TEMPLATE.format(num=num)

        # Dry run mode
        if dry_run:
            tqdm.write(f"{Color.BOLD}{Color.CYAN}Dry Run: Frame {num} would be uploaded{Color.RESET}")
            continue

        # Upload single photo (published or unpublished)
        if multi_photo:
            # Upload unpublished to get media_fbid
            media_fbid = upload_single_photo_unpublished(image_source, caption, album_id)
            if media_fbid:
                media_fbids.append(media_fbid)
                os.remove(image_source)

            # If enough photos are collected, create a multi-photo post
            if len(media_fbids) >= multi_photo:
                upload_multiple_photos(media_fbids[:max_photos_per_post], f"Uploaded {len(media_fbids)} frames: {caption}")
                media_fbids = []  # Reset the list after posting
        else:
            # Upload and publish immediately
            if upload_single_photo_published(image_source, caption, album_id):
                os.remove(image_source)

    # Upload any remaining photos in multi-photo mode
    if multi_photo and media_fbids:
        upload_multiple_photos(media_fbids[:max_photos_per_post], f"Uploaded {len(media_fbids)} frames")

# Entry point of the script
if __name__ == "__main__":
    # Configure logging to file only
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('upload.log'),
        ]
    )

    # Parse arguments
    args = setup_argument_parser()

    # Validate multi-photo argument
    if args.multi_photo and (args.multi_photo < 1 or args.multi_photo > 4):
        tqdm.write(f"{Color.BOLD}{Color.RED}Multi-photo value must be between 1 and 4{Color.RESET}")
        sys.exit(1)

    # Upload frames
    upload_frames(args.start, args.loop, args.album, args.dry_run, args.multi_photo)

    # Print completion message
    tqdm.write(f"{Color.BOLD}Task Done{Color.RESET}")
