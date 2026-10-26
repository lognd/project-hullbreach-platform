# Hullbreach platform doctor for Windows PowerShell.
#
# The platform runs inside WSL (Linux inside Windows); see README.md
# "Step 0: What a terminal is, and how to open one". This script checks
# whether WSL and an Ubuntu distribution are installed, offers the official
# `wsl --install` (asking first), and prints the exact commands to run the
# real doctor (./doctor.sh) inside Ubuntu. It changes nothing without a "y".

$ErrorActionPreference = "Continue"
$repoUrl = "https://github.com/lognd/project-hullbreach-platform.git"

function Ask-Yes([string]$question) {
    $answer = Read-Host "$question [y/N]"
    return $answer -match '^(y|yes)$'
}

Write-Host "Hullbreach platform doctor (Windows)"
Write-Host ""
Write-Host "On Windows the platform runs inside WSL, a Linux system built into Windows."
Write-Host "Docker Desktop, the database and the website all work from there."
Write-Host ""

$wsl = Get-Command wsl.exe -ErrorAction SilentlyContinue
$distros = @()
if ($wsl) {
    # wsl.exe prints UTF-16; strip the NUL bytes so the names compare.
    $raw = & wsl.exe --list --quiet 2>$null
    if ($LASTEXITCODE -eq 0 -and $raw) {
        $distros = @($raw | ForEach-Object { ($_ -replace "`0", "").Trim() } | Where-Object { $_ })
        # Docker Desktop's own distributions are not a Linux you can work in.
        $distros = @($distros | Where-Object { $_ -notlike "docker-desktop*" })
    }
}

if (-not $wsl -or $distros.Count -eq 0) {
    Write-Host "[FAIL] WSL with a Linux distribution is not installed yet."
    Write-Host "How to fix:"
    Write-Host "  1. Run this in an ADMINISTRATOR PowerShell: wsl --install"
    Write-Host "     (it installs WSL and Ubuntu; this script can start it for you)"
    Write-Host "  2. Restart Windows when it asks."
    Write-Host "  3. Open 'Ubuntu' from the Start menu and choose a Linux user name and password."
    Write-Host "  4. Run this doctor again."
    Write-Host ""
    if (Ask-Yes "Start 'wsl --install' now (Windows asks for administrator permission)?") {
        Start-Process -FilePath "wsl.exe" -ArgumentList "--install" -Verb RunAs -Wait
        Write-Host "When it finishes, restart Windows, open Ubuntu once, then run doctor.cmd again."
    }
    exit 1
}

Write-Host "[PASS] WSL is installed with: $($distros -join ', ')"
Write-Host ""
Write-Host "Next, inside WSL (not in this window):"
Write-Host "  1. Open '$($distros[0])' from the Start menu (a black terminal window opens)."
Write-Host "  2. Get the code there, in your Linux home folder (fast and reliable):"
Write-Host "       git clone $repoUrl"
Write-Host "       cd project-hullbreach-platform"
Write-Host "  3. Run the real doctor and follow what it prints:"
Write-Host "       ./doctor.sh"
Write-Host ""
Write-Host "Keep the code inside Ubuntu (for example /home/<you>/...), not under C:\ ;"
Write-Host "the website's live reload and file watching are slow or broken across that boundary."
Write-Host "Docker Desktop: Settings > Resources > WSL integration > turn on Ubuntu."
exit 0
