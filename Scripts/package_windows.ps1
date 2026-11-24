$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $PSScriptRoot
$projectFile = Join-Path $projectRoot 'Warfront.uproject'
$engineRoot = 'C:\Program Files\Epic Games\UE_5.8'
$automationTool = Join-Path $engineRoot 'Engine\Build\BatchFiles\RunUAT.bat'
$buildRoot = Join-Path $projectRoot 'Build'
$archiveRoot = Join-Path $buildRoot 'Warfront-Windows'
$versionLine = Select-String -Path (Join-Path $projectRoot 'Config\DefaultGame.ini') `
    -Pattern '^ProjectVersion=(.+)$' | Select-Object -First 1

if (-not (Test-Path -LiteralPath $projectFile)) {
    throw "Warfront project file was not found: $projectFile"
}
if (-not (Test-Path -LiteralPath $automationTool)) {
    throw "Unreal Automation Tool was not found: $automationTool"
}
if (-not $versionLine) {
    throw 'ProjectVersion is missing from Config\DefaultGame.ini.'
}

$version = $versionLine.Matches[0].Groups[1].Value.Trim()
New-Item -ItemType Directory -Path $buildRoot -Force | Out-Null

& $automationTool BuildCookRun `
    "-project=$projectFile" `
    -noP4 `
    -platform=Win64 `
    -clientconfig=Shipping `
    -build `
    -cook `
    -stage `
    -pak `
    -archive `
    "-archivedirectory=$archiveRoot" `
    -utf8output

if ($LASTEXITCODE -ne 0) {
    throw "Unreal packaging failed with exit code $LASTEXITCODE."
}

$gameExecutable = Get-ChildItem -LiteralPath $archiveRoot -Filter 'Warfront.exe' -File -Recurse |
    Select-Object -First 1
if (-not $gameExecutable) {
    throw "Packaging completed but Warfront.exe was not found under $archiveRoot."
}

Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'WarfrontUpdater.ps1') `
    -Destination (Join-Path $gameExecutable.DirectoryName 'WarfrontUpdater.ps1') -Force

$playFolder = Join-Path $buildRoot 'Warfront-Game'
New-Item -ItemType Directory -Path $playFolder -Force | Out-Null
if (Test-Path -LiteralPath $playFolder) {
    Get-ChildItem -LiteralPath $playFolder -Force | Remove-Item -Recurse -Force
}
New-Item -ItemType Directory -Path $playFolder -Force | Out-Null
Copy-Item -LiteralPath (Join-Path $archiveRoot 'Windows') -Destination $playFolder -Recurse -Force

$playExecutable = Get-ChildItem -LiteralPath $playFolder -Filter 'Warfront.exe' -File -Recurse |
    Select-Object -First 1
if (-not $playExecutable) {
    throw "The playable Warfront folder is missing Warfront.exe."
}

$archivePath = Join-Path $buildRoot 'Warfront-Windows.zip'
if (Test-Path -LiteralPath $archivePath) {
    Remove-Item -LiteralPath $archivePath -Force
}
Compress-Archive -Path (Join-Path $gameExecutable.DirectoryName '*') `
    -DestinationPath $archivePath -CompressionLevel Optimal

$sha256 = (Get-FileHash -LiteralPath $archivePath -Algorithm SHA256).Hash.ToLowerInvariant()
Set-Content -LiteralPath "$archivePath.sha256" -Value "sha256:$sha256" -Encoding ASCII

Write-Output "Game executable: $($gameExecutable.FullName)"
Write-Output "Play folder: $($playExecutable.DirectoryName)"
Write-Output "Release package: $archivePath"
Write-Output "Version: $version"
