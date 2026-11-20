#Requires -Version 5.1
<#
.SYNOPSIS
    Removes build artifacts, the virtual environment and (optionally) the images.

.DESCRIPTION
    Destructive by design, but scoped: only .venv, bin, obj, caches and this repository's images.
#>
[CmdletBinding(SupportsShouldProcess)]
param([switch] $Images)

$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot

Push-Location $repo
try {
    foreach ($path in @(".venv", "src\Mcp.Rag.Dotnet\bin", "src\Mcp.Rag.Dotnet\obj",
                        "tests\Mcp.Rag.Dotnet.Tests\bin", "tests\Mcp.Rag.Dotnet.Tests\obj",
                        ".pytest_cache", "src\mcp_rag_py.egg-info")) {
        if (Test-Path $path) {
            if ($PSCmdlet.ShouldProcess($path, "remove")) {
                Remove-Item -Recurse -Force $path
                Write-Host "removed $path"
            }
        }
    }

    Get-ChildItem -Recurse -Directory -Filter "__pycache__" | ForEach-Object {
        if ($PSCmdlet.ShouldProcess($_.FullName, "remove")) { Remove-Item -Recurse -Force $_.FullName }
    }

    if ($Images) {
        if (Get-Command docker -ErrorAction SilentlyContinue) {
            & docker compose down --rmi local --volumes
        }
        else {
            Write-Host "docker not found; skipping images"
        }
    }
}
finally {
    Pop-Location
}
