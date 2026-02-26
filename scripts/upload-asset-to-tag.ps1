param(
    [string]$Tag
)

$ErrorActionPreference = "Stop"

function Get-GitHubRepoFromOrigin {
    $originUrl = (git remote get-url origin).Trim()

    if ($originUrl -match '^https://github\.com/([^/]+)/([^/]+?)(\.git)?$') {
        return @{ Owner = $Matches[1]; Repo = $Matches[2] }
    }

    if ($originUrl -match '^git@github\.com:([^/]+)/([^/]+?)(\.git)?$') {
        return @{ Owner = $Matches[1]; Repo = $Matches[2] }
    }

    if ($originUrl -match '^ssh://git@github\.com/([^/]+)/([^/]+?)(\.git)?$') {
        return @{ Owner = $Matches[1]; Repo = $Matches[2] }
    }

    throw "No se pudo extraer owner/repo de origin: $originUrl"
}

function Get-TokenFromSecureString {
    param([SecureString]$SecureToken)

    if (-not $SecureToken) {
        return ""
    }

    $ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($SecureToken)
    try {
        return [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr)
    }
    finally {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr)
    }
}

$tokenStoreDir = Join-Path $env:APPDATA "IbepowerHA"
$tokenStoreFile = Join-Path $tokenStoreDir "github_token.txt"

function Get-StoredGitHubToken {
    if (-not (Test-Path $tokenStoreFile)) {
        return ""
    }

    try {
        $encrypted = Get-Content -Path $tokenStoreFile -Raw
        if ([string]::IsNullOrWhiteSpace($encrypted)) {
            return ""
        }

        $secureToken = ConvertTo-SecureString $encrypted
        return Get-TokenFromSecureString -SecureToken $secureToken
    }
    catch {
        return ""
    }
}

function Save-GitHubToken {
    param([string]$Token)

    if ([string]::IsNullOrWhiteSpace($Token)) {
        return
    }

    if (-not (Test-Path $tokenStoreDir)) {
        New-Item -ItemType Directory -Path $tokenStoreDir -Force | Out-Null
    }

    $secureToken = ConvertTo-SecureString $Token -AsPlainText -Force
    $encrypted = ConvertFrom-SecureString $secureToken
    Set-Content -Path $tokenStoreFile -Value $encrypted -Encoding UTF8
}

function Upload-AssetWithApi {
    param(
        [string]$Tag,
        [string]$ZipPath,
        [string]$Token
    )

    $repoInfo = Get-GitHubRepoFromOrigin
    $owner = $repoInfo.Owner
    $repo = $repoInfo.Repo

    $apiHeaders = @{
        Authorization = "Bearer $Token"
        Accept = "application/vnd.github+json"
        "X-GitHub-Api-Version" = "2022-11-28"
    }

    $encodedTag = [System.Uri]::EscapeDataString($Tag)
    $releaseByTagUri = "https://api.github.com/repos/$owner/$repo/releases/tags/$encodedTag"
    $release = Invoke-RestMethod -Method Get -Uri $releaseByTagUri -Headers $apiHeaders

    $zipFileName = Split-Path -Path $ZipPath -Leaf
    $existingAsset = $release.assets | Where-Object { $_.name -eq $zipFileName } | Select-Object -First 1
    if ($existingAsset) {
        $deleteAssetUri = "https://api.github.com/repos/$owner/$repo/releases/assets/$($existingAsset.id)"
        Invoke-RestMethod -Method Delete -Uri $deleteAssetUri -Headers $apiHeaders | Out-Null
    }

    $encodedZipFileName = [System.Uri]::EscapeDataString($zipFileName)
    $uploadUri = "https://uploads.github.com/repos/$owner/$repo/releases/$($release.id)/assets?name=$encodedZipFileName"

    Invoke-RestMethod -Method Post `
        -Uri $uploadUri `
        -Headers $apiHeaders `
        -InFile $ZipPath `
        -ContentType "application/zip" | Out-Null
}

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $repoRoot

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw "git no está disponible en PATH."
}

if ([string]::IsNullOrWhiteSpace($Tag)) {
    $Tag = Read-Host "Tag existente (ej. v1.3.0)"
}

if ([string]::IsNullOrWhiteSpace($Tag)) {
    throw "Debes indicar un tag."
}

$ghAvailable = $null -ne (Get-Command gh -ErrorAction SilentlyContinue)
$githubToken = if (-not [string]::IsNullOrWhiteSpace($env:GITHUB_TOKEN)) { $env:GITHUB_TOKEN } else { $env:GH_TOKEN }

if ([string]::IsNullOrWhiteSpace($githubToken)) {
    $githubToken = Get-StoredGitHubToken
}

if (-not $ghAvailable -and [string]::IsNullOrWhiteSpace($githubToken)) {
    Write-Host "No se encontró GitHub CLI (gh) y no hay GITHUB_TOKEN/GH_TOKEN definido."
    Write-Host "Introduce un token con permisos de repo (contents: write). Se guardará cifrado para próximos usos."
    $secureToken = Read-Host "GitHub token" -AsSecureString
    $githubToken = Get-TokenFromSecureString -SecureToken $secureToken

    if ([string]::IsNullOrWhiteSpace($githubToken)) {
        throw "No se proporcionó token. Instala gh o define GITHUB_TOKEN/GH_TOKEN."
    }

    Save-GitHubToken -Token $githubToken
}

$hacsPath = Join-Path $repoRoot "hacs.json"
$buildZipScript = Join-Path $PSScriptRoot "build-hacs-zip.ps1"
& $buildZipScript

$hacsConfig = Get-Content $hacsPath -Raw | ConvertFrom-Json
$zipName = if ($hacsConfig.filename) { $hacsConfig.filename } else { "ibepower_integration.zip" }
$zipPath = Join-Path $repoRoot (Join-Path "dist" $zipName)

if (-not (Test-Path $zipPath)) {
    throw "No se encontró el ZIP esperado en: $zipPath"
}

if ($ghAvailable) {
    gh release upload $Tag $zipPath --clobber
}
else {
    Upload-AssetWithApi -Tag $Tag -ZipPath $zipPath -Token $githubToken
}

Write-Host "Asset subido al tag existente: $Tag"
