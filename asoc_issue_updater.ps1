# ============================================================
# HCL AppScan on Cloud - Safe Issue Updater
# ============================================================

# =========================
# CONFIGURATION
# =========================

$API_BASE = "https://cloud.appscan.com/api/v4"

$KEY_ID = "YOUR_KEY_ID"
$KEY_SECRET = "YOUR_KEY_SECRET"

#
# Single App:
# $APP_ID = "f099bbb6-f82e-4139-bc59-db6be079d78e"
#
# All Apps:
# $APP_ID = $null
#
$APP_ID = "f099bbb6-f82e-4139-bc59-db6be079d78e"

$TARGET_ISSUE_TYPES = @(
    "SQL Injection"
)

$TARGET_FILE_EXTENSIONS = @(
    ".js"
)

$NEW_STATUS = "Noise"
$COMMENT = "Status updated via API automation"

# ============================================================
# AUTHENTICATION
# ============================================================

function Get-AccessToken {

    $url = "$API_BASE/Account/ApiKeyLogin"

    $body = @{
        KeyId     = $KEY_ID
        KeySecret = $KEY_SECRET
    }

    Write-Host ""
    Write-Host "Authenticating..."

    $response = Invoke-RestMethod `
        -Method Post `
        -Uri $url `
        -Body ($body | ConvertTo-Json) `
        -ContentType "application/json"

    Write-Host "Authenticated."

    return $response.Token
}

# ============================================================
# GET APPLICATIONS
# ============================================================

function Get-Applications {

    param(
        [string]$Token,
        [string]$AppId
    )

    $headers = @{
        Authorization = "Bearer $Token"
    }

    #
    # Single App Mode
    #
    if ($AppId) {

        Write-Host ""
        Write-Host "Using specified application:"
        Write-Host $AppId

        return @(
            @{
                Id   = $AppId
                Name = "Specified Application"
            }
        )
    }

    #
    # All Apps Mode
    #
    Write-Host ""
    Write-Host "No APP_ID specified. Retrieving all applications..."

    $page = 1
    $apps = @()

    do {

        $url = "$API_BASE/Apps?Page=$page&PageSize=100"

        $response = Invoke-RestMethod `
            -Method Get `
            -Uri $url `
            -Headers $headers

        $apps += $response.Items

        $hasNextPage = $response.HasNextPage

        $page++

    } while ($hasNextPage)

    Write-Host "Found $($apps.Count) applications."

    return $apps
}

# ============================================================
# BUILD ODATA FILTER
# ============================================================

function Build-ODataFilter {

    param(
        [string]$IssueType
    )

    $extensionFilters = @()

    foreach ($ext in $TARGET_FILE_EXTENSIONS) {

        $extensionFilters += "endswith(SourceFile,'$ext')"
    }

    $extensionFilter = $extensionFilters -join " or "

    return "IssueType eq '$IssueType' and ($extensionFilter)"
}

# ============================================================
# GET MATCHING ISSUES
# ============================================================

function Get-MatchingIssues {

    param(
        [string]$Token,
        [string]$AppId,
        [string]$IssueType
    )

    $headers = @{
        Authorization = "Bearer $Token"
    }

    $filter = Build-ODataFilter -IssueType $IssueType

    Write-Host ""
    Write-Host "Filter:"
    Write-Host $filter

    $encodedFilter = [System.Web.HttpUtility]::UrlEncode($filter)

    $url = "$API_BASE/Issues/Application/${AppId}?`$filter=$encodedFilter&`$top=5000"

    Write-Host ""
    Write-Host "GET URL:"
    Write-Host $url

    $response = Invoke-RestMethod `
        -Method Get `
        -Uri $url `
        -Headers $headers

    return $response.Items
}

# ============================================================
# UPDATE SINGLE ISSUE
# ============================================================

function Update-Issue {

    param(
        [string]$Token,
        [string]$AppId,
        [string]$IssueId
    )

    $headers = @{
        Authorization = "Bearer $Token"
        "Content-Type" = "application/json"
    }

    #
    # Update a single issue using the documented endpoint
    #
    $filter = "Id eq $IssueId"

    #
    # If your tenant requires GUID syntax:
    #
    # $filter = "Id eq guid'$IssueId'"
    #

    $encodedFilter = [System.Web.HttpUtility]::UrlEncode($filter)

    $url = "$API_BASE/Issues/Application/${AppId}?odataFilter=$encodedFilter"

    $body = @{
        Status  = $NEW_STATUS
        Comment = $COMMENT
    }

    Write-Host ""
    Write-Host "PUT URL:"
    Write-Host $url

    try {

        $response = Invoke-RestMethod `
            -Method Put `
            -Uri $url `
            -Headers $headers `
            -Body ($body | ConvertTo-Json)

        Write-Host "Updated Issue: $IssueId" -ForegroundColor Green
        Write-Host "NUpdatedIssues: $($response.NUpdatedIssues)"
    }
    catch {

        Write-Host "FAILED: $IssueId" -ForegroundColor Red

        try {

            $reader = New-Object System.IO.StreamReader(
                $_.Exception.Response.GetResponseStream()
            )

            $reader.BaseStream.Position = 0
            $reader.DiscardBufferedData()

            $responseBody = $reader.ReadToEnd()

            Write-Host $responseBody

        }
        catch {

            Write-Host $_.Exception.Message
        }
    }
}

# ============================================================
# MAIN
# ============================================================

$token = Get-AccessToken

$applications = Get-Applications `
    -Token $token `
    -AppId $APP_ID

foreach ($app in $applications) {

    $currentAppId = $app.Id
    $currentAppName = $app.Name

    Write-Host ""
    Write-Host "================================================="
    Write-Host "Application: $currentAppName"
    Write-Host "App ID: $currentAppId"
    Write-Host "================================================="

    foreach ($issueType in $TARGET_ISSUE_TYPES) {

        Write-Host ""
        Write-Host "Processing Issue Type: $issueType"

        $issues = Get-MatchingIssues `
            -Token $token `
            -AppId $currentAppId `
            -IssueType $issueType

        if (-not $issues) {

            Write-Host "No matching issues found."
            continue
        }

        Write-Host ""
        Write-Host "Found $($issues.Count) matching issues."

        foreach ($issue in $issues) {

            $issueId = $issue.Id

            Write-Host ""
            Write-Host "Issue:"
            Write-Host "  Id:   $issueId"
            Write-Host "  Type: $($issue.IssueType)"
            Write-Host "  File: $($issue.SourceFile)"

            Update-Issue `
                -Token $token `
                -AppId $currentAppId `
                -IssueId $issueId
        }
    }
}

Write-Host ""
Write-Host "Completed."
