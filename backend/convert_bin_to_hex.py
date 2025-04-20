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
bin_files = ["data_level0.bin", "header.bin", "length.bin", "link_lists.bin"]

# Convert binary files to hex
for file in bin_files:
    path = os.path.join(bin_subdir, file)
    if os.path.exists(path):
        with open(path, "rb") as f:
            hex_data = f.read().hex()  # Convert entire file to hex
            print(f"\n🔹 {file} (Hex Data - First 100 chars):\n{hex_data[:100]}\n")
    else:
        print(f"⚠️ {file} not found at {path}")
