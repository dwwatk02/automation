#!/usr/bin/env python3

import os
import sys
from pathlib import Path

import requests

# AppScan on Cloud API v4
BASE_URL = "https://cloud.appscan.com/api/v4"

# Input file containing one scan UUID per line
SCAN_IDS_FILE = "scan_ids.txt"

# Target test policy ID
NEW_POLICY_ID = ""

# API credentials
API_KEY_ID = ""
API_KEY_SECRET = ""

TIMEOUT = 60


def create_session():
    if not API_KEY_ID or not API_KEY_SECRET:
        raise RuntimeError(
            "Set ASOC_API_KEY_ID and ASOC_API_KEY_SECRET "
            "environment variables."
        )

    session = requests.Session()
    session.headers.update({
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-Api-Key": f"{API_KEY_ID}:{API_KEY_SECRET}",
    })

    return session


def read_scan_ids(filename):
    path = Path(filename)

    if not path.is_file():
        raise FileNotFoundError(
            f"Scan ID file not found: {filename}"
        )

    return [
        line.strip()
        for line in path.read_text(
            encoding="utf-8-sig"
        ).splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]


def update_scan(session, scan_id):
    # Retrieve the existing DAST scan configuration
    get_url = f"{BASE_URL}/Scans/Dast/{scan_id}"
    response = session.get(get_url, timeout=TIMEOUT)
    response.raise_for_status()

    scan = response.json()

    # Update the test policy while preserving other scan properties
    scan["CustomTestPolicyId"] = NEW_POLICY_ID

    # Submit the full updated DAST scan object
    put_url = f"{BASE_URL}/Scans/Dast/{scan_id}"
    response = session.put(
        put_url,
        json=scan,
        timeout=TIMEOUT
    )
    response.raise_for_status()

    print(f"SUCCESS: Updated scan {scan_id} (HTTP {response.status_code})")


def main():
    if not NEW_POLICY_ID:
        sys.exit(
            "Error: Set ASOC_TEST_POLICY_ID to the target test policy ID."
        )

    try:
        scan_ids = read_scan_ids(SCAN_IDS_FILE)
    except Exception as exc:
        sys.exit(f"Error reading scan IDs: {exc}")

    if not scan_ids:
        sys.exit("No scan IDs found in the input file.")

    print(f"Loaded {len(scan_ids)} scan IDs.")

    try:
        session = create_session()
    except Exception as exc:
        sys.exit(f"Authentication configuration error: {exc}")

    succeeded = 0
    failed = 0

    for scan_id in scan_ids:
        try:
            update_scan(session, scan_id)
            succeeded += 1
        except Exception as exc:
            failed += 1
            print(f"FAILED: Scan {scan_id}: {exc}")

    print("\nUpdate summary")
    print(f"  Total:   {len(scan_ids)}")
    print(f"  Success: {succeeded}")
    print(f"  Failed:  {failed}")


if __name__ == "__main__":
    main()
