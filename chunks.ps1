<#
.SYNOPSIS
Shows document details and a selected chunk range.

.DESCRIPTION
This is a short launcher for:

scripts\document_chunk_range.ps1

.EXAMPLE
.\chunks.ps1 1 0 1

Shows Document ID 1, from chunk index 0 through 1.

.EXAMPLE
Get-Help .\chunks.ps1 -Full

Displays the purpose and examples for this shortcut.
#>

param(
    [Parameter(Mandatory = $true, Position = 0)]
    [int]$DocumentId,

    [Parameter(Mandatory = $true, Position = 1)]
    [int]$StartIndex,

    [Parameter(Mandatory = $true, Position = 2)]
    [int]$EndIndex
)

$ScriptPath = Join-Path `
    $PSScriptRoot `
    "scripts\document_chunk_range.ps1"

& $ScriptPath `
    -DocumentId $DocumentId `
    -StartIndex $StartIndex `
    -EndIndex $EndIndex