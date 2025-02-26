import os
import shutil
import cv2

def extract_frames(video_path, save_folder, fps=15, interval=1):
    """Extract frames at specified time intervals from a video."""
    print(f"Opening video: {video_path}")
    
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"❌ Error: Could not open video {video_path}")
        return
    else:
        print(f"✅ Successfully opened video: {video_path}")
    
    frame_rate = int(cap.get(cv2.CAP_PROP_FPS))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    if frame_rate == 0:
        frame_rate = fps
    
    frame_interval = frame_rate * interval
    print(f"Video FPS: {frame_rate}, Total Frames: {total_frames}, Extracting every {interval}s")
    
    frame_count = 0
    save_count = 0
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        if frame_count % frame_interval == 0:
            filename = os.path.join(save_folder, f"frame_{save_count:04d}.png")
            success = cv2.imwrite(filename, frame)
            if success:
                print(f"✅ Frame saved: {filename}")
            else:
                print(f"❌ Frame save failed: {filename}")
            save_count += 1
        frame_count += 1
    
    cap.release()
    print(f"Total frames saved: {save_count} to {save_folder}")

def organize_data(main_directory, output_directory, fps=15, interval=1):
    """Organize RGB and Depth video data into structured directories."""
    print(f"Processing data from {main_directory} and saving to {output_directory}")
    print(f"Using parameters - FPS: {fps}, Frame Extraction Interval: {interval} seconds")
    
    if not os.path.exists(main_directory):
        print(f"❌ Error: Directory {main_directory} does not exist!")
        return
    
    print(f"Files in {main_directory}: {os.listdir(main_directory)}")
    
    os.makedirs(output_directory, exist_ok=True)
    rgb_output = os.path.join(output_directory, "rgb_frames")
    depth_output = os.path.join(output_directory, "depth_frames")
    calibration_output = os.path.join(output_directory, "calibration")
    
    os.makedirs(rgb_output, exist_ok=True)
    os.makedirs(depth_output, exist_ok=True)
    os.makedirs(calibration_output, exist_ok=True)
    
    rgb_video_path = os.path.join(main_directory, "RGB_video.avi")
    depth_video_path = os.path.join(main_directory, "Depth_video.avi")
    calibration_file = os.path.join(main_directory, "calibration_params.txt")
    
    if os.path.exists(rgb_video_path):
        print(f"✅ RGB Video found: {rgb_video_path}")
        extract_frames(rgb_video_path, rgb_output, fps, interval)
    else:
        print(f"❌ RGB Video missing in {main_directory}")
    
    if os.path.exists(depth_video_path):
        print(f"✅ Depth Video found: {depth_video_path}")
        extract_frames(depth_video_path, depth_output, fps, interval)
    else:
        print(f"❌ Depth Video missing in {main_directory}")
    
    if os.path.exists(calibration_file):
        dest_calibration_file = os.path.join(calibration_output, "calibration_params.txt")
        shutil.copy(calibration_file, dest_calibration_file)
        print(f"✅ Moved calibration file to {dest_calibration_file}")
    else:
        print(f"❌ Calibration File missing in {main_directory}")
    
    print("✅ Data extraction and organization complete!")

# Example usage
main_directory = "C:\ZED\DataCollection\Vidalia\Session_20250221_143736"  # Change this to your dataset path
output_directory = "M:\Research\Data\Weeds\Vidalia_visit1\Datasample9"  # Change to the desired output path
fps = 15  # Default FPS of your camera
interval = 1  # Extract 1 frame per second

organize_data(main_directory, output_directory, fps, interval)





# main_directory = r"C:\ZED\DataCollection\Testing\Session_20250220_175412"  # Change this to your actual dataset path
# output_directory = r"M:\Research\Data\Weeds\Vidalia_visit1\Datasample1_handheld"  # Change this to where you want processed data stored