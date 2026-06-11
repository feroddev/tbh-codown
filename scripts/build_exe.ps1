$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

$Python = Join-Path $ProjectRoot "venv\Scripts\python.exe"
if (-not (Test-Path $Python)) {
    Write-Error "Virtual environment not found. Run: python -m venv venv"
}

& $Python -m pip install --quiet pyinstaller
& $Python (Join-Path $ProjectRoot "scripts\generate_icon.py")

$SpecPath = Join-Path $ProjectRoot "TBH-Monitor.spec"
& $Python -m PyInstaller $SpecPath --noconfirm --clean

$DistDir = Join-Path $ProjectRoot "dist\TBH-Monitor"
$ExePath = Join-Path $DistDir "TBH-Monitor.exe"
$ConfigPath = Join-Path $DistDir "config.yaml"

if (-not (Test-Path $ExePath)) {
    Write-Error "Build failed: $ExePath was not created."
}

if (-not (Test-Path $ConfigPath)) {
    Copy-Item (Join-Path $ProjectRoot "config.yaml") $ConfigPath
}

Write-Host ""
Write-Host "Build complete."
Write-Host "Run: $ExePath"
Write-Host "Config: $ConfigPath"
