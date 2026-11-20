#Requires -Version 5.1
<#
.SYNOPSIS
    Creates the Python virtual environment, installs dev dependencies and restores .NET.

.DESCRIPTION
    Idempotent: safe to run repeatedly. Requires Python 3.12 on PATH or in PYTHON.
#>
[CmdletBinding()]
param(
    [string] $Python = $(if ($env:PYTHON) { $env:PYTHON } else { "python" })
)

$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot

Push-Location $repo
try {
    Write-Host "==> Python: $Python"
    & $Python --version

    if (-not (Test-Path ".venv")) {
        Write-Host "==> creating .venv"
        & $Python -m venv .venv
    }

    Write-Host "==> installing python dependencies"
    & ".\.venv\Scripts\python.exe" -m pip install --quiet --upgrade pip
    & ".\.venv\Scripts\python.exe" -m pip install --quiet -e ".[dev]"

    Write-Host "==> restoring .NET"
    & dotnet restore | Out-Null

    Write-Host "==> done"
}
finally {
    Pop-Location
}
