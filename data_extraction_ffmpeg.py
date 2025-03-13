import os
import shutil
import subprocess  # <-- Important for calling ffmpeg

###############################################################################
# CONFIGURE YOUR FFMPEG PATH HERE
###############################################################################
FFMPEG_PATH = r"C:\ffmpeg\ffmpeg-7.1-essentials_build\bin\ffmpeg.exe"  # <-- Change to your actual ffmpeg.exe location

def extract_frames_ffmpeg(video_path, save_folder, fps=15, interval=1, is_depth=False):
    """
    Extract frames using FFmpeg from a video file (FFV1 in MKV).
    - video_path: path to the .mkv file
    - save_folder: folder to save extracted frames
    - fps: the *original* capture FPS (not always used, but kept for reference)
    - interval: extract 1 frame every 'interval' seconds
    - is_depth: if True, treat as 16-bit depth video and preserve 16-bit PNG
    """
    print(f"Opening video with FFmpeg: {video_path}")
    if not os.path.exists(video_path):
        print(f"❌ Error: Could not find {video_path}")
        return

    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    # Calculate how many frames per second to extract
    # If original fps=15 and interval=1 => extraction_fps=1 => 1 frame/second
    # If interval=2 => extraction_fps=0.5 => 1 frame every 2 seconds
    extraction_fps = 1.0 / interval

    # Output file pattern for saving PNG frames
    out_pattern = os.path.join(save_folder, "frame_%04d.png")

    # Build the ffmpeg command:
    cmd = [
        FFMPEG_PATH,         # Use the full path to ffmpeg.exe here
        "-y",                # Overwrite existing output
        "-i", video_path,    # Input video
        "-vf", f"fps={extraction_fps}",
        "-vsync", "0"        # Avoid generating duplicate frames
    ]

    # If this is a 16-bit depth video, we force gray16le output
    if is_depth:
        cmd += ["-pix_fmt", "gray16le"]

    # Finally, specify the output pattern (PNG files)
    cmd += [out_pattern]

    print(f"Running FFmpeg command: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True)
        print(f"✅ Frames extracted to {save_folder}")
    except subprocess.CalledProcessError as e:
        print(f"❌ FFmpeg failed: {e}")


def organize_data(main_directory, output_directory, fps=15, interval=1):
    """Organize RGB and Depth video data into structured directories, using FFmpeg to decode."""
    print(f"Processing data from {main_directory} and saving to {output_directory}")
    print(f"Using parameters - FPS: {fps}, Frame Extraction Interval: {interval} second(s)")

    if not os.path.exists(main_directory):
        print(f"❌ Error: Directory {main_directory} does not exist!")
        return

    # Create subfolders for the extracted frames
    os.makedirs(output_directory, exist_ok=True)
    rgb_output = os.path.join(output_directory, "rgb_frames")
    depth_output = os.path.join(output_directory, "depth_frames")
    calibration_output = os.path.join(output_directory, "calibration")

    os.makedirs(rgb_output, exist_ok=True)
    os.makedirs(depth_output, exist_ok=True)
    os.makedirs(calibration_output, exist_ok=True)

    # Expect these filenames in main_directory
    rgb_video_path = os.path.join(main_directory, "RGB_video.mkv")
    depth_video_path = os.path.join(main_directory, "Depth_video.mkv")
    calibration_file = os.path.join(main_directory, "calibration_params.txt")

    # Extract RGB frames (8-bit)
    if os.path.exists(rgb_video_path):
        print(f"✅ RGB Video found: {rgb_video_path}")
        extract_frames_ffmpeg(rgb_video_path, rgb_output, fps, interval, is_depth=False)
    else:
        print(f"❌ RGB Video missing in {main_directory}")

    # Extract Depth frames (16-bit)
    if os.path.exists(depth_video_path):
        print(f"✅ Depth Video found: {depth_video_path}")
        extract_frames_ffmpeg(depth_video_path, depth_output, fps, interval, is_depth=True)
    else:
        print(f"❌ Depth Video missing in {main_directory}")

    # Copy calibration file if present
    if os.path.exists(calibration_file):
        dest_calibration_file = os.path.join(calibration_output, "calibration_params.txt")
        shutil.copy(calibration_file, dest_calibration_file)
        print(f"✅ Copied calibration file to {dest_calibration_file}")
    else:
        print(f"❌ Calibration File missing in {main_directory}")

    print("✅ Data extraction and organization complete!")


# Example usage
if __name__ == "__main__":
    main_directory = r"C:\ZED\DataCollection\Vidalia2\Session_20250304_104505"  # Example path
    output_directory = r"M:\Research\Data\Weeds\Vidalia2\02"                # Example output
    fps = 15       # For reference, original camera FPS
    interval = 0.4348   # Extract 1 frame every 0.4348 seconds = 2.3 FPS

    organize_data(main_directory, output_directory, fps, interval)
