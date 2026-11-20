#Requires -Version 5.1
<#
.SYNOPSIS
    Calls the same MCP tool on both servers and compares the citations.

.DESCRIPTION
    Speaks MCP over streamable HTTP. Both services run stateless, so every request stands alone and no
    session id is involved. Compares only the citation list (docId#NN), never prose or floats.

    Works on Windows PowerShell 5.1 and PowerShell 7+.

.PARAMETER Python
    Base URL of the Python service.

.PARAMETER Dotnet
    Base URL of the .NET service.

.EXAMPLE
    ./scripts/smoke.ps1
#>
[CmdletBinding()]
param(
    [string] $Python = "http://127.0.0.1:8080",
    [string] $Dotnet = "http://127.0.0.1:8081"
)

$ErrorActionPreference = 'Stop'

$queries = @(
    "how do I rotate an api key",
    "restore a database backup",
    "quarterly access review",
    "roll back the previous artifact",
    "egress rules"
)

function ConvertFrom-SseBody {
    param([string] $Text)

    $data = ($Text -split "`n" | Where-Object { $_ -match '^data:\s*' }) -replace '^data:\s*', ''
    if (-not $data) { throw "empty MCP response" }
    return ($data | Select-Object -Last 1) | ConvertFrom-Json
}

function Invoke-McpTool {
    param([string] $BaseUrl, [string] $Tool, [hashtable] $Arguments)

    $initialize = @{
        jsonrpc = "2.0"; id = 1; method = "initialize"
        params  = @{
            protocolVersion = "2025-06-18"; capabilities = @{}
            clientInfo      = @{ name = "smoke.ps1"; version = "1.0" }
        }
    } | ConvertTo-Json -Depth 6

    Invoke-WebRequest -UseBasicParsing -Method Post -Uri "$BaseUrl/mcp" `
        -ContentType "application/json" -Headers @{ Accept = "application/json, text/event-stream" } `
        -Body $initialize | Out-Null

    $call = @{
        jsonrpc = "2.0"; id = 2; method = "tools/call"
        params  = @{ name = $Tool; arguments = $Arguments }
    } | ConvertTo-Json -Depth 6

    $response = Invoke-WebRequest -UseBasicParsing -Method Post -Uri "$BaseUrl/mcp" `
        -ContentType "application/json" -Headers @{ Accept = "application/json, text/event-stream" } `
        -Body $call

    $envelope = ConvertFrom-SseBody -Text $response.Content
    if ($envelope.error) { throw "MCP error from $BaseUrl : $($envelope.error.message)" }

    $result = $envelope.result
    if ($result.structuredContent) { return $result.structuredContent }
    return ($result.content[0].text | ConvertFrom-Json)
}

$failures = 0

Write-Host "Python : $Python"
Write-Host ".NET   : $Dotnet"
Write-Host ""

foreach ($query in $queries) {
    $py = Invoke-McpTool -BaseUrl $Python -Tool "search" -Arguments @{ query = $query; k = 3 }
    $net = Invoke-McpTool -BaseUrl $Dotnet -Tool "search" -Arguments @{ query = $query; k = 3 }

    $pyIds = @($py.results | ForEach-Object { $_.citation })
    $netIds = @($net.results | ForEach-Object { $_.citation })

    $match = ($pyIds -join ',') -eq ($netIds -join ',')
    if (-not $match) { $failures++ }

    Write-Host ("query: {0}" -f $query)
    Write-Host ("  python  {0}" -f ($pyIds -join '  '))
    Write-Host ("  dotnet  {0}" -f ($netIds -join '  '))
    Write-Host ("  {0}" -f $(if ($match) { "MATCH" } else { "MISMATCH" }))
    Write-Host ""
}

if ($failures -gt 0) {
    Write-Host "$failures/$($queries.Count) queries diverged" -ForegroundColor Red
    exit 1
}

Write-Host "$($queries.Count)/$($queries.Count) queries matched" -ForegroundColor Green
exit 0
