#Requires -Version 5.1
<#
.SYNOPSIS
    Runs the Python service (REST + MCP) on a port, in the foreground.
#>
[CmdletBinding()]
param([int] $Port = 8080)

$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot

Push-Location $repo
try {
    Write-Host "Python service on http://localhost:$Port  (REST /docs, MCP /mcp)"
    & ".\.venv\Scripts\python.exe" -m uvicorn mcp_rag_py.apps.http:app --host 127.0.0.1 --port $Port
}
finally {
    Pop-Location
}
