<#
.SYNOPSIS
  Install (or uninstall) the Jarvis OpenCode agents, commands and skills.

.DESCRIPTION
  Copies the files under .opencode/ of this package into a project
  (<project>\.opencode\...) or into the global OpenCode config folder
  (default: %USERPROFILE%\.config\opencode). Existing files are never
  overwritten unless -Force is given. Works with Windows PowerShell 5.1
  and PowerShell 7+.

.PARAMETER Target
  Project folder to install into (its .opencode subfolder is used).

.PARAMETER Global
  Install into the global OpenCode config folder instead of a project.

.PARAMETER ConfigDir
  Global config folder to use with -Global. Check yours with:
  opencode debug paths

.PARAMETER Only
  all (default) | factory (jarvis-* agents, commands, skills) | skills (the general skills only)

.PARAMETER WithTemplates
  Project install only: also copy templates\opencode.json and templates\AGENTS.md
  into the project root when they do not exist yet.

.PARAMETER Force
  Overwrite existing files (install) or remove modified files (uninstall).

.PARAMETER DryRun
  Show what would happen without changing anything.

.PARAMETER Uninstall
  Remove the files this package installs. Files you changed are kept unless -Force.

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File .\install\install.ps1 -Target C:\work\my-app -WithTemplates

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File .\install\install.ps1 -Global -Only skills
#>
[CmdletBinding()]
param(
    [string]$Target,
    [switch]$Global,
    [string]$ConfigDir,
    [ValidateSet('all', 'factory', 'skills')]
    [string]$Only = 'all',
    [switch]$WithTemplates,
    [switch]$Force,
    [switch]$DryRun,
    [switch]$Uninstall
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2

$PackageRoot = Split-Path -Parent $PSScriptRoot
$Source = Join-Path $PackageRoot '.opencode'
if (-not (Test-Path -LiteralPath $Source -PathType Container)) {
    throw "Package folder not found: $Source (run this script from the extracted package)."
}

if ($Global -and $Target) { throw 'Use either -Target <project folder> or -Global, not both.' }
if (-not $Global -and -not $Target) { throw 'Specify -Target <project folder> or -Global.' }
if ($WithTemplates -and $Global) { throw '-WithTemplates only applies to a project install (-Target).' }

if ($Global) {
    if ($ConfigDir) { $Dest = $ConfigDir } else { $Dest = Join-Path (Join-Path $HOME '.config') 'opencode' }
    $ProjectRoot = $null
} else {
    if (-not (Test-Path -LiteralPath $Target -PathType Container)) { throw "Target folder not found: $Target" }
    $ProjectRoot = (Resolve-Path -LiteralPath $Target).Path
    $Dest = Join-Path $ProjectRoot '.opencode'
}

function Test-Selected([string]$RelativePath) {
    $p = $RelativePath -replace '\\', '/'
    $isFactory = ($p -like 'agents/jarvis-*') -or ($p -like 'commands/jarvis-*') -or ($p -like 'skills/jarvis-*')
    if ($Only -eq 'factory') { return $isFactory }
    if ($Only -eq 'skills') { return (($p -like 'skills/*') -and -not $isFactory) }
    return $true
}

function Get-Sha256([string]$Path) {
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash
}

$files = @(Get-ChildItem -LiteralPath $Source -Recurse -File | ForEach-Object {
    $rel = $_.FullName.Substring($Source.Length).TrimStart('\', '/')
    if (Test-Selected $rel) { [pscustomobject]@{ Rel = $rel; Full = $_.FullName } }
})

$mode = 'install'
if ($Uninstall) { $mode = 'uninstall' }
$prefix = ''
if ($DryRun) { $prefix = '[dry-run] ' }
Write-Host ("{0}Jarvis OpenCode package: {1} {2} file(s) ({3}) -> {4}" -f $prefix, $mode, $files.Count, $Only, $Dest)

$done = 0; $skipped = @(); $kept = @()
foreach ($f in $files) {
    $to = Join-Path $Dest $f.Rel
    if ($Uninstall) {
        if (-not (Test-Path -LiteralPath $to -PathType Leaf)) { continue }
        if (-not $Force -and ((Get-Sha256 $to) -ne (Get-Sha256 $f.Full))) { $kept += $f.Rel; continue }
        if (-not $DryRun) {
            Remove-Item -LiteralPath $to -Force
            # prune only the folders this file lived in, upwards, while they are empty (never $Dest itself)
            $cur = Split-Path -Parent $to
            $stop = $Dest.TrimEnd('\', '/').Length
            while ($cur -and $cur.Length -gt $stop -and (Test-Path -LiteralPath $cur -PathType Container)) {
                if (@(Get-ChildItem -LiteralPath $cur -Force).Count -gt 0) { break }
                Remove-Item -LiteralPath $cur -Force
                $cur = Split-Path -Parent $cur
            }
        }
        $done++
        continue
    }
    if ((Test-Path -LiteralPath $to -PathType Leaf) -and -not $Force) { $skipped += $f.Rel; continue }
    if (-not $DryRun) {
        $dir = Split-Path -Parent $to
        if (-not (Test-Path -LiteralPath $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
        Copy-Item -LiteralPath $f.Full -Destination $to -Force
    }
    $done++
}

if ($Uninstall) {
    Write-Host ("{0}removed: {1}" -f $prefix, $done)
    if ($kept.Count -gt 0) {
        Write-Host ("kept (changed after install; use -Force to remove): {0}" -f $kept.Count)
        $kept | ForEach-Object { Write-Host ("  " + $_) }
    }
} else {
    Write-Host ("{0}copied: {1}" -f $prefix, $done)
    if ($skipped.Count -gt 0) {
        Write-Host ("skipped (already exists; use -Force to overwrite): {0}" -f $skipped.Count)
        $skipped | ForEach-Object { Write-Host ("  " + $_) }
    }
}

if ($WithTemplates -and -not $Uninstall) {
    foreach ($name in @('opencode.json', 'AGENTS.md')) {
        $from = Join-Path (Join-Path $PackageRoot 'templates') $name
        $to = Join-Path $ProjectRoot $name
        if (Test-Path -LiteralPath $to) {
            Write-Host ("template {0}: {1} already exists - merge templates\{0} into it by hand" -f $name, $to)
        } else {
            if (-not $DryRun) { Copy-Item -LiteralPath $from -Destination $to }
            Write-Host ("{0}template {1}: created {2}" -f $prefix, $name, $to)
        }
    }
}

if (-not $Uninstall) {
    Write-Host ''
    Write-Host 'Next steps:'
    if ($ProjectRoot) {
        Write-Host ('  1. Add ".jarvis/" to {0}\.gitignore (task state and worktrees are local).' -f $ProjectRoot)
        Write-Host ('  2. cd "{0}"; opencode agent list   (expect jarvis-queen and five jarvis-* subagents)' -f $ProjectRoot)
        Write-Host '  3. Start opencode, press Tab to select jarvis-queen, then run /jarvis-analyze'
    } else {
        Write-Host '  1. opencode agent list   (expect jarvis-queen and five jarvis-* subagents)'
        Write-Host '  2. In a project: start opencode, press Tab to select jarvis-queen, then run /jarvis-analyze'
    }
}
