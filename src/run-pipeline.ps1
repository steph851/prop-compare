<#
.SYNOPSIS
    Claude-Only Pipeline: Discover → Extract → Score → Approve → Dashboard
    Uses ONLY your Claude Pro plan (no extra API costs)

.EXAMPLE
    .\src\run-pipeline.ps1 -FirmName "FundedNext" -SeedUrl "https://fundednext.com"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$FirmName,
    
    [Parameter(Mandatory=$true)]
    [string]$SeedUrl
)

$projectRoot = "$Home\ai-command-center\projects\prop-compare"
$firmLower = $FirmName.ToLower() -replace '\s+', ''

Write-Host "`n╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  🧠 CLAUDE-ONLY PIPELINE: $FirmName" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# ── STEP 1: DISCOVERY ──
Write-Host "🔍 Step 1: Discovering URLs..." -ForegroundColor Yellow
.\src\discover.ps1 -FirmName $FirmName -SeedUrl $SeedUrl
Write-Host "✅ Discovery complete`n" -ForegroundColor Green

# ── STEP 2: EXTRACTION (Claude) ──
Write-Host "🤖 Step 2: Extraction via Claude..." -ForegroundColor Yellow
Write-Host "👉 In VS Code Chat (or Claude Code terminal), run:" -ForegroundColor Cyan
Write-Host ""
Write-Host "   /schema-extended-extraction Extract $FirmName with FULL extended schema" -ForegroundColor White
Write-Host ""
Write-Host "   Then paste URLs from: staging\discovery.txt" -ForegroundColor Gray
Write-Host "   Output to: staging\raw_extract.json" -ForegroundColor Gray
Write-Host ""
Write-Host "⏳  Waiting for you to complete extraction in Claude..." -ForegroundColor Gray
Write-Host "   Press ENTER when you've saved staging\raw_extract.json" -ForegroundColor Gray
$null = $Host.UI.ReadLine()

# Verify extraction file exists
$rawFile = "staging\raw_extract.json"
if (-not (Test-Path $rawFile)) {
    Write-Host "❌ staging\raw_extract.json not found. Please extract first." -ForegroundColor Red
    exit 1
}
Write-Host "✅ Raw extraction found`n" -ForegroundColor Green

# ── STEP 3: SCORING (Ask Claude or Local) ──
Write-Host "🧮 Step 3: Scoring..." -ForegroundColor Yellow
Write-Host "Option A: Ask Claude to score (recommended)" -ForegroundColor Gray
Write-Host "   In VS Code Chat: /difficulty-ranker Score staging\raw_extract.json" -ForegroundColor Gray
Write-Host ""
Write-Host "Option B: Use local Python scoring" -ForegroundColor Gray
Write-Host "   Run: python src\score.py" -ForegroundColor Gray
Write-Host ""
Write-Host "⏳  Waiting for you to complete scoring..." -ForegroundColor Gray
Write-Host "   Output should be: staging\scored_extract.json" -ForegroundColor Gray
Write-Host "   Press ENTER when ready" -ForegroundColor Gray
$null = $Host.UI.ReadLine()

$scoredFile = "staging\scored_extract.json"
if (-not (Test-Path $scoredFile)) {
    Write-Host "⚠️  staging\scored_extract.json not found. Using raw_extract.json for approval." -ForegroundColor Yellow
    $scoredFile = $rawFile
}
Write-Host "✅ Scoring complete`n" -ForegroundColor Green

# ── STEP 4: YOUR APPROVAL (Gatekeeping) ──
Write-Host "👁️  Step 4: Your Review (Gatekeeping)..." -ForegroundColor Yellow
Write-Host "👉 Open in VS Code: code staging\scored_extract.json" -ForegroundColor Cyan
Write-Host ""
Write-Host "Check:" -ForegroundColor Gray
Write-Host "  ✅ firm_name matches exactly: '$FirmName'" -ForegroundColor Gray
Write-Host "  ✅ All 4 schema sections present" -ForegroundColor Gray
Write-Host "  ✅ Arrays use [""item""] format" -ForegroundColor Gray
Write-Host "  ✅ Numbers are numbers, booleans are true/false" -ForegroundColor Gray
Write-Host ""
Write-Host "If approved, type: approve" -ForegroundColor Green
Write-Host "If needs edits, type: tweak" -ForegroundColor Yellow
Write-Host "If reject, type: reject" -ForegroundColor Red
Write-Host ""
$decision = $Host.UI.ReadLine().Trim().ToLower()

if ($decision -eq "approve") {
    # Save to production
    Copy-Item $scoredFile "data\$firmLower.json" -Force
    Write-Host "✅ Saved to data\$firmLower.json" -ForegroundColor Green
    
    # Log decision
    $logEntry = "$(Get-Date -Format 'o') | $firmLower | APPROVED | Claude-only pipeline by Steph"
    Add-Content -Path "$projectRoot\logs\decisions.log" -Value $logEntry
    Write-Host "✅ Decision logged`n" -ForegroundColor Gray
    
} elseif ($decision -eq "tweak") {
    Write-Host "✏️  Edit staging\scored_extract.json, then re-run this script." -ForegroundColor Yellow
    exit 0
    
} elseif ($decision -eq "reject") {
    Write-Host "❌ Extraction rejected. Delete staging files and re-extract." -ForegroundColor Red
    exit 1
    
} else {
    Write-Host "⚠️  Unknown decision. Please type: approve, tweak, or reject" -ForegroundColor Yellow
    exit 1
}

# ── STEP 5: COMPARISON + DASHBOARD ──
Write-Host "📊 Step 5: Updating comparison + dashboard..." -ForegroundColor Yellow
python src\compare.py
.\refresh-dashboard.ps1
Write-Host "✅ Dashboard updated`n" -ForegroundColor Green

# ── DONE ──
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║  🎉 PIPELINE COMPLETE: $FirmName" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "✅ Data saved: data\$firmLower.json" -ForegroundColor Green
Write-Host "✅ Dashboard: output\index.html (refresh browser)" -ForegroundColor Green
Write-Host "✅ Log: logs\decisions.log" -ForegroundColor Green
Write-Host ""
Write-Host "🚀 Next firm: .\src\run-pipeline.ps1 -FirmName 'NextFirm' -SeedUrl 'https://...'" -ForegroundColor Cyan
