# **Documentation: Facebook Frame Uploader**

This Python script is designed to upload frames (images) to Facebook using the Graph API. The script supports several features, including uploading single frames, uploading multiple frames in a single post, and a simulation mode (`dry-run`).

---

## **Requirements**
1. **Python 3**: Ensure Python 3 is installed.
2. **Required Libraries**:
   - `requests`
   - `tqdm`
   - `urllib3`
   - `argparse`
   - `logging`
3. **Facebook Access Token**: The Facebook access token must be stored in a `config.py` file as the `ACCESS_TOKEN` variable.
4. **Caption Template**: The caption template for each frame must be stored in the `config.py` file as the `CAPTION_TEMPLATE` variable.

---

## **File Structure**
- `upload_frames.py`: The main script for uploading frames.
- `config.py`: Configuration file containing `ACCESS_TOKEN` and `CAPTION_TEMPLATE`.
- `frame/`: Directory containing the frames to be uploaded. Frames must be named in the format `frame_XXXX.jpg`, where `XXXX` is the frame number (e.g., `frame_0001.jpg`).

---

## **Usage**

### **1. Running the Script**
The script can be executed using the following command:

```bash
python3 upload_frames.py --start <START_FRAME> --loop <LOOP_COUNT> [OPTIONS]
```

### **2. Available Arguments**
| Argument         | Description                                                                 |
|------------------|-----------------------------------------------------------------------------|
| `--start`        | The first frame to upload (e.g., `100`).                                    |
| `--loop`         | The number of frames to upload (default: `40`).                             |
| `--album`        | The Facebook album ID where frames will be uploaded (optional).             |
| `--dry-run`      | Simulation mode (does not upload frames, only displays logs).               |
| `--multi-photo`  | The number of photos to upload in a single post (maximum 4, optional).      |

### **3. Examples**
- **Uploading Frames**:
  ```bash
  python3 upload_frames.py --start 100 --loop 20
  ```
- **Uploading Frames to a Specific Album**:
  ```bash
  python3 upload_frames.py --start 100 --loop 20 --album ALBUM_ID
  ```
- **Simulation Mode (Dry Run)**:
  ```bash
  python3 upload_frames.py --start 100 --loop 20 --dry-run
  ```
- **Uploading Multiple Frames in a Single Post**:
  ```bash
  python3 upload_frames.py --start 100 --loop 20 --multi-photo 3
  ```

---

## **Features**

### **1. Upload Single Photo**
- Uploads a single frame and publishes it immediately.
- Uses the `upload_single_photo_published` function.

### **2. Upload Multiple Photos**
- Uploads multiple frames in a single post.
- Uses the `upload_single_photo_unpublished` function to obtain `media_fbid` and the `upload_multiple_photos` function to create the post.

### **3. Dry Run Mode**
- Simulates the upload process without actually uploading frames.
- Displays logs to verify the program flow.

### **4. Progress Bar**
- Uses `tqdm` to display a progress bar during the upload process.

### **5. Logging**
- Logs are saved in the `upload.log` file for debugging purposes.

---

## **Main Functions**

### **1. `upload_single_photo_published(image_source, caption, album_id=None)`**
- Uploads a single frame and publishes it immediately.
- **Parameters**:
  - `image_source`: Path to the image file.
  - `caption`: Caption for the frame.
  - `album_id`: Facebook album ID (optional).
- **Return**: `True` if successful, `False` if failed.

### **2. `upload_single_photo_unpublished(image_source, caption, album_id=None)`**
- Uploads a single frame without publishing it and returns the `media_fbid`.
- **Parameters**: Same as `upload_single_photo_published`.
- **Return**: `media_fbid` if successful, `None` if failed.

### **3. `upload_multiple_photos(media_fbids, caption)`**
- Uploads multiple frames in a single post.
- **Parameters**:
  - `media_fbids`: List of `media_fbid` from uploaded frames.
  - `caption`: Caption for the post.

### **4. `upload_frames(start_frame, loop_count, album_id=None, dry_run=False, multi_photo=None)`**
- Main function to upload frames.
- **Parameters**:
  - `start_frame`: The first frame to upload.
  - `loop_count`: The number of frames to upload.
  - `album_id`: Facebook album ID (optional).
  - `dry_run`: Simulation mode (optional).
  - `multi_photo`: The number of photos to upload in a single post (optional).

---

## **Notes**
- Ensure the `ACCESS_TOKEN` is valid and has the necessary permissions.
- Frames must be named in the format `frame_XXXX.jpg` and stored in the `frame/` directory.
- Facebook limits a maximum of 4 photos per post.

---

## **License**
This script is released under the MIT License. Feel free to modify and distribute it as needed.

---

For questions or issues, please open an issue in the repository. 😊
