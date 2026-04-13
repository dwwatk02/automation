# ----------------------------
# CONFIGURATION
# ----------------------------
$API_KEY    = "your key ID"
$API_SECRET = "your key secret"

$AUTH_URL        = "https://cloud.appscan.com/api/v4/Account/ApiKeyLogin"
$INVITE_URL      = "https://cloud.appscan.com/api/v4/Account/InviteUsers"
$ASSET_GROUP_URL = "https://cloud.appscan.com/api/v4/AssetGroups"

$CSV_FILE = "users.csv"
$ROLE_ID  = "your role ID"   # placeholder


# ----------------------------
# GET TOKEN
# ----------------------------
function Get-Token {
    $body = @{
        KeyId     = $API_KEY
        KeySecret = $API_SECRET
    } | ConvertTo-Json

    $response = Invoke-RestMethod -Method Post -Uri $AUTH_URL -Body $body -ContentType "application/json"
    return $response.Token
}


# ----------------------------
# GET ALL ASSET GROUPS
# ----------------------------
function Get-AssetGroups($token) {
    $headers = @{
        Authorization = "Bearer $token"
    }

    $uri = $ASSET_GROUP_URL + '?$top=5000&$select=Id,Name'

    $response = Invoke-RestMethod -Method Get -Uri $uri -Headers $headers

    $map = @{}

    foreach ($item in $response.Items) {
        $key = $item.Name.Trim().ToLower()
        $map[$key] = $item.Id
    }

    return $map
}


# ----------------------------
# INVITE USER
# ----------------------------
function Invite-User($token, $email, $assetGroupIds) {
    $headers = @{
        Authorization  = "Bearer $token"
        "Content-Type" = "application/json"
    }

    $body = @{
        Emails        = @($email)
        AssetGroupIds = $assetGroupIds
        RoleId        = $ROLE_ID
    } | ConvertTo-Json -Depth 5

    try {
        Invoke-RestMethod -Method Post -Uri $INVITE_URL -Headers $headers -Body $body
        Write-Host "[SUCCESS] Invitation sent to $email (AGs: $($assetGroupIds -join ', '))"
    }
    catch {
        Write-Host "[FAILED] $email"
        Write-Host "  Error: $($_.Exception.Message)"
    }
}


# ----------------------------
# MAIN
# ----------------------------
Write-Host "Authenticating..."
$token = Get-Token

Write-Host "Loading Asset Groups..."
$assetGroups = Get-AssetGroups $token

Write-Host "Found $($assetGroups.Count) asset groups.`n"

$users = Import-Csv $CSV_FILE

foreach ($row in $users) {
    $email = $row.Email

    if (-not $email) {
        Write-Host "Skipping row with missing email: $($row | Out-String)"
        continue
    }

    $assetGroupIds = @()

    # Loop through AssetGroup1..10
    for ($i = 1; $i -le 10; $i++) {
        $colName = "AssetGroup$i"
        $agName = $row.$colName

        if ($agName) {
            $key = $agName.Trim().ToLower()

            if ($assetGroups.ContainsKey($key)) {
                $assetGroupIds += $assetGroups[$key]
            }
            else {
                Write-Host "[ERROR] Asset Group NOT FOUND: '$agName' for user $email"
            }
        }
    }

    if ($assetGroupIds.Count -eq 0) {
        Write-Host "Skipping $email - no valid asset groups found"
        continue
    }

    Invite-User $token $email $assetGroupIds
}