param (
    [Parameter(Mandatory=$true)]
    [string]$BusinessUnit
)

# === CONFIG ===
$API_BASE = "https://cloud.appscan.com/api/v4"
$KEY_ID = "YOUR_KEY_ID"
$KEY_SECRET = "YOUR_KEY_SECRET"

$PAGE_SIZE = 500

$OUTPUT_FILE = "asoc_bu_issues_export.csv"

# === AUTH ===
function Get-Token {
    $url = "$API_BASE/Account/ApiKeyLogin"

    $body = @{
        KeyId     = $KEY_ID
        KeySecret = $KEY_SECRET
    } | ConvertTo-Json

    $response = Invoke-RestMethod -Method Post -Uri $url -Body $body -ContentType "application/json"
    return $response.Token
}

# === GET APPS ===
function Get-Apps($token, $businessUnit) {
    $baseUrl = "$API_BASE/Apps"
    $headers = @{ Authorization = "Bearer $token" }

    $apps = @()
    $page = 1

    while ($true) {
        $params = @{
            Page      = $page
            PageSize  = 50
            '$filter' = "BusinessUnit eq '$businessUnit'"
            '$select' = "Id,Name,BusinessUnit"
        }

        $queryString = ($params.GetEnumerator() | ForEach-Object {
            "$($_.Key)=$([uri]::EscapeDataString($_.Value))"
        }) -join "&"

        $url = "$baseUrl`?$queryString"

        $response = Invoke-RestMethod -Method Get -Uri $url -Headers $headers

        $apps += $response.Items

        if (-not $response.HasNextPage) {
            break
        }

        $page++
    }

    return $apps
}

# === GET ISSUES ===
function Get-Issues($token, $appId) {
    $baseUrl = "$API_BASE/Issues/Application/$appId"
    $headers = @{ Authorization = "Bearer $token" }

    $issues = @()
    $skip = 0

    while ($true) {
        $params = @{
            '$top'  = $PAGE_SIZE
            '$skip' = $skip
        }

        $queryString = ($params.GetEnumerator() | ForEach-Object {
            "$($_.Key)=$($_.Value)"
        }) -join "&"

        $url = "$baseUrl`?$queryString"

        $response = Invoke-RestMethod -Method Get -Uri $url -Headers $headers

        $batch = $response.Items
        $issues += $batch

        if ($batch.Count -lt $PAGE_SIZE) {
            break
        }

        $skip += $PAGE_SIZE
    }

    return $issues
}

# === MAIN ===
Write-Host "`nAuthenticating..."
$token = Get-Token
Write-Host "Authenticated.`n"

Write-Host "Fetching applications for Business Unit: $BusinessUnit"
$apps = Get-Apps $token $BusinessUnit

if (-not $apps -or $apps.Count -eq 0) {
    Write-Host "No applications found."
    exit
}

Write-Host "Found $($apps.Count) applications.`n"

$results = @()

foreach ($app in $apps) {
    $appId = $app.Id
    $appName = $app.Name
    $buName = $app.BusinessUnit

    Write-Host "Processing: $appName ($appId)"

    $issues = Get-Issues $token $appId
    Write-Host "  -> $($issues.Count) issues"

    foreach ($issue in $issues) {
        $results += [PSCustomObject]@{
            AppName        = $appName
            BusinessUnit   = $buName
            Severity       = $issue.Severity
            Status         = $issue.Status
            IssueType      = $issue.IssueType
            IssueTypeId    = $issue.IssueTypeId
            IssueTypeGuid  = $issue.IssueTypeGuid
            Location       = $issue.Location
            FixGroupId     = $issue.FixGroupId
            LastFound      = $issue.LastFound
            LastUpdated    = $issue.LastUpdated
            Cve            = $issue.Cve
            Cvss           = $issue.Cvss
            Domain         = $issue.Domain
            LastComment    = $issue.LastComment
            Id             = $issue.Id
            LibraryName    = $issue.LibraryName
            LibraryVersion = $issue.LibraryVersion
            AppPackageId   = $issue.AppPackageId
        }
    }
}

# === EXPORT CSV ===
$results | Export-Csv -Path $OUTPUT_FILE -NoTypeInformation -Encoding UTF8

Write-Host "`nDone. Output written to: $OUTPUT_FILE`n"
