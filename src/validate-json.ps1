<#
.SYNOPSIS
    Validate JSON files for Phase 6 pipeline

.EXAMPLE
    .\src\validate-json.ps1 -FilePath "staging\scored_extract.json" -Schema "extended"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$FilePath,
    
    [ValidateSet("extended", "basic")]
    [string]$Schema = "extended"
)

Write-Host "🔍 Validating: $FilePath" -ForegroundColor Cyan

# Check file exists
if (-not (Test-Path $FilePath)) {
    Write-Host "❌ File not found: $FilePath" -ForegroundColor Red
    exit 1
}

# Try to parse JSON
try {
    $json = Get-Content $FilePath -Raw | ConvertFrom-Json -ErrorAction Stop
    Write-Host "✅ Valid JSON syntax" -ForegroundColor Green
} catch {
    Write-Host "❌ Invalid JSON: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Schema validation
if ($Schema -eq "extended") {
    $required = @("firm_name", "🏢 FIRM PROFILE", "💰 PRICING & OFFERS", "📊 CHALLENGE MODELS", "🏆 AGGREGATE METRICS")
    $missing = $required | Where-Object { -not $json.PSObject.Properties.Name.Contains($_) }
    
    if ($missing) {
        Write-Host "❌ Missing required sections: $($missing -join ', ')" -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ Extended schema validation passed" -ForegroundColor Green
}

# Check firm_name matches expected pattern
if ($json.firm_name -and $json.firm_name -match "^[A-Z][a-zA-Z\s]+$") {
    Write-Host "✅ firm_name format valid: '$($json.firm_name)'" -ForegroundColor Green
} else {
    Write-Host "⚠️  firm_name may need review: '$($json.firm_name)'" -ForegroundColor Yellow
}

Write-Host "✅ Validation complete" -ForegroundColor Green
exit 0
