import os

def list_files(startpath):
    for root, dirs, files in os.walk(startpath):
        print(f"Directory: {root}")
        for file in files:
            print(os.path.join(root, file))

list_files(r"M:\Research\Peanut_data\data")