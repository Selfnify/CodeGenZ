# CodeGenZ installer (Windows)
#
#   irm https://raw.githubusercontent.com/enderairstudio/CodeGenZ/main/installers/install-windows.ps1 | iex
#
# Clones the repo into %USERPROFILE%\.codegenz, installs the Python
# compiler as a real `genz` command, and adds it to your PATH.

$ErrorActionPreference = "Stop"

$RepoUrl = "https://github.com/enderairstudio/CodeGenZ.git"
$InstallDir = Join-Path $env:USERPROFILE ".codegenz"

function Info($msg) { Write-Host "==> $msg" }
function Fail($msg) { Write-Error $msg; exit 1 }

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Fail "git is required but not found. Install it from https://git-scm.com and re-run."
}

$PythonCmd = $null
foreach ($candidate in @("python", "py")) {
    if (Get-Command $candidate -ErrorAction SilentlyContinue) { $PythonCmd = $candidate; break }
}
if (-not $PythonCmd) {
    Fail "Python is required but not found. Install it from https://python.org (check 'Add to PATH') and re-run."
}

Info "Installing CodeGenZ into $InstallDir"
# if we're currently sitting inside the folder we're about to wipe
# (e.g. re-running the installer from compiler-py), Windows refuses
# to delete it - hop out to a safe neutral directory first.
Set-Location $env:USERPROFILE
if (Test-Path $InstallDir) { Remove-Item -Recurse -Force $InstallDir }
$prevEap = $ErrorActionPreference
$ErrorActionPreference = "Continue"
git clone --depth 1 $RepoUrl $InstallDir *>&1 | ForEach-Object { Write-Host $_ }
$cloneExit = $LASTEXITCODE
$ErrorActionPreference = $prevEap
if ($cloneExit -ne 0) { Fail "git clone failed (exit code $cloneExit)" }

Info "Installing the genz CLI (pip --user)"
Set-Location (Join-Path $InstallDir "compiler-py")

# pip writes harmless warnings (e.g. "script not on PATH") to stderr,
# and PowerShell's "Stop" preference turns ANY stderr line from a
# native command into a terminating error. Relax it just for the pip
# calls and judge success by exit code instead.
$prevEap = $ErrorActionPreference
$ErrorActionPreference = "Continue"
& $PythonCmd -m pip install --user -e . *>&1 | ForEach-Object { Write-Host $_ }
$pipExit = $LASTEXITCODE
if ($pipExit -ne 0) {
    # modern Python installs may refuse system-wide installs (PEP 668);
    # --user -e into our own prefix is safe to override
    & $PythonCmd -m pip install --user --break-system-packages -e . *>&1 | ForEach-Object { Write-Host $_ }
    $pipExit = $LASTEXITCODE
}
$ErrorActionPreference = $prevEap
if ($pipExit -ne 0) { Fail "pip install failed (exit code $pipExit)" }

$UserBase = (& $PythonCmd -m site --user-base).Trim()
$ScriptsDir = Join-Path $UserBase "Scripts"

$CurrentPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($CurrentPath -notlike "*$ScriptsDir*") {
    $NewPath = if ([string]::IsNullOrEmpty($CurrentPath)) { $ScriptsDir } else { "$CurrentPath;$ScriptsDir" }
    [Environment]::SetEnvironmentVariable("Path", $NewPath, "User")
    Info "Added $ScriptsDir to your user PATH"
}

Write-Host ""
Write-Host "CodeGenZ installed."
Write-Host ""
Write-Host "  Open a NEW terminal window, then:"
Write-Host "    genz build path\to\site.gz -o dist\"
Write-Host ""
Write-Host "  Examples live in: $InstallDir\examples"
Write-Host "  Language reference: $InstallDir\docs\SYNTAX.md"
