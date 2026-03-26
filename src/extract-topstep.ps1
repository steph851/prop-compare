# extract-topstep.ps1 - Simple Topstep Data Extraction
# Usage: .\src\extract-topstep.ps1

Write-Host "=== 🤖 Topstep Extraction Started ===" -ForegroundColor Cyan

# Configuration
$Url = "https://propfirmmatch.com/futures/prop-firms/topstep"
$projectRoot = "$Home\ai-command-center\projects\prop-compare"
$dataDir = "$projectRoot\data"
$outputDir = "$projectRoot\output"

Write-Host "🎯 Target URL: $Url" -ForegroundColor Gray
Write-Host "📁 Data folder: $dataDir" -ForegroundColor Gray
Write-Host ""

# Build the prompt for Claude
$prompt = @"
You are a FinTech data extraction specialist.

TASK: Extract Topstep Futures challenge data from this URL and normalize to JSON.

SOURCE: $Url

OUTPUT FORMAT (VALID JSON ONLY, no markdown, no explanations):
{
  "firm_name": "Topstep",
  "division": "Futures",
  "last_verified": "$(Get-Date -Format 'yyyy-MM-dd')",
  "verified_by": "Steph",
  "source_urls": ["$Url"],
  "challenge_models": [{
    "model_name": "Trader Combination",
    "model_type": "standard",
    "account_sizes": [
      {"size": 25000, "profit_target_pct": null, "max_loss_limit_pct": null, "daily_loss_limit_pct": null},
      {"size": 50000, "profit_target_pct": null, "max_loss_limit_pct": null, "daily_loss_limit_pct": null},
      {"size": 100000, "profit_target_pct": null, "max_loss_limit_pct": null, "daily_loss_limit_pct": null}
    ],
    "trading_rules": {
      "overnight_holding": null,
      "news_trading_allowed": null,
      "ea_allowed": null
    },
    "payout_structure": {
      "profit_split_pct": 80,
      "withdrawal_frequency_days": null,
      "min_withdrawal_amount": null
    },
    "restrictions": {
      "inactivity_days_breach": null
    }
  }]
}

INSTRUCTIONS:
1. Fill in the null values with actual data from the URL
2. If a value cannot be found, leave it as null or use "TBD"
3. Output VALID JSON only - no intro text, no markdown code blocks
4. Double-check numbers: profit targets, loss limits, percentages
"@

# Run Claude extraction
Write-Host "🔹 Calling Claude for extraction..." -ForegroundColor Blue
$rawOutput = claude "$prompt" -p --model "claude-sonnet-4-5" 2>&1

# Save raw output for review
$timestamp = Get-Date -Format "yyyyMMdd-HHmm"
$rawFile = "$outputDir\topstep-raw-$timestamp.json"
$rawOutput | Out-File -FilePath $rawFile -Encoding UTF8

Write-Host "✅ Raw output saved: $rawFile" -ForegroundColor Green
Write-Host "📄 Size: $((Get-Item $rawFile).Length) bytes" -ForegroundColor Gray
Write-Host ""

# Open in VS Code for gatekeeping review
Write-Host "🔹 Opening file for your review..." -ForegroundColor Cyan
code $rawFile

# Display review instructions
Write-Host ""
Write-Host "╔════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  🚪 YOUR GATEKEEPING REVIEW                ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "📄 Review this file in VS Code:" -ForegroundColor Gray
Write-Host "   1. Is the JSON valid? (no red squiggly lines)" -ForegroundColor Gray
Write-Host "   2. Does firm_name = 'Topstep'?" -ForegroundColor Gray
Write-Host "   3. Are profit_target_pct values present?" -ForegroundColor Gray
Write-Host "   4. Are loss limit values reasonable?" -ForegroundColor Gray
Write-Host ""
Write-Host "✏️  If needed: Edit values directly in VS Code, then Save (Ctrl+S)" -ForegroundColor Yellow
Write-Host ""
Write-Host "🎯 When ready, return here and type:" -ForegroundColor Cyan
Write-Host "   approve  → Save to final location" -ForegroundColor Gray
Write-Host "   tweak    → Keep editing, then re-run" -ForegroundColor Gray
Write-Host "   reject   → Discard and try manual entry" -ForegroundColor Gray
Write-Host ""

# Wait for user decision
$decision = Read-Host "Your decision (approve/tweak/reject)"

# Handle the decision
$finalPath = "$dataDir\topstep-futures.json"

if ($decision -eq "approve") {
    try {
        # Read and clean the output (extract JSON if mixed with text)
        $content = Get-Content $rawFile -Raw
        $jsonStart = $content.IndexOf('{')
        $jsonEnd = $content.LastIndexOf('}') + 1
        
        if ($jsonStart -ge 0 -and $jsonEnd -gt $jsonStart) {
            $jsonOnly = $content.Substring($jsonStart, $jsonEnd - $jsonStart)
            $validatedJson = $jsonOnly | ConvertFrom-Json
            
            # Save to final location
            $validatedJson | ConvertTo-Json -Depth 10 | Out-File -FilePath $finalPath -Encoding UTF8
            
            Write-Host ""
            Write-Host "✅ APPROVED! Saved to: $finalPath" -ForegroundColor Green
            
            # Log the decision
            $logEntry = "$(Get-Date -Format 'o') | topstep-futures | APPROVED | Extracted from $Url"
            Add-Content -Path "$projectRoot\..\..\logs\decisions.log" -Value $logEntry
            
            # Quick preview
            Write-Host "`n📋 Preview:" -ForegroundColor Cyan
            Write-Host "   Firm: $($validatedJson.firm_name)" -ForegroundColor White
            Write-Host "   Model: $($validatedJson.challenge_models[0].model_name)" -ForegroundColor White
            Write-Host "   Verified: $($validatedJson.last_verified)" -ForegroundColor Gray
        } else {
            Write-Host "❌ No valid JSON found in output" -ForegroundColor Red
            Write-Host "💡 Try running with manual fallback or edit the raw file" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "❌ JSON validation failed: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "💡 Fix the JSON in VS Code and try 'approve' again" -ForegroundColor Yellow
    }
} elseif ($decision -eq "tweak") {
    Write-Host "✏️  TWEAK: Edit $rawFile in VS Code, save it, then run:" -ForegroundColor Yellow
    Write-Host "   Copy-Item '$rawFile' '$finalPath' -Force" -ForegroundColor Gray
} elseif ($decision -eq "reject") {
    Write-Host "❌ REJECTED: You can manually create the file with:" -ForegroundColor Red
    Write-Host "   notepad '$finalPath'" -ForegroundColor Gray
} else {
    Write-Host "⚠️  Unrecognized decision: '$decision'" -ForegroundColor Yellow
    Write-Host "💡 Valid options: approve / tweak / reject" -ForegroundColor Gray
}

Write-Host ""
Write-Host "=== ✅ Extraction Complete ===" -ForegroundColor Cyan