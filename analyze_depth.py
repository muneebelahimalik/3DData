import os
import cv2
import numpy as np
import open3d as o3d

def load_camera_intrinsics(calibration_file):
    """
    Load camera intrinsic parameters from the calibration file with improved robustness.
    
    Args:
        calibration_file (str): Path to the calibration parameters file.
    
    Returns:
        tuple: Focal lengths (fx, fy) and optical center (cx, cy)
    """
    try:
        with open(calibration_file, 'r') as f:
            content = f.read()
        
        # More flexible parsing using regex or multiple parsing strategies
        import re
        
        # Try different parsing methods
        def extract_param(param_name):
            # First try exact match
            exact_match = re.search(rf"{param_name}:\s*([\d.]+)", content)
            if exact_match:
                return float(exact_match.group(1))
            
            # Then try comma-separated values
            comma_match = re.search(rf"{param_name}:\s*([\d.]+)\s*[,\n]", content)
            if comma_match:
                return float(comma_match.group(1))
            
            return None
        
        # Extract parameters
        fx = extract_param('fx')
        fy = extract_param('fy')
        cx = extract_param('cx')
        cy = extract_param('cy')
        
        if not all([fx, fy, cx, cy]):
            raise ValueError("Could not extract all intrinsic parameters")
        
        return fx, fy, cx, cy
    
    except Exception as e:
        print(f"❌ Error parsing calibration file: {e}")
        raise

def preprocess_depth_image(depth_image):
    """
    Preprocess depth image to remove invalid and noisy depth values.
    
    Args:
        depth_image (np.ndarray): Input depth image
    
    Returns:
        np.ndarray: Preprocessed depth image
    """
    # Ensure single channel
    if len(depth_image.shape) > 2:
        depth_image = depth_image[:, :, 0]
    
    # Remove invalid depth values (zero or extremely large)
    depth_image = np.where(
        (depth_image > 0) & (depth_image < 10000),  # Adjust threshold as needed
        depth_image, 
        0
    )
    
    # Optional: Apply median filtering to reduce noise
    depth_image = cv2.medianBlur(depth_image.astype(np.uint16), 3)
    
    return depth_image

def depth_to_point_cloud(
    depth_image_path, 
    calibration_file, 
    save_dir=None, 
    depth_scale=0.001,  # Configurable depth scale
    min_depth=0.1,      # Minimum valid depth
    max_depth=10.0      # Maximum valid depth
):
    """
    Convert depth image to a cleaned 3D point cloud with advanced preprocessing.
    
    Args:
        depth_image_path (str): Path to depth image
        calibration_file (str): Path to camera calibration file
        save_dir (str, optional): Directory to save point cloud
        depth_scale (float): Scale factor to convert depth to meters
        min_depth (float): Minimum valid depth in meters
        max_depth (float): Maximum valid depth in meters
    
    Returns:
        o3d.geometry.PointCloud: Processed point cloud
    """
    # Load camera intrinsics
    fx, fy, cx, cy = load_camera_intrinsics(calibration_file)
    
    # Read depth image
    depth = cv2.imread(depth_image_path, cv2.IMREAD_UNCHANGED)
    if depth is None:
        raise ValueError(f"❌ Could not load depth image: {depth_image_path}")
    
    # Preprocess depth image
    depth = preprocess_depth_image(depth)
    
    h, w = depth.shape
    points = []
    
    # Vectorized point cloud generation
    for v in range(h):
        for u in range(w):
            Z = depth[v, u] * depth_scale
            
            # Filter depth values
            if min_depth < Z < max_depth:
                X = (u - cx) * Z / fx
                Y = (v - cy) * Z / fy
                points.append([X, Y, Z])
    
    # Convert to point cloud
    points = np.array(points)
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)
    
    # Advanced noise removal
    print("🧹 Applying advanced noise removal...")
    
    # Statistical outlier removal
    pcd, _ = pcd.remove_statistical_outlier(
        nb_neighbors=20,   # Number of neighbors to analyze
        std_ratio=1.5      # Standard deviation multiplier (lower = more aggressive)
    )
    
    # Optional: Radius outlier removal for additional cleaning
    pcd, _ = pcd.remove_radius_outlier(
        nb_points=16,      # Minimum points in neighborhood
        radius=0.05        # Radius of neighborhood
    )
    
    # Optional: Downsampling to reduce point cloud size
    pcd = pcd.voxel_down_sample(voxel_size=0.01)
    
    # Visualization (optional)
    o3d.visualization.draw_geometries([pcd])
    
    # Save point cloud
    if save_dir:
        os.makedirs(save_dir, exist_ok=True)
        file_name = os.path.splitext(os.path.basename(depth_image_path))[0] + ".ply"
        save_path = os.path.join(save_dir, file_name)
        o3d.io.write_point_cloud(save_path, pcd)
        print(f"✅ Point cloud saved at: {save_path}")
    
    return pcd

# Example usage
if __name__ == "__main__":
    depth_image_path = r"M:\Research\Data\Weeds\Vidalia2\01\depth_frames\frame_0067.png"
    calibration_file = r"M:\Research\Data\Weeds\Vidalia2\01\calibration\calibration_params.txt"
    save_directory = r"M:\Research\Data\Weeds\Vidalia2\01\point_cloud_67"

    try:
        point_cloud = depth_to_point_cloud(
            depth_image_path, 
            calibration_file, 
            save_directory,
            depth_scale=0.001,  # Adjust based on your sensor
            min_depth=0.1,
            max_depth=10.0
        )
    except Exception as e:
        print(f"Error processing depth image: {e}")