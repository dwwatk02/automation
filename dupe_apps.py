#!/usr/bin/env python3


import csv
import requests
from datetime import datetime

ASOC_API_KEY = ""
ASOC_API_SECRET = ""
CSV_FILE = "apps_to_create.csv"
ASOC_BASE_URL = "https://cloud.appscan.com/api/v4"

# Optional static values
DEFAULT_DESCRIPTION = "Created via API"
DEFAULT_ASSET_GROUP_ID = ""
presence_id_1 = ""
presence_id_2 = ""

def authenticate(api_key, api_secret):
    url = f"{ASOC_BASE_URL}/Account/ApiKeyLogin"
    payload = {"KeyId": api_key, "KeySecret": api_secret}
    response = requests.post(url, json=payload)
    response.raise_for_status()
    token = response.json()["Token"]
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

def read_csv(file_path):
    apps = []
    with open(file_path, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            presence_ids = list()
            presence_ids.append(presence_id_1)
            presence_ids.append(presence_id_2)
            if not presence_ids:
                print(f"Skipping app '{row['AppName']}' due to missing PresenceIds.")
                continue
            app_name = f"{row['AppName'].strip()}_WAF"
            apps.append({
                "Name": app_name,
                "PresenceIds": presence_ids
            })
    return apps

def create_application(headers, app_data):
    payload = {
        "Name": app_data["Name"],
        "PresencesIds": app_data["PresenceIds"],
        "UseOnlyAppPresences": True,
        "AssetGroupId": DEFAULT_ASSET_GROUP_ID
    }

    response = requests.post(f"{ASOC_BASE_URL}/Apps", headers=headers, json=payload)
    if response.status_code == 200:
        print(f"App created: {app_data['Name']}")
    elif response.status_code == 409:
        print(f"App already exists: {app_data['Name']}")
    else:
        print(f"Failed to create app {app_data['Name']}: {response.status_code} - {response.text}")

def main():
    headers = authenticate(ASOC_API_KEY, ASOC_API_SECRET)
    apps = read_csv(CSV_FILE)
    for app in apps:
        create_application(headers, app)

if __name__ == "__main__":
    main()
