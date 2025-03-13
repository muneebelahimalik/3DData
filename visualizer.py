import open3d as o3d

# Load the .ply file
ply_file_path = r"M:\Research\Data\Weeds\Vidalia2\01\point_cloud_67\frame_0067.ply"  # Replace with your .ply file path
point_cloud = o3d.io.read_point_cloud(ply_file_path)

# Check if the point cloud is loaded correctly
if not point_cloud:
    print("Failed to load the .ply file.")
else:
    print("Point cloud loaded successfully.")
    print(f"Number of points: {len(point_cloud.points)}")

    # Visualize the point cloud
    o3d.visualization.draw_geometries([point_cloud])