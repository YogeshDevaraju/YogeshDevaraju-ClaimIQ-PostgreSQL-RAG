<#
.SYNOPSIS
Shows all available ClaimIQ PostgreSQL entities.

.DESCRIPTION
Runs scripts/entity_list.py.

Displays:

- PostgreSQL table/entity name
- Current row count
- Short explanation of the table

The command is read-only. It does not insert,
update, or delete data.

.EXAMPLE
.\scripts\entity_list.ps1

Shows every available ClaimIQ PostgreSQL table
and its current row count.

.EXAMPLE
Get-Help .\scripts\entity_list.ps1 -Full

Shows the description and examples.
#>

$ProjectRoot = Split-Path `
    -Parent `
    $PSScriptRoot


Push-Location $ProjectRoot


try {
    & python -m scripts.entity_list

    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
}
finally {
    Pop-Location
}