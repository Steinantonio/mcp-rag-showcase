#Requires -Version 5.1
<#
.SYNOPSIS
    Calls the same MCP tool on both servers and compares the citations.

.DESCRIPTION
    Speaks MCP over streamable HTTP: initialize, notifications/initialized, tools/call.
    Compares only the citation list (docId#NN), never prose or floats.

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

function Get-McpSession {
    param([string] $BaseUrl)

    $body = @{
        jsonrpc = "2.0"; id = 1; method = "initialize"
        params  = @{
            protocolVersion = "2025-06-18"; capabilities = @{}
            clientInfo      = @{ name = "smoke.ps1"; version = "1.0" }
        }
    } | ConvertTo-Json -Depth 6

    $response = Invoke-WebRequest -UseBasicParsing -Method Post -Uri "$BaseUrl/mcp" `
        -ContentType "application/json" -Headers @{ Accept = "application/json, text/event-stream" } -Body $body

    $sessionKey = $response.Headers.Keys | Where-Object { $_ -match 'session' } | Select-Object -First 1
    # .NET's HTTP transport is stateless: it returns no session id and every request stands alone.
    if (-not $sessionKey) { return $null }
    $session = $response.Headers[$sessionKey]

    $notify = @{ jsonrpc = "2.0"; method = "notifications/initialized" } | ConvertTo-Json -Depth 4
    Invoke-WebRequest -UseBasicParsing -Method Post -Uri "$BaseUrl/mcp" -ContentType "application/json" `
        -Headers @{ Accept = "application/json, text/event-stream"; 'mcp-session-id' = $session } -Body $notify | Out-Null

    return $session
}

function ConvertFrom-SseBody {
    param([string] $Text)
    $data = ($Text -split "`n" | Where-Object { $_ -match '^data:\s*' }) -replace '^data:\s*', ''
    if (-not $data) { throw "empty MCP response" }
    return ($data | Select-Object -Last 1) | ConvertFrom-Json
}

function Invoke-McpTool {
    param([string] $BaseUrl, [string] $Session, [string] $Tool, [hashtable] $Arguments)

    $body = @{
        jsonrpc = "2.0"; id = 2; method = "tools/call"
        params  = @{ name = $Tool; arguments = $Arguments }
    } | ConvertTo-Json -Depth 6

    $headers = @{ Accept = "application/json, text/event-stream" }
    if ($Session) { $headers['mcp-session-id'] = $Session }

    $response = Invoke-WebRequest -UseBasicParsing -Method Post -Uri "$BaseUrl/mcp" -ContentType "application/json" `
        -Headers $headers -Body $body

    $envelope = ConvertFrom-SseBody -Text $response.Content
    if ($envelope.error) { throw "MCP error: $($envelope.error.message)" }

    $result = $envelope.result
    if ($result.structuredContent) { return $result.structuredContent }
    return ($result.content[0].text | ConvertFrom-Json)
}

$failures = 0

Write-Host "Python : $Python"
Write-Host ".NET   : $Dotnet"
Write-Host ""

$pySession = Get-McpSession -BaseUrl $Python
$netSession = Get-McpSession -BaseUrl $Dotnet

foreach ($query in $queries) {
    $py = Invoke-McpTool -BaseUrl $Python -Session $pySession -Tool "search" -Arguments @{ query = $query; k = 3 }
    $net = Invoke-McpTool -BaseUrl $Dotnet -Session $netSession -Tool "search" -Arguments @{ query = $query; k = 3 }

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
