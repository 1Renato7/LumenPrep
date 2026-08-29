<#!
.SYNOPSIS
Downloads the official Python 3.14.4 embeddable runtime for local development.

.DESCRIPTION
The runtime stays in .python-runtime/ and is intentionally excluded from Git.
The downloaded archive is validated against the SHA-256 published by the Python
Software Foundation before extraction.
#>
[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'

$version = '3.14.4'
$archiveUrl = 'https://www.python.org/ftp/python/3.14.4/python-3.14.4-embed-amd64.zip'
$expectedSha256 = 'cda80a9b1e75c0f1b4f9872ca1b417f0d19bce32facc811aea9180e70fad5fb9'
$repositoryRoot = Split-Path -Parent $PSScriptRoot
$runtimeDirectory = Join-Path $repositoryRoot '.python-runtime'
$pythonExecutable = Join-Path $runtimeDirectory 'python.exe'

if (Test-Path -LiteralPath $pythonExecutable) {
    $installedVersion = (& $pythonExecutable --version).Trim()
    if ($installedVersion -eq "Python $version") {
        Write-Output "Python $version is already available at $pythonExecutable"
        exit 0
    }

    throw "Existing local runtime reports '$installedVersion'; remove .python-runtime manually before bootstrapping a different version."
}

if (Test-Path -LiteralPath $runtimeDirectory) {
    throw "Local runtime directory exists without python.exe: $runtimeDirectory. Inspect it before retrying."
}

$archivePath = Join-Path ([System.IO.Path]::GetTempPath()) "python-$version-embed-amd64.zip"
Invoke-WebRequest -Uri $archiveUrl -OutFile $archivePath

$actualSha256 = (Get-FileHash -LiteralPath $archivePath -Algorithm SHA256).Hash.ToLowerInvariant()
if ($actualSha256 -ne $expectedSha256) {
    throw "Downloaded Python archive checksum mismatch: $actualSha256"
}

Expand-Archive -LiteralPath $archivePath -DestinationPath $runtimeDirectory

$pthFile = Get-ChildItem -LiteralPath $runtimeDirectory -Filter '*._pth' -File | Select-Object -First 1
if ($null -eq $pthFile) {
    throw "Python embeddable runtime did not include a ._pth file."
}

$pthLines = Get-Content -LiteralPath $pthFile.FullName
if ($pthLines -notcontains '..') {
    Add-Content -LiteralPath $pthFile.FullName -Value '..'
}
if ($pthLines -contains '#import site') {
    (Get-Content -Raw -LiteralPath $pthFile.FullName).Replace('#import site', 'import site') |
        Set-Content -LiteralPath $pthFile.FullName -NoNewline
}

$installedVersion = (& $pythonExecutable --version).Trim()
if ($installedVersion -ne "Python $version") {
    throw "Bootstrap completed but reported '$installedVersion' instead of Python $version."
}

Write-Output "Python $version is ready at $pythonExecutable"
