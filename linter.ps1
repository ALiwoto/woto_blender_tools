[CmdletBinding()]
param(
    [ValidateSet("all", "ruff", "pyright", "fix", "format")]
    [string[]]$Tasks = @("all")
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

function Invoke-RepoCommand {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Label,

        [Parameter(Mandatory = $true)]
        [scriptblock]$Command
    )

    Write-Host "==> $Label" -ForegroundColor Cyan
    & $Command

    if ($LASTEXITCODE -ne 0) {
        throw "$Label failed with exit code $LASTEXITCODE."
    }
}

Push-Location $repoRoot

try {
    $resolvedTasks = foreach ($task in $Tasks) {
        if ($task -eq "all") {
            "ruff"
            "pyright"
        }
        else {
            $task
        }
    }

    foreach ($task in $resolvedTasks) {
        switch ($task) {
            "ruff" {
                Invoke-RepoCommand "Ruff check" { python -m ruff check . }
            }
            "pyright" {
                Invoke-RepoCommand "Pyright" { python -m pyright }
            }
            "fix" {
                Invoke-RepoCommand "Ruff auto-fix" { python -m ruff check . --fix }
            }
            "format" {
                Invoke-RepoCommand "Ruff format" { python -m ruff format . }
            }
        }
    }
}
finally {
    Pop-Location
}
