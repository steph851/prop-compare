# Dashboard Refresh Script
# Run anytime after: python src\compare.py
Write-Host "=== 🔄 Refreshing Dashboard ===" -ForegroundColor Cyan
$projectRoot = "$Home\ai-command-center\projects\prop-compare"
Set-Location $projectRoot
# Find newest categorized file
$latest = Get-ChildItem "output\categorized-master-*.json" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
if ($latest) {
    Copy-Item $latest.FullName "output\categorized-master-latest.json" -Force
    Write-Host "✅ Dashboard JSON updated" -ForegroundColor Green
    Write-Host "   Source: $($latest.Name)" -ForegroundColor Gray
    Write-Host "🌐 Refresh browser: F5" -ForegroundColor Cyan
} else {
    Write-Host "❌ No categorized files found" -ForegroundColor Red
    Write-Host "💡 Run: python src\compare.py first" -ForegroundColor Yellow
}
