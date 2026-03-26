# ╔═══════════════════════════════════════════════════════════════╗
# ║  🧠 PROP FIRM INTELLIGENCE SYSTEM - QUICK VALIDATION          ║
# ╚═══════════════════════════════════════════════════════════════╝

Write-Host ""
Write-Host "╔═══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  🧠 SYSTEM VALIDATION - Quick Check                           ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

$projectRoot = "$Home\ai-command-center\projects\prop-compare"
$skillsDir = "$env:USERPROFILE\.claude\skills"
$logsDir = "$Home\ai-command-center\logs"

$pass = 0; $fail = 0

function Test-Item {
    param([string]$Name, [bool]$Ok, [string]$Info = "")
    if ($Ok) { Write-Host "  ✅ $Name" -ForegroundColor Green; if($Info){Write-Host "     $Info" -ForegroundColor DarkGray}; $script:pass++ }
    else { Write-Host "  ❌ $Name" -ForegroundColor Red; if($Info){Write-Host "     $Info" -ForegroundColor DarkGray}; $script:fail++ }
}

Set-Location $projectRoot

Test-Item "Project root" (Test-Path $projectRoot)
Test-Item "Git clean" ([string]::IsNullOrWhiteSpace($(git status --short 2>$null)))
Test-Item "Commits" ($(git log --oneline 2>$null | Measure-Object | Select-Object -ExpandProperty Count) -gt 0)
Test-Item "Data files" ($(Get-ChildItem "data\*.json" -ErrorAction SilentlyContinue | Measure-Object | Select-Object -ExpandProperty Count) -gt 0)
Test-Item "compare.py" (Test-Path "src\compare.py")
Test-Item "Dashboard" (Test-Path "output\index.html")
Test-Item "Skills" ($(Get-ChildItem "$skillsDir\*\SKILL.md" -ErrorAction SilentlyContinue | Measure-Object | Select-Object -ExpandProperty Count) -gt 0)
Test-Item "Audit log" (Test-Path "$logsDir\decisions.log")

$total = $pass + $fail
$score = [math]::Round(($pass / $total) * 100, 1)

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor DarkGray
Write-Host "  Score: $score% ($pass/$total checks passed)" -ForegroundColor $(if($score -ge 90){"Green"}else{"Yellow"})
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor DarkGray
Write-Host ""
