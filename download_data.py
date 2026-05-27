"""Download Kaggle datasets with legacy API credentials."""
import os
import json
import sys

# Set credentials
os.environ['KAGGLE_USERNAME'] = 'pagadalamohith'
os.environ['KAGGLE_KEY'] = '11a637c1051ecf7aa27a87c47ce8ebc8'

# Also save to ~/.kaggle/kaggle.json
kaggle_dir = os.path.join(os.path.expanduser('~'), '.kaggle')
os.makedirs(kaggle_dir, exist_ok=True)
with open(os.path.join(kaggle_dir, 'kaggle.json'), 'w') as f:
    json.dump({'username': 'pagadalamohith', 'key': '11a637c1051ecf7aa27a87c47ce8ebc8'}, f)

print("[1/4] Credentials configured")

try:
    from kaggle.api.kaggle_api_extended import KaggleApi
    api = KaggleApi()
    api.authenticate()
    print("[2/4] Authenticated successfully")
except Exception as e:
    print(f"[ERROR] Authentication failed: {e}")
    sys.exit(1)

DATA_BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

datasets = [
    ("amritanshuspeaks/jud-ipl", os.path.join(DATA_BASE, "jud-ipl")),
    ("vangmayapurohit/indian-supreme-court-judgments", os.path.join(DATA_BASE, "indian-court")),
]

for i, (ds, dest) in enumerate(datasets, 1):
    os.makedirs(dest, exist_ok=True)
    print(f"\n[3.{i}/4] Downloading {ds}...")
    try:
        api.dataset_download_files(ds, path=dest, unzip=True)
        files = os.listdir(dest)
        print(f"  SUCCESS: {len(files)} files extracted")
        for f in files[:8]:
            fp = os.path.join(dest, f)
            sz = os.path.getsize(fp) if os.path.isfile(fp) else 0
            print(f"    - {f} ({sz/1024:.1f} KB)")
    except Exception as e:
        print(f"  FAILED: {e}")

print("\n[4/4] Done!")
