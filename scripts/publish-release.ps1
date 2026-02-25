param(
    [ValidateSet("major", "minor", "patch")]
    [string]$Bump = "patch"
)

$ErrorActionPreference = "Stop"

function Get-NextVersion {
    param(
        [string]$CurrentVersion,
        [string]$BumpType
    )

    if ($CurrentVersion -notmatch '^(\d+)\.(\d+)\.(\d+)$') {
        throw "Formato de versión no válido: $CurrentVersion. Se espera x.y.z"
    }

    $major = [int]$Matches[1]
    $minor = [int]$Matches[2]
    $patch = [int]$Matches[3]

    switch ($BumpType) {
        "major" {
            $major++
            $minor = 0
            $patch = 0
        }
        "minor" {
            $minor++
            $patch = 0
        }
        "patch" {
            $patch++
        }
        default {
            throw "Tipo de bump no soportado: $BumpType"
        }
    }

    return "$major.$minor.$patch"
}

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

function Publish-ReleaseWithApi {
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

    $createReleaseBody = @{
        tag_name = $Tag
        name = $Tag
        generate_release_notes = $true
    } | ConvertTo-Json

    $createReleaseUri = "https://api.github.com/repos/$owner/$repo/releases"
    $release = Invoke-RestMethod -Method Post `
        -Uri $createReleaseUri `
        -Headers $apiHeaders `
        -Body $createReleaseBody `
        -ContentType "application/json"

    $zipFileName = Split-Path -Path $ZipPath -Leaf
    $encodedZipFileName = [System.Uri]::EscapeDataString($zipFileName)
    $uploadUri = "https://uploads.github.com/repos/$owner/$repo/releases/$($release.id)/assets?name=$encodedZipFileName"

    Invoke-RestMethod -Method Post `
        -Uri $uploadUri `
        -Headers $apiHeaders `
        -InFile $ZipPath `
        -ContentType "application/zip" | Out-Null
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

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $repoRoot

$manifestPath = Join-Path $repoRoot "custom_components\ibepower\manifest.json"
$hacsPath = Join-Path $repoRoot "hacs.json"

if (-not (Test-Path $manifestPath)) {
    throw "No se encontró manifest.json en custom_components/ibepower."
}

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw "git no está disponible en PATH."
}

$ghAvailable = $null -ne (Get-Command gh -ErrorAction SilentlyContinue)
$githubToken = if (-not [string]::IsNullOrWhiteSpace($env:GITHUB_TOKEN)) { $env:GITHUB_TOKEN } else { $env:GH_TOKEN }

if (-not $ghAvailable -and [string]::IsNullOrWhiteSpace($githubToken)) {
    Write-Host "No se encontró GitHub CLI (gh) y no hay GITHUB_TOKEN/GH_TOKEN definido."
    Write-Host "Introduce un token con permisos de repo (contents: write)."
    $secureToken = Read-Host "GitHub token" -AsSecureString
    $githubToken = Get-TokenFromSecureString -SecureToken $secureToken

    if ([string]::IsNullOrWhiteSpace($githubToken)) {
        throw "No se proporcionó token. Instala gh o define GITHUB_TOKEN/GH_TOKEN."
    }
}

$statusBefore = git status --porcelain
if ($statusBefore) {
    throw "El repositorio tiene cambios sin commitear. Haz commit/stash antes de publicar."
}

if ($ghAvailable) {
    gh auth status | Out-Null
}

$manifestJson = Get-Content $manifestPath -Raw | ConvertFrom-Json
$currentVersion = [string]$manifestJson.version
$newVersion = Get-NextVersion -CurrentVersion $currentVersion -BumpType $Bump

$manifestRaw = Get-Content $manifestPath -Raw
$updatedManifestRaw = [regex]::Replace(
    $manifestRaw,
    '"version"\s*:\s*"[0-9]+\.[0-9]+\.[0-9]+"',
    '"version": "' + $newVersion + '"',
    1
)

if ($manifestRaw -eq $updatedManifestRaw) {
    throw "No se pudo actualizar el campo version en manifest.json."
}

[System.IO.File]::WriteAllText(
    $manifestPath,
    $updatedManifestRaw,
    [System.Text.UTF8Encoding]::new($false)
)

$buildZipScript = Join-Path $PSScriptRoot "build-hacs-zip.ps1"
& $buildZipScript

$hacsConfig = Get-Content $hacsPath -Raw | ConvertFrom-Json
$zipName = if ($hacsConfig.filename) { $hacsConfig.filename } else { "ibepower_integration.zip" }
$zipPath = Join-Path $repoRoot (Join-Path "dist" $zipName)

if (-not (Test-Path $zipPath)) {
    throw "No se encontró el ZIP esperado en: $zipPath"
}

$tag = "v$newVersion"

$localTagExists = git tag --list $tag
if ($localTagExists) {
    throw "La tag $tag ya existe localmente."
}

$remoteTagExists = git ls-remote --tags origin "refs/tags/$tag"
if ($remoteTagExists) {
    throw "La tag $tag ya existe en remoto."
}

git add $manifestPath
git commit -m "chore(release): $tag"
$pushedCommit = $false
$pushedTag = $false
try {
    git tag $tag

    git push
    $pushedCommit = $true
    git push origin $tag
    $pushedTag = $true

    if ($ghAvailable) {
        gh release create $tag $zipPath --title $tag --generate-notes
    }
    else {
        Publish-ReleaseWithApi -Tag $tag -ZipPath $zipPath -Token $githubToken
    }
}
catch {
    if (-not $pushedTag) {
        git tag -d $tag 2>$null | Out-Null
    }
    if (-not $pushedCommit) {
        git reset --hard HEAD~1
    }
    throw
}

Write-Host "Release publicada: $tag"
