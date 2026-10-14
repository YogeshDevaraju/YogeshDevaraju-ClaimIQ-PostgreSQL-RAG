<#
.SYNOPSIS
Shows ClaimIQ PostgreSQL entity history.

.DESCRIPTION
Runs scripts/history_query.py and displays INSERT,
UPDATE, DELETE, version-wise, ID-wise, and latest history.

The database connection is read from the ClaimIQ .env file
through src/core/config.py and src/db/session.py.

This script is read-only.

.PARAMETER Entity
Entity name, such as users, policies, claims, or documents.

.PARAMETER Id
Optional entity record ID.

.PARAMETER Operation
Optional operation:

INSERT
UPDATE
DELETE

.PARAMETER Version
Optional version number.

.PARAMETER Latest
Returns the latest version for the specified record.

-Id is required when -Latest is used.

.EXAMPLE
.\scripts\history.ps1 users

Shows all User history.

.EXAMPLE
.\scripts\history.ps1 users -Id 1

Shows all versions of User ID 1.

.EXAMPLE
.\scripts\history.ps1 users -Operation UPDATE

Shows all User UPDATE operations.

.EXAMPLE
.\scripts\history.ps1 users -Id 1 -Operation UPDATE

Shows only UPDATE operations for User ID 1.

.EXAMPLE
.\scripts\history.ps1 users -Id 1 -Version 2

Shows Version 2 of User ID 1.

.EXAMPLE
.\scripts\history.ps1 users -Id 1 -Latest

Shows the latest version of User ID 1.
#>

param(
    [Parameter(
        Mandatory = $true,
        Position = 0
    )]
    [string]$Entity,

    [Parameter(Mandatory = $false)]
    [string]$Id,

    [Parameter(Mandatory = $false)]
    [ValidateSet(
        "INSERT",
        "UPDATE",
        "DELETE"
    )]
    [string]$Operation,

    [Parameter(Mandatory = $false)]
    [int]$Version,

    [Parameter(Mandatory = $false)]
    [switch]$Latest
)


if (
    $Latest.IsPresent
    -and
    !$PSBoundParameters.ContainsKey("Id")
) {
    Write-Host (
        "ERROR: -Latest requires -Id."
    )

    Write-Host (
        "Example: " +
        ".\scripts\history.ps1 " +
        "users -Id 1 -Latest"
    )

    exit 1
}


$ProjectRoot = Split-Path `
    -Parent `
    $PSScriptRoot


$PythonArguments = @(
    "-m"
    "scripts.history_query"
    $Entity
)


if (
    $PSBoundParameters.ContainsKey("Id")
) {
    $PythonArguments += "--id"
    $PythonArguments += $Id
}


if (
    $PSBoundParameters.ContainsKey(
        "Operation"
    )
) {
    $PythonArguments += "--operation"
    $PythonArguments += $Operation
}


if (
    $PSBoundParameters.ContainsKey(
        "Version"
    )
) {
    $PythonArguments += "--version"
    $PythonArguments += [string]$Version
}


if ($Latest.IsPresent) {
    $PythonArguments += "--latest"
}


Push-Location $ProjectRoot

try {
    & python $PythonArguments

    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
}
finally {
    Pop-Location
}