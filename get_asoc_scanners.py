#!/usr/bin/env python3

import csv
import requests

# ======================================================
# Configuration
# ======================================================

API_BASE = "https://cloud.appscan.com/api/v4"

KEY_ID = ""
KEY_SECRET = ""

OUTPUT_FILE = "asoc_scan_creators.csv"

# ======================================================
# Authentication
# ======================================================

def get_access_token():

    url = f"{API_BASE}/Account/ApiKeyLogin"

    payload = {
        "KeyId": KEY_ID,
        "KeySecret": KEY_SECRET
    }

    r = requests.post(url, json=payload)
    r.raise_for_status()

    return r.json()["Token"]


# ======================================================
# Get Applications
# ======================================================

def get_apps(token):

    headers = {
        "Authorization": f"Bearer {token}"
    }

    apps = []
    skip = 0

    while True:

        r = requests.get(
            f"{API_BASE}/Apps",
            headers=headers,
            params={
                "$top": 5000,
                "$skip": skip,
                "$select": "Id,Name"
            }
        )

        r.raise_for_status()

        page = r.json()["Items"]

        if not page:
            break

        apps.extend(page)

        if len(page) < 5000:
            break

        skip += 5000

    return apps


# ======================================================
# Get Scans
# ======================================================

def get_scans(token):

    headers = {
        "Authorization": f"Bearer {token}"
    }

    scans = []
    skip = 0

    while True:

        r = requests.get(
            f"{API_BASE}/Scans",
            headers=headers,
            params={
                "$top": 500,
                "$skip": skip,
                "$select": "CreatedBy,AppId",
                "$expand": "CreatedBy"
            }
        )

        r.raise_for_status()

        page = r.json()["Items"]

        if not page:
            break

        scans.extend(page)

        if len(page) < 500:
            break

        skip += 500

    return scans


# ======================================================
# Main
# ======================================================

def main():

    print("Authenticating...")
    token = get_access_token()

    print("Retrieving applications...")
    apps = get_apps(token)

    print(f"Found {len(apps)} applications")

    app_lookup = {}

    for app in apps:
        app_lookup[app["Id"]] = app["Name"]

    print("Retrieving scans...")
    scans = get_scans(token)

    print(f"Found {len(scans)} scans")

    #
    # Remove duplicate App/User combinations
    #

    results = {}

    for scan in scans:

        app_id = scan.get("AppId")

        created_by = scan.get("CreatedBy")

        if not created_by:
            continue

        username = created_by.get("UserName", "")

        key = (app_id, username)

        if key not in results:

            results[key] = [
                app_lookup.get(app_id, "Unknown"),
                app_id,
                created_by.get("FirstName", ""),
                created_by.get("LastName", ""),
                username,
                created_by.get("Email", "")
            ]

    #
    # Write CSV
    #

    print(f"Writing {OUTPUT_FILE}...")

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as csvfile:

        writer = csv.writer(csvfile)

        writer.writerow([
            "Application Name",
            "Application ID",
            "First Name",
            "Last Name",
            "Username",
            "Email"
        ])

        for row in sorted(results.values(), key=lambda x: x[0].lower()):
            writer.writerow(row)

    print(f"\nCSV successfully written to '{OUTPUT_FILE}'")


if __name__ == "__main__":
    main()
