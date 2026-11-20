#Requires -Version 5.1
<#
.SYNOPSIS
    Builds and starts both services with docker compose, then waits for health.

.DESCRIPTION
    Requires Docker (Desktop or Podman with the compose provider). Without Docker this script fails
    immediately with a clear message instead of pretending.
#>
[CmdletBinding()]
param([int] $TimeoutSeconds = 120)

$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw "docker not found on PATH. Install Docker Desktop (or Podman) to use compose, or run scripts/serve.ps1 and dotnet run -- --http for a native pair."
}

Push-Location $repo
try {
    Write-Host "==> docker compose up --build -d"
    & docker compose up --build -d
    if ($LASTEXITCODE -ne 0) { throw "docker compose up failed" }

    $targets = @(
        @{ Name = "python"; Url = "http://127.0.0.1:8080/health" },
        @{ Name = "dotnet"; Url = "http://127.0.0.1:8081/health" }
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    foreach ($target in $targets) {
        $healthy = $false
        while ((Get-Date) -lt $deadline) {
            try {
                $response = Invoke-WebRequest -UseBasicParsing -Uri $target.Url -TimeoutSec 5
                if ($response.StatusCode -eq 200) { $healthy = $true; break }
            }
            catch { Start-Sleep -Seconds 2 }
        }
        if (-not $healthy) { throw "$($target.Name) did not become healthy at $($target.Url)" }
        Write-Host "  $($target.Name) healthy"
    }

    Write-Host "==> both services up. Run scripts/smoke.ps1" -ForegroundColor Green
}
finally {
    Pop-Location
}
