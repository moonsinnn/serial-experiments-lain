import os
import subprocess
import logging
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('frame_extraction.log'),
        logging.StreamHandler()
    ]
)

def create_frames_from_video(
    video_path: str,
    output_folder: str,
    frame_rate: int = 2,
    output_format: str = 'jpg',
    frame_prefix: str = 'frame_'
) -> Optional[str]:
    """
    Extract frames from a video file and save them as images.

    :param video_path: Path to the input video file.
    :param output_folder: Directory where the frames will be saved.
    :param frame_rate: Number of frames to extract per second.
    :param output_format: Output image format (e.g., 'jpg', 'png').
    :param frame_prefix: Prefix for the output frame filenames.
    :return: Path to the output folder if successful, None otherwise.
    """
    # Validate input video path
    if not os.path.isfile(video_path):
        logging.error(f"The video file '{video_path}' does not exist.")
        return None

    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    logging.info(f"Output folder: '{output_folder}'")

    # Construct FFmpeg command
    output_pattern = os.path.join(output_folder, f'{frame_prefix}%04d.{output_format}')
    command = [
        'ffmpeg',
        '-i', video_path,               # Input video file
        '-vf', f'fps={frame_rate}',     # Frame rate filter
        '-q:v', '3',                    # Quality level (lower is better)
        '-progress', 'pipe:1',          # Enable progress feedback
        output_pattern                  # Output frame naming pattern
    ]

    # Execute FFmpeg command
    try:
        logging.info("Starting frame extraction...")
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )

        # Capture and log progress
        for line in process.stderr:
            if 'frame=' in line:
                logging.info(line.strip())

        # Wait for the process to complete
        process.wait()

        if process.returncode == 0:
            logging.info(f"Frames extracted successfully to '{output_folder}'")
            return output_folder
        else:
            logging.error(f"Frame extraction failed with return code {process.returncode}.")
            return None

    except FileNotFoundError:
        logging.error("FFmpeg is not installed or not found in the system PATH.")
        return None

def load_config(config_file: str = 'config.ini') -> dict:
    """
    Load configuration from a file.

    :param config_file: Path to the configuration file.
    :return: Dictionary containing configuration settings.
    """
    import configparser

    config = configparser.ConfigParser()
    config.read(config_file)

    return {
        'video_path': config.get('DEFAULT', 'video_path', fallback=None),
        'output_folder': config.get('DEFAULT', 'output_folder', fallback='./frames'),
        'frame_rate': config.getint('DEFAULT', 'frame_rate', fallback=2),
        'output_format': config.get('DEFAULT', 'output_format', fallback='jpg'),
        'frame_prefix': config.get('DEFAULT', 'frame_prefix', fallback='frame_')
    }

def main():
    """Main function to handle user input and frame extraction."""
    # Load configuration
    config = load_config()

    # Get video path from user if not provided in config
    video_path = config.get('video_path')
    if not video_path:
        video_path = input("Enter the path to the video file: ").strip()

    # Extract frames
    result = create_frames_from_video(
        video_path=video_path,
        output_folder=config['output_folder'],
        frame_rate=config['frame_rate'],
        output_format=config['output_format'],
        frame_prefix=config['frame_prefix']
    )

    # Display result
    if result:
        logging.info(f"Frames saved in: {result}")
    else:
        logging.error("Frame extraction failed.")

if __name__ == "__main__":
    main()
