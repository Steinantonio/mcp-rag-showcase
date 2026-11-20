#Requires -Version 7.0
<#
.SYNOPSIS
    Copies the canonical agent definitions into the OpenCode discovery path.

.DESCRIPTION
    OpenCode discovers agents under <workspace>/.opencode/agents/. The canonical files live in
    mcp-rag-showcase/agents/, so this script mirrors them to
    C:\Trabalho\.opencode\agents\mcp_rag_showcase\ (including adapters/).

    README.md is excluded: it is documentation, not an agent.

.PARAMETER WorkspaceRoot
    Workspace root that contains both this repository and .opencode/.

.PARAMETER WhatIf
    Show what would be copied without copying.

.EXAMPLE
    ./scripts/sync-agents.ps1
#>
[CmdletBinding(SupportsShouldProcess)]
param(
    [string] $WorkspaceRoot = (Split-Path -Parent (Split-Path -Parent $PSScriptRoot))
)

$ErrorActionPreference = 'Stop'

$repoRoot   = Split-Path -Parent $PSScriptRoot
$sourceRoot = Join-Path $repoRoot 'agents'
$targetRoot = Join-Path $WorkspaceRoot '.opencode/agents/mcp_rag_showcase'

if (-not (Test-Path $sourceRoot)) { throw "Agent source not found: $sourceRoot" }

$files = Get-ChildItem -Path $sourceRoot -Recurse -File -Filter '*.md' |
    Where-Object { $_.Name -ne 'README.md' }

if (-not $files) { throw "No agent definitions found in $sourceRoot" }

foreach ($file in $files) {
    $relative = [System.IO.Path]::GetRelativePath($sourceRoot, $file.FullName)
    $target   = Join-Path $targetRoot $relative
    $targetDir = Split-Path -Parent $target

    if (-not (Test-Path $targetDir)) {
        if ($PSCmdlet.ShouldProcess($targetDir, 'Create directory')) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
    }

    if ($PSCmdlet.ShouldProcess($target, 'Copy agent definition')) {
        Copy-Item -Path $file.FullName -Destination $target -Force
        Write-Host "synced  $relative"
    }
}

Write-Host ""
Write-Host "Agents synced to $targetRoot"
Write-Host "Restart OpenCode (or start a new session) so discovery picks them up."
Write-Host "Edit agents/ in the repo, never the copies."
