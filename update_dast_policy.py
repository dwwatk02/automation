#!/usr/bin/env python3

import os
import sys
from pathlib import Path

import requests

# AppScan on Cloud API v4
BASE_URL = "https://cloud.appscan.com/api/v4"

# Input file containing one scan UUID per line
SCAN_IDS_FILE = "scan_ids.txt"

# Target DAST test policy ID
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

    put_url = f"{BASE_URL}/Scans/Dast/{scan_id}"

    # PUT request model: CustomTestPolicyId belongs
    # inside the Tests object, not at the root level.

    payload = {
        "Tests": {
            "CustomTestPolicyId": NEW_POLICY_ID
        }
    }

    response = session.put(
        put_url,
        json=payload,
        timeout=TIMEOUT
    )

    if not response.ok:
        raise RuntimeError(
            f"HTTP {response.status_code}: {response.text}"
        )

    print(
        f"SUCCESS: Updated DAST test policy "
        f"for scan {scan_id}"
    )


def main():

    if not NEW_POLICY_ID:
        sys.exit(
            "Error: Set ASOC_TEST_POLICY_ID environment variable."
        )

    try:
        scan_ids = read_scan_ids(SCAN_IDS_FILE)

    except Exception as exc:
        sys.exit(f"Error reading scan IDs: {exc}")

    if not scan_ids:
        sys.exit("No scan IDs found in the input file.")

    print(f"Loaded {len(scan_ids)} scan IDs.")
    print(f"Target test policy: {NEW_POLICY_ID}")
    print("-" * 60)

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

    print("\n" + "=" * 40)
    print("UPDATE SUMMARY")
    print("=" * 40)
    print(f"Total:   {len(scan_ids)}")
    print(f"Success: {succeeded}")
    print(f"Failed:  {failed}")


if __name__ == "__main__":
    main()
