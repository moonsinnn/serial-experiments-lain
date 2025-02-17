#!/usr/bin/env python3
import signal
import sys
import os
import argparse
import time
import requests
import urllib3
from tqdm import tqdm
from config import ACCESS_TOKEN, CAPTION_TEMPLATE

# Disable warnings and handle SIGINT
urllib3.disable_warnings()
signal.signal(signal.SIGINT, lambda x, y: sys.exit(1))

# Constants
MAX_PHOTOS_PER_POST = 4
API_VERSION = "v22.0"
BASE_URL = f"https://graph.facebook.com/{API_VERSION}"

# Color class for terminal output
class Color:
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    DARKCYAN = "\033[36m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    RESET = "\033[0m"
    MAGENTA = "\033[35m"

def setup_argument_parser():
    parser = argparse.ArgumentParser(description="Upload frames to Facebook.")
    parser.add_argument(
        "--start",
        metavar="123",
        type=int,
        required=True,
        help="First frame you want to upload",
    )
    parser.add_argument(
        "--loop", metavar="40", nargs="?", default=40, type=int, help="Loop value"
    )
    parser.add_argument(
        "--album", metavar="ALBUM_ID", type=str, help="Facebook Album ID"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Simulate the upload process"
    )
    parser.add_argument(
        "--multi-photo",
        type=int,
        metavar="N",
        help="Number of photos to upload in a single post (max 4)",
    )
    return parser.parse_args()

def upload_single_photo_published(image_source, caption, album_id=None, retries=3):
    url = f"{BASE_URL}/me/photos" if not album_id else f"{BASE_URL}/{album_id}/photos"
    payload = {
        "access_token": ACCESS_TOKEN,
        "caption": caption,
        "published": "true",
    }

    for attempt in range(retries):
        try:
            with open(image_source, "rb") as image_file:
                files = {"source": (image_source, image_file)}
                response = requests.post(url, files=files, data=payload, timeout=10)

            if response.status_code == 200:
                tqdm.write(
                    f"{Color.BOLD}{Color.GREEN}Frame uploaded and published successfully{Color.RESET}. Response: {response.json()}"
                )
                return True
            tqdm.write(
                f"{Color.BOLD}{Color.RED}Attempt {attempt + 1} failed to upload and publish frame{Color.RESET}. Status Code: {response.status_code}, Response: {response.json()}"
            )
        except requests.exceptions.RequestException as e:
            tqdm.write(
                f"{Color.BOLD}{Color.RED}Attempt {attempt + 1} error uploading and publishing frame: {e}{Color.RESET}"
            )
        time.sleep(2)
    return False

def upload_single_photo_unpublished(image_source, caption, album_id=None, retries=3):
    url = f"{BASE_URL}/me/photos" if not album_id else f"{BASE_URL}/{album_id}/photos"
    payload = {
        "access_token": ACCESS_TOKEN,
        "caption": caption,
        "published": "false",
    }

    for attempt in range(retries):
        try:
            with open(image_source, "rb") as image_file:
                files = {"source": (image_source, image_file)}
                response = requests.post(url, files=files, data=payload, timeout=10)

            if response.status_code == 200:
                media_fbid = response.json().get("id")
                if media_fbid:
                    tqdm.write(
                        f"{Color.BOLD}{Color.GREEN}Frame uploaded successfully (unpublished){Color.RESET}. Media FBID: {media_fbid}"
                    )
                    return media_fbid
                tqdm.write(
                    f"{Color.BOLD}{Color.RED}Failed to get media_fbid{Color.RESET}"
                )
            else:
                tqdm.write(
                    f"{Color.BOLD}{Color.RED}Attempt {attempt + 1} failed to upload frame (unpublished){Color.RESET}. Status Code: {response.status_code}, Response: {response.json()}"
                )
        except requests.exceptions.RequestException as e:
            tqdm.write(
                f"{Color.BOLD}{Color.RED}Attempt {attempt + 1} error uploading frame (unpublished): {e}{Color.RESET}"
            )
        time.sleep(2)
    return None

def upload_multiple_photos(media_fbids, caption):
    url = f"{BASE_URL}/me/feed"
    payload = {
        "access_token": ACCESS_TOKEN,
        "message": caption,
    }

    for i, media_fbid in enumerate(media_fbids):
        payload[f"attached_media[{i}]"] = f'{{"media_fbid":"{media_fbid}"}}'

    try:
        response = requests.post(url, data=payload, timeout=10)
        if response.status_code == 200:
            tqdm.write(
                f"{Color.BOLD}{Color.GREEN}Multiple photos posted successfully{Color.RESET}. Post ID: {response.json().get('id')}"
            )
        else:
            tqdm.write(
                f"{Color.BOLD}{Color.RED}Failed to post multiple photos{Color.RESET}. Status Code: {response.status_code}, Response: {response.json()}"
            )
    except requests.exceptions.RequestException as e:
        tqdm.write(
            f"{Color.BOLD}{Color.RED}Error posting multiple photos: {e}{Color.RESET}"
        )

def upload_frames(start_frame, loop_count, album_id=None, dry_run=False, multi_photo=None):
    media_fbids = []
    success_count = 0
    fail_count = 0

    for i in tqdm(range(start_frame, start_frame + loop_count), desc="Uploading frames"):
        time.sleep(2)
        num = f"{i:04}"
        image_source = f"./frames/frame_{num}.jpg"

        if not os.path.exists(image_source):
            tqdm.write(f"{Color.BOLD}{Color.RED}Frame {num} not found{Color.RESET}")
            fail_count += 1
            continue

        caption = CAPTION_TEMPLATE.format(num=num)

        if dry_run:
            tqdm.write(
                f"{Color.BOLD}{Color.CYAN}Dry Run: Frame {num} would be uploaded{Color.RESET}"
            )
            success_count += 1
            continue

        if multi_photo:
            media_fbid = upload_single_photo_unpublished(image_source, caption, album_id)
            if media_fbid:
                media_fbids.append(media_fbid)
                os.remove(image_source)
                success_count += 1

            if len(media_fbids) >= multi_photo:
                upload_multiple_photos(
                    media_fbids[:MAX_PHOTOS_PER_POST],
                    f"Uploaded {len(media_fbids)} frames: {caption}",
                )
                media_fbids = []
        else:
            if upload_single_photo_published(image_source, caption, album_id):
                os.remove(image_source)
                success_count += 1
            else:
                fail_count += 1

    if multi_photo and media_fbids:
        upload_multiple_photos(
            media_fbids[:MAX_PHOTOS_PER_POST], f"Uploaded {len(media_fbids)} frames"
        )

    tqdm.write(f"{Color.BOLD}Upload Summary:{Color.RESET}")
    tqdm.write(
        f"{Color.GREEN}Successfully uploaded: {success_count} frames{Color.RESET}"
    )
    tqdm.write(f"{Color.RED}Failed to upload: {fail_count} frames{Color.RESET}")

if __name__ == "__main__":
    args = setup_argument_parser()

    if args.multi_photo and (args.multi_photo < 1 or args.multi_photo > MAX_PHOTOS_PER_POST):
        tqdm.write(
            f"{Color.BOLD}{Color.RED}Multi-photo value must be between 1 and {MAX_PHOTOS_PER_POST}{Color.RESET}"
        )
        sys.exit(1)

    upload_frames(args.start, args.loop, args.album, args.dry_run, args.multi_photo)
    tqdm.write(f"{Color.BOLD}Task Done{Color.RESET}")
