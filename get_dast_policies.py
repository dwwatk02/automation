#!/usr/bin/env python3

import os
import csv
import requests

# ============================================================
# Configuration
# Set these environment variables before running:
# ASOC_KEY_ID
# ASOC_KEY_SECRET
# ============================================================

API_BASE = "https://cloud.appscan.com/api/v4"
KEY_ID = ""
KEY_SECRET = ""


OUTPUT_FILE = "asoc_dast_policies.csv"
PAGE_SIZE = 500
TIMEOUT = 60

if not KEY_ID or not KEY_SECRET:
    raise ValueError(
        "Set ASOC_KEY_ID and ASOC_KEY_SECRET environment variables."
    )

session = requests.Session()
session.headers.update({"Accept": "application/json"})


# ============================================================
# Authentication
# ============================================================

def authenticate():
    url = f"{API_BASE}/Account/ApiKeyLogin"

    response = session.post(
        url,
        json={
            "KeyId": KEY_ID,
            "KeySecret": KEY_SECRET,
        },
        timeout=TIMEOUT,
    )
    response.raise_for_status()

    token = response.json().get("Token")
    if not token:
        raise RuntimeError("Authentication succeeded without a token.")

    session.headers.update({"Authorization": f"Bearer {token}"})


# ============================================================
# Generic paginated OData GET
# ============================================================

def get_all_items(endpoint, params=None):
    url = f"{API_BASE}/{endpoint}"
    items = []
    skip = 0
    base_params = dict(params or {})

    while True:
        page_params = {
            **base_params,
            "$top": PAGE_SIZE,
            "$skip": skip,
        }

        response = session.get(
            url,
            params=page_params,
            timeout=TIMEOUT,
        )
        response.raise_for_status()

        data = response.json()
        page_items = data.get("Items", [])

        if not page_items:
            break

        items.extend(page_items)
        skip += len(page_items)

        if len(page_items) < PAGE_SIZE:
            break

    return items


# ============================================================
# Retrieve applications
# ============================================================

def get_apps():
    apps = get_all_items(
        "Apps",
        params={"$select": "Id,Name"},
    )

    return {
        app["Id"]: app.get("Name", "")
        for app in apps
        if app.get("Id")
    }


# ============================================================
# Retrieve all DAST scans
# ============================================================

def get_dast_scans():
    return get_all_items(
        "Scans",
        params={
            "$filter": "Technology eq 'DynamicAnalyzer'",
            "$select": (
                "Id,Name,AppId,AppName,Technology,"
                "NumberOfExecutions,LatestExecution"
            ),
        },
    )


# ============================================================
# Retrieve test policies
# Includes predefined and custom policies
# ============================================================

def get_test_policy_lookups():
    policies = get_all_items(
        "TestPolicies",
        params={
            "$select": "Id,Name,IsPredefined,IsDefault",
        },
    )

    policies_by_id = {}
    policies_by_name = {}

    for policy in policies:
        policy_id = policy.get("Id")
        policy_name = policy.get("Name")

        if policy_id:
            policies_by_id[policy_id] = policy

        if policy_name:
            policies_by_name[policy_name.casefold()] = policy

    return policies_by_id, policies_by_name


# ============================================================
# Retrieve DAST scan configuration
# IMPORTANT: this endpoint takes the SCAN ID
# ============================================================

def get_dast_scan_details(scan_id):
    url = f"{API_BASE}/Scans/Dast/{scan_id}"

    response = session.get(url, timeout=TIMEOUT)
    response.raise_for_status()

    return response.json()


# ============================================================
# Extract policy fields
# Preserve empty custom fields for predefined policies.
# Use TestPolicies to fill missing values when a policy can
# be matched confidently.
# ============================================================

def extract_policy_fields(
    config,
    policies_by_id,
    policies_by_name,
):
    test_policy = config.get("TestPolicy") or ""
    predefined_policy = config.get("PredefinedTestPolicy") or ""
    custom_policy_id = config.get("CustomTestPolicyId") or ""
    custom_policy_name = config.get("CustomTestPolicyName") or ""

    matched_policy = None

    # First preference: an explicit custom policy ID.
    if custom_policy_id:
        matched_policy = policies_by_id.get(custom_policy_id)

    # Second preference: an explicit custom policy name.
    if not matched_policy and custom_policy_name:
        matched_policy = policies_by_name.get(
            custom_policy_name.casefold()
        )

    # If neither custom field is populated, try the policy name
    # returned in the configuration. For example, Default.policy.
    if not matched_policy and test_policy:
        policy_filename = test_policy.rsplit("/", 1)[-1]
        policy_name = policy_filename

        if policy_name.casefold().endswith(".policy"):
            policy_name = policy_name[:-len(".policy")]

        matched_policy = policies_by_name.get(policy_name.casefold())

    if matched_policy:
        is_predefined = matched_policy.get("IsPredefined") is True

        if is_predefined:
            # Populate the predefined field only.
            if not predefined_policy:
                predefined_policy = matched_policy.get("Name", "")

            # Do not copy predefined policy IDs/names into
            # the custom-policy columns.
        else:
            # Fill custom fields only for a confirmed custom policy.
            if not custom_policy_id:
                custom_policy_id = matched_policy.get("Id", "")

            if not custom_policy_name:
                custom_policy_name = matched_policy.get("Name", "")

    return {
        "Predefined Test Policy": predefined_policy,
        "Custom Test Policy ID": custom_policy_id,
        "Custom Test Policy Name": custom_policy_name,
    }


# ============================================================
# Extract latest execution fields
# These are available directly in LatestExecution.
# No separate execution API call is required for these fields.
# ============================================================

def extract_latest_execution(scan_details, scan_list_item):
    # Prefer the detailed DAST response; fall back to /Scans.
    latest = scan_details.get("LatestExecution") or {}
    if not latest:
        latest = scan_list_item.get("LatestExecution") or {}

    return {
        "Execution ID": latest.get("Id", ""),
        "Execution Created At": latest.get("CreatedAt", ""),
        "Execution Status": latest.get("Status", ""),
        "Execution Progress": latest.get("ExecutionProgress", ""),
        "Execution End Time": latest.get("ScanEndTime", ""),
    }


# ============================================================
# Main
# ============================================================

def main():
    print("Authenticating to ASoC...")
    authenticate()

    print("Retrieving applications...")
    apps_by_id = get_apps()
    print(f"Found {len(apps_by_id)} applications.")

    print("Retrieving test policies...")
    policies_by_id, policies_by_name = get_test_policy_lookups()
    print(f"Found {len(policies_by_id)} test policies.")

    print("Retrieving DAST scans...")
    scans = get_dast_scans()
    print(f"Found {len(scans)} DAST scans.")

    rows = []

    for index, scan in enumerate(scans, start=1):
        scan_id = scan.get("Id", "")
        scan_name = scan.get("Name", "")

        print(
            f"[{index}/{len(scans)}] "
            f"Processing scan: {scan_name} ({scan_id})"
        )

        app_id = scan.get("AppId", "")
        app_name = scan.get("AppName") or apps_by_id.get(app_id, "")

        row = {
            "Application Name": app_name,
            "Application ID": app_id,
            "Scan Name": scan_name,
            "Scan ID": scan_id,
            "Technology": scan.get("Technology", ""),
            "Number Of Executions": scan.get("NumberOfExecutions", ""),
            "Execution ID": "",
            "Execution Created At": "",
            "Execution Status": "",
            "Execution Progress": "",
            "Execution End Time": "",
            "Predefined Test Policy": "",
            "Custom Test Policy ID": "",
            "Custom Test Policy Name": "",
            "Retrieval Error": "",
        }

        try:
            details = get_dast_scan_details(scan_id)
            config = details.get("ScanConfiguration") or {}

            # Extract execution details from LatestExecution.
            row.update(
                extract_latest_execution(details, scan)
            )

            # Extract and resolve policy fields.
            row.update(
                extract_policy_fields(
                    config,
                    policies_by_id,
                    policies_by_name,
                )
            )

        except requests.RequestException as exc:
            row["Retrieval Error"] = str(exc)
            print(f"  WARNING: Could not retrieve scan details: {exc}")

            # Preserve whatever execution details are available
            # in the scan-list response if the detail call fails.
            row.update(
                extract_latest_execution({}, scan)
            )

        rows.append(row)

    # Write CSV
    fieldnames = [
        "Application Name",
        "Application ID",
        "Scan Name",
        "Scan ID",
        "Technology",
        "Number Of Executions",
        "Execution ID",
        "Execution Created At",
        "Execution Status",
        "Execution Progress",
        "Execution End Time",
        "Predefined Test Policy",
        "Custom Test Policy ID",
        "Custom Test Policy Name",
        "Retrieval Error",
    ]

    with open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as csvfile:
        writer = csv.DictWriter(
            csvfile,
            fieldnames=fieldnames,
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nCompleted. Results saved to: {OUTPUT_FILE}")
    print(f"Total DAST scans processed: {len(rows)}")


if __name__ == "__main__":
    main()
