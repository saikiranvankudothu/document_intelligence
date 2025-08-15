import os

# Directory to store uploaded files
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

# Create upload dir if missing
os.makedirs(UPLOAD_DIR, exist_ok=True)
