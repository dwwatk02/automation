#!/usr/bin/env python3

import requests
import json
import re

# ============================================================
# CONFIGURATION
# ============================================================

API_BASE = "https://cloud.appscan.com/api/v4"

KEY_ID = "YOUR_KEY_ID"
KEY_SECRET = "YOUR_KEY_SECRET"

#
# Single App:
# APP_ID = "f099bbb6-f82e-4139-bc59-db6be079d78e"
#
# All Apps:
# APP_ID = None
#
APP_ID = None

#
# Target Issue Type
#
TARGET_ISSUE_TYPE = "Link to Non-Existing Domain Found"

#
# Wildcard Location Patterns
#
# Examples:
# "*.bcbsfl.com"
# "*.guidewell.com"
#
TARGET_LOCATION_PATTERNS = [
    "*.testfire.com"
]

#
# Severity Update
#
NEW_SEVERITY = "Medium"  # Informational | Low | Medium | High | Critical

COMMENT = "Updated severity via API automation"

# ============================================================
# AUTHENTICATION
# ============================================================

def get_access_token():

    url = f"{API_BASE}/Account/ApiKeyLogin"

    payload = {
        "KeyId": KEY_ID,
        "KeySecret": KEY_SECRET
    }

    response = requests.post(url, json=payload)

    response.raise_for_status()

    return response.json().get("Token")

# ============================================================
# GET APPLICATIONS
# ============================================================

def get_applications(token, app_id=None):

    url = f"{API_BASE}/Apps"

    headers = {
        "Authorization": f"Bearer {token}"
    }

    apps = []

    page = 1

    base_params = {
        "PageSize": 50
    }

    #
    # Optional OData Filter for single app
    #
    if app_id:

        base_params["$filter"] = f"id eq {app_id}"

    while True:

        params = dict(base_params)

        params["Page"] = page

        response = requests.get(
            url,
            headers=headers,
            params=params
        )

        if response.status_code != 200:

            print(f"Failed to fetch applications (page {page})")

            print(response.status_code)

            try:
                print(response.json())
            except Exception:
                print(response.text)

            break

        data = response.json()

        items = data.get("Items", [])

        #
        # Normalize single-object response
        #
        if isinstance(items, dict):

            items = [items]

        apps.extend(items)

        if not data.get("HasNextPage"):

            break

        page += 1

    return apps

# ============================================================
# GET ISSUES
# ============================================================

def get_issues_for_app(token, app_id):

    url = f"{API_BASE}/Issues/Application/{app_id}"

    headers = {
        "Authorization": f"Bearer {token}"
    }

    issues = []

    page = 1

    while True:

        response = requests.get(
            url,
            headers=headers,
            params={
                "Page": page,
                "PageSize": 100
            }
        )

        if response.status_code != 200:

            print(f"Failed to fetch issues for app {app_id}")

            print(response.status_code)

            try:
                print(response.json())
            except Exception:
                print(response.text)

            break

        data = response.json()

        issues.extend(data.get("Items", []))

        if not data.get("HasNextPage"):

            break

        page += 1

    return issues

# ============================================================
# WILDCARD LOCATION MATCH
# ============================================================

def wildcard_match(value, pattern):

    #
    # Convert wildcard syntax:
    #
    # *.bcbsfl.com
    #
    # Into regex:
    #
    # .*\.bcbsfl\.com
    #

    regex = re.escape(pattern)

    regex = regex.replace(r"\*", ".*")

    return re.search(regex, value, re.IGNORECASE) is not None

# ============================================================
# UPDATE ISSUES
# ============================================================

def update_issues(token, app_id, issue_ids, severity, comment=None):

    url = f"{API_BASE}/Issues/UpdateIssuesForScopeByIds/Application/{app_id}"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "issueIds": issue_ids,
        "Comment": comment,
        "Severity": severity
    }

    response = requests.put(
        url,
        headers=headers,
        data=json.dumps(payload)
    )

    if response.status_code == 200:

        print(f"Updated {len(issue_ids)} issues in app {app_id}")

    else:

        print(f"Failed to update issues in app {app_id}")

        print(response.status_code)

        try:
            print(response.json())
        except Exception:
            print(response.text)

# ============================================================
# MAIN
# ============================================================

def main():

    print("Authenticating...")

    token = get_access_token()

    print("Authenticated successfully")

    #
    # Single App
    #
    if APP_ID:

        print(f"Fetching application using APP_ID: {APP_ID}")

    #
    # All Apps
    #
    else:

        print("Fetching all applications...")

    apps = get_applications(
        token,
        app_id=APP_ID
    )

    if not apps:

        print("No applications found.")

        return

    print(f"Processing {len(apps)} application(s)")

    #
    # Process Each App
    #
    for app in apps:

        app_id = app.get("Id")

        app_name = app.get("Name", "<Unnamed>")

        print("")
        print("=================================================")
        print(f"Application: {app_name}")
        print(f"App ID:      {app_id}")
        print("=================================================")

        issues = get_issues_for_app(
            token,
            app_id
        )

        matching_issues = []

        #
        # Match Issues
        #
        for issue in issues:

            issue_type = issue.get("IssueType", "")

            location = issue.get("Location", "")

            #
            # Match Issue Type
            #
            issue_type_match = (
                issue_type.lower()
                == TARGET_ISSUE_TYPE.lower()
            )

            #
            # Match Wildcard Location
            #
            location_match = any(
                wildcard_match(location, pattern)
                for pattern in TARGET_LOCATION_PATTERNS
            )

            #
            # Both conditions must match
            #
            if issue_type_match and location_match:

                matching_issues.append(issue["Id"])

                print("")
                print("Matched Issue")
                print("-----------------------------------")
                print(f"ID:       {issue.get('Id')}")
                print(f"Type:     {issue_type}")
                print(f"Location: {location}")

        #
        # Update Matching Issues
        #
        if matching_issues:

            print("")
            print(f"Found {len(matching_issues)} matching issues")

            print(f"Updating severity to: {NEW_SEVERITY}")

            update_issues(
                token,
                app_id,
                matching_issues,
                NEW_SEVERITY,
                COMMENT
            )

        else:

            print("")
            print("No matching issues found")

    print("")
    print("Completed.")

# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()
