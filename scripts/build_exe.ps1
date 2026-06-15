$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

$Python = Join-Path $ProjectRoot "venv\Scripts\python.exe"
if (-not (Test-Path $Python)) {
    Write-Error "Virtual environment not found. Run: python -m venv venv"
}

$DistConfigTemplate = Join-Path $ProjectRoot "config.dist.yaml"
if (-not (Test-Path $DistConfigTemplate)) {
    Write-Error "Distribution config not found: $DistConfigTemplate"
}

$DistRoot = Join-Path $ProjectRoot "dist"
$DistDir = Join-Path $DistRoot "TBH-Monitor"
$BuildRoot = Join-Path $ProjectRoot "build"
$ConfigBackupPath = Join-Path $env:TEMP "tbh-monitor-config-backup.yaml"
$ExistingConfigPath = Join-Path $DistDir "config.yaml"

function Stop-TbhMonitorProcesses {
    $processes = Get-Process -Name "TBH-Monitor" -ErrorAction SilentlyContinue
    foreach ($process in $processes) {
        Write-Host "Stopping TBH-Monitor (PID $($process.Id))..."
        Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
    }

    if ($processes) {
        Start-Sleep -Milliseconds 750
    }
}

function Remove-DistributionOutput {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    if (-not (Test-Path $Path)) {
        return
    }

    Write-Host "Removing previous build: $Path"
    try {
        Remove-Item -LiteralPath $Path -Recurse -Force -ErrorAction Stop
    } catch {
        Write-Host "Folder locked. Retrying after stopping TBH-Monitor..."
        Stop-TbhMonitorProcesses
        Start-Sleep -Seconds 1
        Remove-Item -LiteralPath $Path -Recurse -Force -ErrorAction Stop
    }
}

function Backup-DistributionConfig {
    if (Test-Path $ExistingConfigPath) {
        Copy-Item $ExistingConfigPath $ConfigBackupPath -Force
        Write-Host "Backed up existing dist config.yaml"
    } elseif (Test-Path $ConfigBackupPath) {
        Remove-Item $ConfigBackupPath -Force -ErrorAction SilentlyContinue
    }
}

function Restore-DistributionConfig {
    $ConfigPath = Join-Path $DistDir "config.yaml"

    if (Test-Path $ConfigBackupPath) {
        Copy-Item $ConfigBackupPath $ConfigPath -Force
        Remove-Item $ConfigBackupPath -Force -ErrorAction SilentlyContinue
        Write-Host "Restored dist config.yaml"
        return
    }

    Copy-Item $DistConfigTemplate $ConfigPath -Force
}

function Invoke-ExternalCommand {
    param(
        [Parameter(Mandatory = $true)]
        [scriptblock]$Command
    )

    $previousErrorAction = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        & $Command
        if ($LASTEXITCODE -ne 0) {
            throw "Command failed with exit code $LASTEXITCODE."
        }
    } finally {
        $ErrorActionPreference = $previousErrorAction
    }
}

$PackagingDir = Join-Path $ProjectRoot "packaging"
$PackagingConfig = Join-Path $PackagingDir "config.yaml"
New-Item -ItemType Directory -Force -Path $PackagingDir | Out-Null
Copy-Item $DistConfigTemplate $PackagingConfig -Force

Invoke-ExternalCommand { & $Python -m pip install --quiet pyinstaller }
Invoke-ExternalCommand { & $Python (Join-Path $ProjectRoot "scripts\generate_icon.py") }

Backup-DistributionConfig
Stop-TbhMonitorProcesses
Remove-DistributionOutput -Path $DistDir

$SpecPath = Join-Path $ProjectRoot "TBH-Monitor.spec"
try {
    Invoke-ExternalCommand {
        & $Python -m PyInstaller $SpecPath --noconfirm --clean --distpath $DistRoot --workpath $BuildRoot
    }
} catch {
    Write-Error @"
PyInstaller failed.
If dist\TBH-Monitor is locked, close TBH-Monitor.exe and any Explorer window open in that folder, then run build again.
"@
}

$ExePath = Join-Path $DistDir "TBH-Monitor.exe"
$InternalDir = Join-Path $DistDir "_internal"

if (-not (Test-Path $ExePath)) {
    Write-Error "Build failed: $ExePath was not created."
}

if (-not (Test-Path $InternalDir)) {
    Write-Error "Build failed: $InternalDir was not created."
}

Restore-DistributionConfig

Write-Host ""
Write-Host "Build complete."
Write-Host ""
Write-Host "Distribution folder (zip this entire folder):"
Write-Host "  $DistDir"
Write-Host ""
Write-Host "Contents required for end users:"
Write-Host "  TBH-Monitor.exe"
Write-Host "  config.yaml"
Write-Host "  _internal\"
Write-Host ""
Write-Host "Run locally: $ExePath"
