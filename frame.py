import os
import subprocess

def create_frames_from_video(video_path: str, output_folder: str, frame_rate: int = 1) -> None:
    """
    Extract frames from a video file and save them as JPEG images.

    :param video_path: Path to the input video file.
    :param output_folder: Directory where the frames will be saved.
    :param frame_rate: Number of frames to extract per second.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    command = [
        'ffmpeg',
        '-i', video_path,
        '-vf', f'fps={frame_rate}',
        os.path.join(output_folder, 'frame_%04d.jpg')
    ]
    
    try:
        subprocess.run(command, check=True)
        print(f"Frames extracted successfully to {output_folder}")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while extracting frames: {e}")

# Example usage
video_path = input("Enter the path to the video file: ")
output_folder = './frames'
create_frames_from_video(video_path, output_folder, frame_rate=1)
