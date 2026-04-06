<#
.SYNOPSIS
    Delete old firm data before re-extraction (with backup safety)
    
.USAGE
    .\src\delete-firm-data.ps1 -FirmName "Topstep"
    .\src\delete-firm-data.ps1 -FirmName "FundedNext" -Backup $false
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$FirmName,
    
    [bool]$Backup = $true
)

$projectRoot = "$Home\ai-command-center\projects\prop-compare"
$dataDir = "$projectRoot\data"
$firmFile = "$dataDir\$($FirmName.ToLower())-futures.json"

Write-Host "=== 🗑️ Delete Firm Data: $FirmName ===" -ForegroundColor Cyan

# Check if file exists
if (-not (Test-Path $firmFile)) {
    Write-Host "ℹ️  No existing data found: $firmFile" -ForegroundColor Yellow
    Write-Host "✅ Ready for fresh extraction" -ForegroundColor Green
    return
}

# Backup first (if enabled)
if ($Backup) {
    $backupDir = "$dataDir\backup-$(Get-Date -Format 'yyyyMMdd-HHmm')"
    New-Item -Path $backupDir -ItemType Directory -Force | Out-Null
    Copy-Item $firmFile -Destination $backupDir -Force
    Write-Host "✅ Backup created: $backupDir\$($FirmName.ToLower())-futures.json" -ForegroundColor Green
}

# Delete the file
Remove-Item $firmFile -Force
Write-Host "✅ Deleted: $firmFile" -ForegroundColor Green

# Verify deletion
if (-not (Test-Path $firmFile)) {
    Write-Host "✅ Confirmed: Old data removed" -ForegroundColor Green
    Write-Host "🚀 Ready to extract fresh data for $FirmName" -ForegroundColor Cyan
} else {
    Write-Host "❌ Failed to delete file" -ForegroundColor Red
}