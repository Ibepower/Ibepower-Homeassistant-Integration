param(
    [string]$OutputDir = "dist"
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$hacsFile = Join-Path $repoRoot "hacs.json"

if (-not (Test-Path $hacsFile)) {
    throw "No se encontró hacs.json en la raíz del repositorio."
}

$hacsConfig = Get-Content $hacsFile -Raw | ConvertFrom-Json
$zipName = if ($hacsConfig.filename) { $hacsConfig.filename } else { "ibepower_integration.zip" }

$customComponentsPath = Join-Path $repoRoot "custom_components"
if (-not (Test-Path $customComponentsPath)) {
    throw "No se encontró la carpeta custom_components en la raíz del repositorio."
}

$resolvedOutputDir = Join-Path $repoRoot $OutputDir
New-Item -ItemType Directory -Path $resolvedOutputDir -Force | Out-Null

$zipPath = Join-Path $resolvedOutputDir $zipName
if (Test-Path $zipPath) {
    Remove-Item $zipPath -Force
}

$tempDir = Join-Path $env:TEMP ("ibepower-hacs-zip-" + [guid]::NewGuid())
New-Item -ItemType Directory -Path $tempDir -Force | Out-Null

try {
    Copy-Item -Path $customComponentsPath -Destination $tempDir -Recurse -Force
    Get-ChildItem -Path $tempDir -Directory -Recurse -Force |
        Where-Object { $_.Name -eq "__pycache__" } |
        Remove-Item -Recurse -Force
    Get-ChildItem -Path $tempDir -File -Recurse -Force |
        Where-Object { $_.Extension -eq ".pyc" } |
        Remove-Item -Force
    Compress-Archive -Path (Join-Path $tempDir "custom_components") -DestinationPath $zipPath -Force
}
finally {
    if (Test-Path $tempDir) {
        Remove-Item $tempDir -Recurse -Force
    }
}

Write-Host "ZIP generado: $zipPath"
