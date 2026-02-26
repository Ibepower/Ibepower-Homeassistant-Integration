param(
    [string]$OutputDir = "dist"
)

$ErrorActionPreference = "Stop"

Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem

$UnixDirPerm = 493  # 0o755
$UnixFilePerm = 420 # 0o644

function Get-RelativePath {
    param(
        [string]$Root,
        [string]$Path
    )

    $rootNormalized = $Root.TrimEnd([char[]]@('\', '/'))
    $pathNormalized = $Path

    if ($pathNormalized.Length -eq $rootNormalized.Length) {
        return ""
    }

    return $pathNormalized.Substring($rootNormalized.Length + 1).Replace('\', '/')
}

function Add-DirectoryEntry {
    param(
        [System.IO.Compression.ZipArchive]$Archive,
        [string]$EntryName
    )

    if ([string]::IsNullOrWhiteSpace($EntryName)) {
        return
    }

    $normalizedEntryName = $EntryName.Replace('\', '/').TrimStart('/')
    $directoryEntry = $Archive.CreateEntry("$normalizedEntryName/")
    $directoryEntry.ExternalAttributes = (($UnixDirPerm -shl 16) -bor 0x10)
}

function Add-FileEntry {
    param(
        [System.IO.Compression.ZipArchive]$Archive,
        [System.IO.FileInfo]$File,
        [string]$EntryName
    )

    $normalizedEntryName = $EntryName.Replace('\', '/').TrimStart('/')
    $fileEntry = $Archive.CreateEntry($normalizedEntryName, [System.IO.Compression.CompressionLevel]::Optimal)
    $fileEntry.LastWriteTime = [DateTimeOffset]$File.LastWriteTimeUtc
    $fileEntry.ExternalAttributes = ($UnixFilePerm -shl 16)

    $zipStream = $fileEntry.Open()
    $inputStream = $File.OpenRead()
    try {
        $inputStream.CopyTo($zipStream)
    }
    finally {
        $inputStream.Dispose()
        $zipStream.Dispose()
    }
}

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$hacsFile = Join-Path $repoRoot "hacs.json"

if (-not (Test-Path $hacsFile)) {
    throw "No se encontró hacs.json en la raíz del repositorio."
}

$hacsConfig = Get-Content $hacsFile -Raw | ConvertFrom-Json
$zipName = if ($hacsConfig.filename) { $hacsConfig.filename } else { "ibepower_integration.zip" }

$integrationPath = Join-Path $repoRoot "custom_components\ibepower"
if (-not (Test-Path $integrationPath)) {
    throw "No se encontró la carpeta custom_components/ibepower en la raíz del repositorio."
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
    Copy-Item -Path (Join-Path $integrationPath "*") -Destination $tempDir -Recurse -Force
    Get-ChildItem -Path $tempDir -Directory -Recurse -Force |
        Where-Object { $_.Name -eq "__pycache__" } |
        Remove-Item -Recurse -Force
    Get-ChildItem -Path $tempDir -File -Recurse -Force |
        Where-Object { $_.Extension -eq ".pyc" } |
        Remove-Item -Force

    $archive = [System.IO.Compression.ZipFile]::Open($zipPath, [System.IO.Compression.ZipArchiveMode]::Create)
    try {
        $directories = Get-ChildItem -Path $tempDir -Directory -Recurse -Force |
            Sort-Object FullName

        foreach ($directory in $directories) {
            $relativePath = Get-RelativePath -Root $tempDir -Path $directory.FullName
            Add-DirectoryEntry -Archive $archive -EntryName $relativePath
        }

        $files = Get-ChildItem -Path $tempDir -File -Recurse -Force |
            Sort-Object FullName

        foreach ($file in $files) {
            $relativePath = Get-RelativePath -Root $tempDir -Path $file.FullName
            Add-FileEntry -Archive $archive -File $file -EntryName $relativePath
        }
    }
    finally {
        $archive.Dispose()
    }
}
finally {
    if (Test-Path $tempDir) {
        Remove-Item $tempDir -Recurse -Force
    }
}

Write-Host "ZIP generado: $zipPath"
