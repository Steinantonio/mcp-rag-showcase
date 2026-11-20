#Requires -Version 5.1
<#
.SYNOPSIS
    Runs every test: Python, .NET and cross-language parity.

.DESCRIPTION
    Single exit code. Fails fast on the first suite that fails.
#>
[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot

Push-Location $repo
try {
    Write-Host "==> pytest"
    & ".\.venv\Scripts\python.exe" -m pytest
    if ($LASTEXITCODE -ne 0) { throw "pytest failed" }

    Write-Host "==> architecture (import-linter)"
    & ".\.venv\Scripts\lint-imports.exe"
    if ($LASTEXITCODE -ne 0) { throw "import-linter failed" }

    Write-Host "==> dotnet test"
    & dotnet test --nologo
    if ($LASTEXITCODE -ne 0) { throw "dotnet test failed" }

    Write-Host "==> parity"
    & ".\.venv\Scripts\python.exe" "tests\conformance\parity_runner.py"
    if ($LASTEXITCODE -ne 0) { throw "parity runner failed" }

    Write-Host "==> all suites passed" -ForegroundColor Green
}
finally {
    Pop-Location
}
