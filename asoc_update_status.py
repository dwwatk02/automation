#!/usr/bin/env python3

import requests
import json

# === CONFIGURATION ===
API_BASE = "https://cloud.appscan.com/api/v4"
KEY_ID = ""
KEY_SECRET = ""

APP_ID = None  # optional: set a single app UUID, or leave None for all

# === MULTIPLE TARGET ISSUE TYPES ===
TARGET_ISSUE_TYPES = [
    "Cookie with Insecure or Improper or Missing SameSite attribute",
    "Missing Secure Attribute in Encrypted Session (SSL) Cookie",
    "Missing HttpOnly Attribute in Session Cookie",
    "Client-Side (JavaScript) Cookie Reference",
    "Cookie with SameSite attribute not Reflective"
]

NEW_STATUS = "Passed"
COMMENT = "Status updated to Passed via API automation"

# === AUTHENTICATION ===
def get_access_token():
    url = f"{API_BASE}/Account/ApiKeyLogin"
    payload = {"KeyId": KEY_ID, "KeySecret": KEY_SECRET}
    r = requests.post(url, json=payload)
    r.raise_for_status()
    return r.json().get("Token")

# === GET APPLICATIONS ===
def get_applications(token, app_id=None):
    url = f"{API_BASE}/Apps"
    headers = {"Authorization": f"Bearer {token}"}
    apps = []
    page = 1

    params = {"PageSize": 50}
    if app_id:
        params["$filter"] = f"id eq {app_id}"

    while True:
        params["Page"] = page
        r = requests.get(url, headers=headers, params=params)
        r.raise_for_status()
        data = r.json()
        apps.extend(data.get("Items", []))
        if not data.get("HasNextPage"):
            break
        page += 1
    return apps

# === UPDATE ISSUES FOR A SINGLE ISSUE TYPE ===
def update_status_for_issue_type(token, app_id, issue_type):
    url = f"{API_BASE}/Issues/Application/{app_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # 🔎 OData filter: match specific issue type
    params = {
        "odataFilter": f"IssueType eq '{issue_type}'"
    }

    payload = {
        "Status": NEW_STATUS,
        "Comment": COMMENT
    }

    r = requests.put(url, headers=headers, params=params, data=json.dumps(payload))

    if r.status_code == 200:
        updated = r.json().get("NUpdatedIssues", 0)
        print(f"  * {issue_type}: {updated} issues updated.")
    else:
        print(f"  * {issue_type}: FAILED ({r.status_code})")
        print(r.text)

# === MAIN ===
def main():
    print("\nAuthenticating...")
    token = get_access_token()
    print("Authenticated.\n")

    apps = get_applications(token, APP_ID)
    if not apps:
        print("No applications found.")
        return

    for app in apps:
        app_id = app.get("Id")
        app_name = app.get("Name")
        print(f"\n=== Processing application: {app_name} ({app_id}) ===")

        for issue_type in TARGET_ISSUE_TYPES:
            update_status_for_issue_type(token, app_id, issue_type)

    print("\nCompleted.\n")

if __name__ == "__main__":
    main()