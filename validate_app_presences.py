#!/usr/bin/env python3

import csv
import requests

# Replace with your actual credentials
ASOC_API_KEY = ""
ASOC_API_SECRET = ""
ASOC_BASE_URL = "https://cloud.appscan.com/api/v4"
CSV_FILE = "apps_to_validate.csv"

# Define required Presence IDs
REQUIRED_PRESENCES = {
    "",
    ""
}

def authenticate(api_key, api_secret):
    url = f"{ASOC_BASE_URL}/Account/ApiKeyLogin"
    payload = {"KeyId": api_key, "KeySecret": api_secret}
    response = requests.post(url, json=payload)
    response.raise_for_status()
    token = response.json()["Token"]
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

def read_csv(csv_file):
    with open(csv_file, newline="") as f:
        return list(csv.DictReader(f))

def get_all_apps(headers):
    url = f"{ASOC_BASE_URL}/Apps"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json().get("Items", [])

def update_app_presences(headers, app_id, current_presences, missing_presences):
    # Combine current + missing presences
    updated_presences = list({*current_presences, *missing_presences})
    url = f"{ASOC_BASE_URL}/Apps/{app_id}"
    payload = {
        "PresencesIds": updated_presences
    }
    response = requests.put(url, json=payload, headers=headers)
    if response.status_code == 200:
        print(f"Updated app ID {app_id} with missing Presence ID(s): {', '.join(missing_presences)}")
    else:
        print(f"Failed to update app ID {app_id}. Status: {response.status_code}, Response: {response.text}")

def validate_and_update_apps(apps_data, csv_apps, headers):
    for row in csv_apps:
        app_name = row["AppName"].strip()
        matching_app = next((app for app in apps_data if app["Name"] == app_name), None)

        if not matching_app:
            print(f"App '{app_name}' not found.")
            continue

        app_id = matching_app["Id"]
        current_presences = {p["Id"] for p in matching_app.get("Presences", [])}
        missing_presences = REQUIRED_PRESENCES - current_presences

        if not missing_presences:
            print(f"App '{app_name}' has all required Presence IDs.")
        else:
            print(f"App '{app_name}' is missing: {', '.join(missing_presences)}. Attempting to update...")
            update_app_presences(headers, app_id, current_presences, missing_presences)

def main():
    headers = authenticate(ASOC_API_KEY, ASOC_API_SECRET)
    csv_apps = read_csv(CSV_FILE)
    all_apps = get_all_apps(headers)
    validate_and_update_apps(all_apps, csv_apps, headers)

if __name__ == "__main__":
    main()

