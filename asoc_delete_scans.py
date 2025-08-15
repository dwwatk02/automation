#!/usr/bin/env python3

import requests
import datetime

# ---- Configuration ----
API_BASE = "https://cloud.appscan.com"  # adjust to your region/server
API_KEY_ID = ""
API_KEY_SECRET = ""

# User-provided cutoff date (YYYY-MM-DD)
import sys
if len(sys.argv) != 2:
    print("Usage: python delete_old_scans.py YYYY-MM-DD")
    sys.exit(1)

cutoff_str = sys.argv[1]
cutoff_date = datetime.datetime.strptime(cutoff_str, "%Y-%m-%d")

# ---- 1. Authenticate ----
login_url = f"{API_BASE}/api/v4/Account/ApiKeyLogin"
login_resp = requests.post(login_url, json={
    "KeyId": API_KEY_ID,
    "KeySecret": API_KEY_SECRET
})
login_resp.raise_for_status()
token = login_resp.json().get("Token")
headers = {"Authorization": f"Bearer {token}"}

# ---- 2. Retrieve scans ----
# Replace with actual endpoint found in Swagger—for example:
scans_url = f"{API_BASE}/api/v4/Scans"  # tweak as needed
resp = requests.get(scans_url, headers=headers)
resp.raise_for_status()
scans = resp.json().get("Items", [])  # adjust key as appropriate

# ---- 3. Filter and delete older scans ----
to_delete = []
for scan in scans:
    created_str = scan.get("CreatedAt")
    scan_id = scan.get("Id")
    if not created_str or not scan_id:
        continue
    # Assume ISO format, adjust parsing if needed
    created_dt = datetime.datetime.fromisoformat(created_str.rstrip("Z"))
    if created_dt < cutoff_date:
        to_delete.append(scan_id)

print(f"Found {len(to_delete)} scans older than {cutoff_str}. Deleting...")

for sid in to_delete:
    del_url = f"{API_BASE}/api/v4/Scans/{sid}"  # adjust as per actual API
    dresp = requests.delete(del_url, headers=headers)
    if dresp.status_code in (200, 204):
        print(f"Deleted scan {sid}")
    else:
        print(f"Failed to delete scan {sid}: {dresp.status_code} {dresp.text}")
