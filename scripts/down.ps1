#Requires -Version 5.1
<#
.SYNOPSIS
    Stops and removes the compose stack.
#>
[CmdletBinding()]
param([switch] $Volumes)

$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "docker not found; nothing to stop."
    exit 0
}

Push-Location $repo
try {
    $composeArgs = @("compose", "down")
    if ($Volumes) { $composeArgs += "--volumes" }
    & docker @composeArgs
}
finally {
    Pop-Location
}
