#!/usr/bin/env python3

import csv
import requests

# ----------------------------
# CONFIGURATION
# ----------------------------
API_KEY = "your key here"
API_SECRET = "your secret"

AUTH_URL = "https://cloud.appscan.com/api/v4/Account/ApiKeyLogin"
INVITE_URL = "https://cloud.appscan.com/api/v4/Account/InviteUsers"
ASSET_GROUP_URL = "https://cloud.appscan.com/api/v4/AssetGroups"

CSV_FILE = "users.csv"
ROLE_ID = "hardcoded role id"   # placeholder


# ----------------------------
# GET TOKEN
# ----------------------------
def get_token():
    payload = {"KeyId": API_KEY, "KeySecret": API_SECRET}
    response = requests.post(AUTH_URL, json=payload)
    response.raise_for_status()
    return response.json()["Token"]


# ----------------------------
# GET ALL ASSET GROUPS
# ----------------------------
def get_asset_groups(token):
    headers = {"Authorization": f"Bearer {token}"}

    # get up to 5000 in one call
    params = {"$top": 5000, "$select": "Id,Name"}
    response = requests.get(ASSET_GROUP_URL, headers=headers, params=params)
    response.raise_for_status()

    items = response.json().get("Items", [])
    return {item["Name"].strip().lower(): item["Id"] for item in items}


# ----------------------------
# INVITE USER (ONE AT A TIME)
# ----------------------------
def invite_user(token, email, asset_group_id):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "Emails": [email],
        "AssetGroupIds": [asset_group_id],
        "RoleId": ROLE_ID
    }

    response = requests.post(INVITE_URL, json=payload, headers=headers)

    if response.status_code == 200:
        print(f"[SUCCESS] Invitation sent to {email} (AG: {asset_group_id})")
    else:
        print(f"[FAILED] {email}")
        print("  Status:", response.status_code)
        print("  Response:", response.text)


# ----------------------------
# MAIN
# ----------------------------
def main():
    print("Authenticating…")
    token = get_token()

    print("Loading Asset Groups…")
    asset_groups = get_asset_groups(token)

    print(f"Found {len(asset_groups)} asset groups.\n")

    with open(CSV_FILE, newline='') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            email = row.get("Email")
            ag_name = row.get("AssetGroupName")

            if not email or not ag_name:
                print("Skipping row with missing fields:", row)
                continue

            ag_key = ag_name.strip().lower()
            asset_group_id = asset_groups.get(ag_key)

            if not asset_group_id:
                print(f"[ERROR] Asset Group NOT FOUND: '{ag_name}' for user {email}")
                continue

            invite_user(token, email, asset_group_id)


if __name__ == "__main__":
    main()