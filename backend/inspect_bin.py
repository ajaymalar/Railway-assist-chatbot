import os
import glob

# Use the correct absolute path
bin_dir = r"S:\CIP\Railway UI\chatbot-ui\backend\chroma_db"

# Find the unique subfolder inside chroma_db
subfolders = glob.glob(os.path.join(bin_dir, "*"))
if not subfolders:
    print("⚠️ No subfolder found inside chroma_db!")
    exit()

# Use the first found subfolder
bin_subdir = subfolders[0]  

# List of expected binary files
bin_files = ["data_level0.bin", "header.bin", "index_metadata.p", "length.bin", "link_lists.bin"]

# Read each file
for file in bin_files:
    path = os.path.join(bin_subdir, file)
    if os.path.exists(path):
        with open(path, "rb") as f:
            data = f.read(100)  # Read first 100 bytes
            print(f"\n🔹 {file} (First 100 bytes):\n{data}\n")
    else:
        print(f"⚠️ {file} not found at {path}")
