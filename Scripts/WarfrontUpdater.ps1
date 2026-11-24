param(
    [Parameter(Mandatory = $true)]
    [string]$DownloadUrl,
    [Parameter(Mandatory = $true)]
    [string]$ExpectedDigest,
    [Parameter(Mandatory = $true)]
    [int]$ProcessId,
    [Parameter(Mandatory = $true)]
    [string]$InstallDirectory,
    [Parameter(Mandatory = $true)]
    [string]$ExecutablePath
)

$ErrorActionPreference = 'Stop'
$temporaryDirectory = Join-Path $env:TEMP ('WarfrontUpdate-' + [guid]::NewGuid().ToString('N'))

try {
    $verifyDigest = $ExpectedDigest -match '^sha256:[0-9a-fA-F]{64}$'

    $archivePath = Join-Path $temporaryDirectory 'Warfront-Windows.zip'
    $stagingDirectory = Join-Path $temporaryDirectory 'staged'
    New-Item -ItemType Directory -Path $stagingDirectory -Force | Out-Null
    Invoke-WebRequest -Uri $DownloadUrl -OutFile $archivePath

    if ($verifyDigest) {
        $actualDigest = (Get-FileHash -LiteralPath $archivePath -Algorithm SHA256).Hash
        $expectedHash = $ExpectedDigest.Substring(7)
        if (-not [string]::Equals($actualDigest, $expectedHash, [StringComparison]::OrdinalIgnoreCase)) {
            throw 'Downloaded update failed SHA-256 verification.'
        }
    }

    Expand-Archive -LiteralPath $archivePath -DestinationPath $stagingDirectory -Force
    $sourceDirectory = $stagingDirectory
    if (-not (Test-Path -LiteralPath (Join-Path $sourceDirectory 'Warfront.exe'))) {
        $candidate = Get-ChildItem -LiteralPath $stagingDirectory -Directory |
            Where-Object { Test-Path -LiteralPath (Join-Path $_.FullName 'Warfront.exe') } |
            Select-Object -First 1
        if (-not $candidate) {
            throw 'The downloaded archive does not contain Warfront.exe.'
        }
        $sourceDirectory = $candidate.FullName
    }

    $resolvedInstallDirectory = [IO.Path]::GetFullPath($InstallDirectory)
    $resolvedExecutablePath = [IO.Path]::GetFullPath($ExecutablePath)
    if (-not $resolvedExecutablePath.StartsWith(
        $resolvedInstallDirectory.TrimEnd('\') + '\',
        [StringComparison]::OrdinalIgnoreCase
    )) {
        throw 'The game executable is outside the installation directory.'
    }

    Wait-Process -Id $ProcessId
    Get-ChildItem -LiteralPath $sourceDirectory -Force | ForEach-Object {
        Copy-Item -LiteralPath $_.FullName -Destination $resolvedInstallDirectory -Recurse -Force
    }
    if (-not (Test-Path -LiteralPath $resolvedExecutablePath)) {
        throw 'Warfront.exe was not present after applying the update.'
    }

    Start-Process -FilePath $resolvedExecutablePath -WorkingDirectory $resolvedInstallDirectory
}
catch {
    Add-Type -AssemblyName System.Windows.Forms
    [System.Windows.Forms.MessageBox]::Show(
        "Aktualizace Warfront se nepodarila: $($_.Exception.Message)",
        'Warfront updater',
        [System.Windows.Forms.MessageBoxButtons]::OK,
        [System.Windows.Forms.MessageBoxIcon]::Error
    ) | Out-Null
}
finally {
    if (Test-Path -LiteralPath $temporaryDirectory) {
        Remove-Item -LiteralPath $temporaryDirectory -Recurse -Force
    }
}
