$apiUrl = if ($env:API_URL) { $env:API_URL } else { "http://localhost:8000" }
$output = Join-Path $PSScriptRoot "..\apps\api\openapi.json"
Invoke-WebRequest -Uri "$apiUrl/openapi.json" -OutFile $output
Write-Host "Saved to $output"
