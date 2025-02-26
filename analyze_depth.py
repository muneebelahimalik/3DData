import os
import shutil
import cv2
import numpy as np
import open3d as o3d

def load_camera_intrinsics(calibration_file):
    """Load camera intrinsic parameters from the calibration file."""
    with open(calibration_file, 'r') as f:
        lines = f.readlines()
    
    fx, fy, cx, cy = None, None, None, None
    for line in lines:
        if "fx:" in line and "fy:" in line:
            parts = line.replace("fx:", "").replace("fy:", "").split(",")
            fx, fy = map(float, parts)
        elif "cx:" in line and "cy:" in line:
            parts = line.replace("cx:", "").replace("cy:", "").split(",")
            cx, cy = map(float, parts)
        if fx is not None and fy is not None and cx is not None and cy is not None:
            break
    
    if fx is None or fy is None or cx is None or cy is None:
        raise ValueError("❌ Could not find valid intrinsic parameters in calibration file.")
    
    return fx, fy, cx, cy

def depth_to_point_cloud(depth_image_path, calibration_file):
    """Convert a depth image to a 3D point cloud using camera intrinsics and visualize it."""
    fx, fy, cx, cy = load_camera_intrinsics(calibration_file)
    
    depth = cv2.imread(depth_image_path, cv2.IMREAD_UNCHANGED)

    if depth is None:
        print(f"❌ Error: Could not load depth image {depth_image_path}")
        return

    if len(depth.shape) == 3:  # If depth has more than one channel, extract the first one
        print(f"⚠️ Warning: Depth image has {depth.shape[2]} channels, extracting the first one.")
        depth = depth[:, :, 0]  # Take the first channel

    
    h, w = depth.shape
    points = []
    
    for v in range(h):
        for u in range(w):
            Z = depth[v, u] * 0.001  # Convert depth to meters
            if Z > 0:
                X = (u - cx) * Z / fx
                Y = (v - cy) * Z / fy
                points.append([X, Y, Z])
    
    points = np.array(points)
    
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)
    
    print("✅ Point cloud generated. Now displaying...")
    o3d.visualization.draw_geometries([pcd])

# Example usage
depth_image_path = r"M:\Research\Data\Weeds\Vidalia_visit1\Chosen\01\frame_0078_depth.png"
calibration_file = r"M:\Research\Data\Weeds\Vidalia_visit1\Chosen\01\calibration_params.txt"
depth_to_point_cloud(depth_image_path, calibration_file)
