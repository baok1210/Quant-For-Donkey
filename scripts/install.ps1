# Quant for Donkey — create venv and install dependencies (Windows PowerShell).
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

$Venv = Join-Path $Root ".venv"
if (-not (Test-Path $Venv)) {
    Write-Host "Creating virtual environment in .venv ..."
    python -m venv $Venv
}

$Activate = Join-Path $Venv "Scripts\Activate.ps1"
if (-not (Test-Path $Activate)) {
    Write-Error "venv Scripts not found. Is Python installed?"
}

. $Activate
python -m pip install --upgrade pip
pip install -r (Join-Path $Root "requirements.txt")

Write-Host ""
Write-Host "Done."
Write-Host "  Activate:  .\.venv\Scripts\Activate.ps1"
Write-Host "  Dashboard: streamlit run dashboard.py"
Write-Host "  CLI demo:  python main.py"
Write-Host "  Tests:     pip install -r requirements-dev.txt && pytest tests -q"
