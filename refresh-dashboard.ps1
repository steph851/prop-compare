# Dashboard Refresh Script
cd "$Home\ai-command-center\projects\prop-compare"
$latest = Get-ChildItem "output\categorized-master-*.json" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
if ($latest) {
    Copy-Item $latest.FullName "output\categorized-master-latest.json" -Force
    Write-Host "✅ Dashboard refreshed: $($latest.Name)" -ForegroundColor Green
} else {
    Write-Host "❌ Run python src\compare.py first" -ForegroundColor Red
}
