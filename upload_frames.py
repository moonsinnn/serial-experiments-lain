#!/usr/bin/env python3
"""
Script untuk mengupload frame ke Facebook menggunakan Graph API.
Mendukung upload single photo, multiple photos, dan dry-run mode.
"""

import signal
import sys
import os
import argparse
import time
import httpx
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
    """
    Class untuk menambahkan warna pada output terminal.
    """

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

    @staticmethod
    def apply(color, text):
        """
        Mengaplikasikan warna ke teks.
        """
        return f"{color}{text}{Color.RESET}"

    @staticmethod
    def bold(text):
        """
        Membuat teks menjadi bold.
        """
        return f"{Color.BOLD}{text}{Color.RESET}"

def setup_argument_parser():
    """
    Setup argument parser untuk command-line arguments.
    """
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

async def upload_single_photo_published(image_source, caption, album_id=None, retries=3):
    """
    Upload single photo dan publish secara langsung.
    """
    url = f"{BASE_URL}/me/photos" if not album_id else f"{BASE_URL}/{album_id}/photos"
    payload = {
        "access_token": ACCESS_TOKEN,
        "caption": caption,
        "published": "true",
    }

    for attempt in range(retries):
        try:
            async with httpx.AsyncClient() as client:
                with open(image_source, "rb") as image_file:
                    files = {"source": (image_source, image_file)}
                    response = await client.post(url, data=payload, files=files, timeout=10)

                if response.status_code == 200:
                    tqdm.write(
                        Color.apply(
                            Color.GREEN,
                            "Frame uploaded and published successfully. "
                            f"Response: {response.json()}",
                        )
                    )
                    return True
                tqdm.write(
                    Color.apply(
                        Color.RED,
                        f"Attempt {attempt + 1} failed to upload and publish frame. "
                        f"Status Code: {response.status_code}, Response: {response.json()}",
                    )
                )
        except httpx.RequestError as e:
            tqdm.write(
                Color.apply(
                    Color.RED,
                    f"Attempt {attempt + 1} error uploading and publishing frame: {e}",
                )
            )
        time.sleep(2)
    return False

async def upload_single_photo_unpublished(image_source, caption, album_id=None, retries=3):
    """
    Upload single photo tanpa publish dan kembalikan media_fbid.
    """
    url = f"{BASE_URL}/me/photos" if not album_id else f"{BASE_URL}/{album_id}/photos"
    payload = {
        "access_token": ACCESS_TOKEN,
        "caption": caption,
        "published": "false",
    }

    for attempt in range(retries):
        try:
            async with httpx.AsyncClient() as client:
                with open(image_source, "rb") as image_file:
                    files = {"source": (image_source, image_file)}
                    response = await client.post(url, data=payload, files=files, timeout=10)

                if response.status_code == 200:
                    media_fbid = response.json().get("id")
                    if media_fbid:
                        tqdm.write(
                            Color.apply(
                                Color.GREEN,
                                f"Frame uploaded successfully (unpublished). "
                                f"Media FBID: {media_fbid}",
                            )
                        )
                        return media_fbid
                    tqdm.write(Color.apply(Color.RED, "Failed to get media_fbid"))
                else:
                    tqdm.write(
                        Color.apply(
                            Color.RED,
                            f"Attempt {attempt + 1} failed to upload frame (unpublished). "
                            f"Status Code: {response.status_code}, Response: {response.json()}",
                        )
                    )
        except httpx.RequestError as e:
            tqdm.write(
                Color.apply(
                    Color.RED,
                    f"Attempt {attempt + 1} error uploading frame (unpublished): {e}",
                )
            )
        time.sleep(2)
    return None

async def upload_multiple_photos(media_fbids, caption):
    """
    Upload multiple photos dalam satu post.
    """
    url = f"{BASE_URL}/me/feed"
    payload = {
        "access_token": ACCESS_TOKEN,
        "message": caption,
    }

    for i, media_fbid in enumerate(media_fbids):
        payload[f"attached_media[{i}]"] = f'{{"media_fbid":"{media_fbid}"}}'

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=payload, timeout=10)
            if response.status_code == 200:
                tqdm.write(
                    Color.apply(
                        Color.GREEN,
                        f"Multiple photos posted successfully. "
                        f"Post ID: {response.json().get('id')}",
                    )
                )
            else:
                tqdm.write(
                    Color.apply(
                        Color.RED,
                        f"Failed to post multiple photos. Status Code: {response.status_code}, "
                        f"Response: {response.json()}",
                    )
                )
    except httpx.RequestError as e:
        tqdm.write(Color.apply(Color.RED, f"Error posting multiple photos: {e}"))

async def upload_frames(start_frame, loop_count, album_id=None, dry_run=False, multi_photo=None):
    """
    Fungsi utama untuk mengupload frames.
    """
    media_fbids = []
    success_count = 0
    fail_count = 0

    for i in tqdm(range(start_frame, start_frame + loop_count), desc="Uploading frames"):
        time.sleep(2)
        num = f"{i:04}"
        image_source = f"./frames/frame_{num}.jpg"

        if not os.path.exists(image_source):
            tqdm.write(Color.apply(Color.RED, f"Frame {num} not found"))
            fail_count += 1
            continue

        caption = CAPTION_TEMPLATE.format(num=num)

        if dry_run:
            tqdm.write(Color.apply(Color.CYAN, f"Dry Run: Frame {num} would be uploaded"))
            success_count += 1
            continue

        if multi_photo:
            media_fbid = await upload_single_photo_unpublished(image_source, caption, album_id)
            if media_fbid:
                media_fbids.append(media_fbid)
                os.remove(image_source)
                success_count += 1

            if len(media_fbids) >= multi_photo:
                await upload_multiple_photos(
                    media_fbids[:MAX_PHOTOS_PER_POST],
                    f"Uploaded {len(media_fbids)} frames: {caption}",
                )
                media_fbids = []
        else:
            if await upload_single_photo_published(image_source, caption, album_id):
                os.remove(image_source)
                success_count += 1
            else:
                fail_count += 1

    if multi_photo and media_fbids:
        await upload_multiple_photos(
            media_fbids[:MAX_PHOTOS_PER_POST], f"Uploaded {len(media_fbids)} frames"
        )

    tqdm.write(Color.apply(Color.BOLD, "Upload Summary:"))
    tqdm.write(Color.apply(Color.GREEN, f"Successfully uploaded: {success_count} frames"))
    tqdm.write(Color.apply(Color.RED, f"Failed to upload: {fail_count} frames"))

async def main():
    """
    Fungsi utama untuk menjalankan script.
    """
    args = setup_argument_parser()

    if args.multi_photo and (args.multi_photo < 1 or args.multi_photo > MAX_PHOTOS_PER_POST):
        tqdm.write(
            Color.apply(
                Color.RED,
                f"Multi-photo value must be between 1 and {MAX_PHOTOS_PER_POST}",
            )
        )
        sys.exit(1)

    await upload_frames(args.start, args.loop, args.album, args.dry_run, args.multi_photo)
    tqdm.write(Color.apply(Color.BOLD, "Task Done"))

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
