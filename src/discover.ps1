<#
.SYNOPSIS
    Simple URL discovery for prop firm extraction (Claude-only workflow)
.EXAMPLE
    .\src\discover.ps1 -FirmName "FundedNext" -SeedUrl "https://fundednext.com"
#>
param(
    [Parameter(Mandatory=$true)]
    [string]$FirmName,
    [Parameter(Mandatory=$true)]
    [string]$SeedUrl
)
$projectRoot = "$Home\ai-command-center\projects\prop-compare"
$stagingDir = "$projectRoot\staging"
$discoveryFile = "$stagingDir\discovery.txt"
# Ensure staging folder exists
New-Item -Path $stagingDir -ItemType Directory -Force | Out-Null
# Start with seed URL + common patterns
$urls = @(
    $SeedUrl,
    "$SeedUrl/pricing",
    "$SeedUrl/rules",
    "$SeedUrl/challenges",
    "$SeedUrl/faq",
    "$SeedUrl/terms",
    "$SeedUrl/reviews"
)
# Try to fetch and find more links (simple PowerShell)
Write-Host "🔍 Fetching $SeedUrl to discover more URLs..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri $SeedUrl -UseBasicParsing -TimeoutSec 10
    $links = $response.Links | Where-Object { $_.href } | Select-Object -ExpandProperty href
    # Filter for relevant pages
    $relevant = $links | Where-Object {
        $_ -match "pricing|rules|challenge|faq|terms|review|fee|payout|commission" -and
        $_ -notmatch "blog|news|affiliate|login|admin|cart"
    } | ForEach-Object {
        if ($_ -like "http*") { $_ } else { "$SeedUrl/$_" }
    } | Select-Object -Unique
    if ($relevant) {
        $urls += $relevant
        Write-Host "✅ Found $($relevant.Count) additional relevant URLs" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️  Could not fetch page: $($_.Exception.Message)" -ForegroundColor Yellow
    Write-Host "   Using seed URL + common patterns only" -ForegroundColor Gray
}
# Remove duplicates + sort
$urls = $urls | Select-Object -Unique | Sort-Object
# Save to discovery.txt (simple, human-readable)
$urls | Out-File -FilePath $discoveryFile -Encoding UTF8
Write-Host "`n✅ Discovery complete for $FirmName" -ForegroundColor Green
Write-Host "📄 URLs saved to: $discoveryFile" -ForegroundColor Gray
Write-Host "📋 Preview:" -ForegroundColor Cyan
$urls | Select-Object -First 5 | ForEach-Object { Write-Host "   - $_" -ForegroundColor Gray }
if ($urls.Count -gt 5) {
    Write-Host "   ... and $($urls.Count - 5) more" -ForegroundColor Gray
}
Write-Host "`n👉 Next: In VS Code Chat, run:" -ForegroundColor Cyan
Write-Host "   /schema-extended-extraction Extract $FirmName" -ForegroundColor White
Write-Host "   Then paste URLs from: $discoveryFile" -ForegroundColor Gray
