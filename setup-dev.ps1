# setup-dev.ps1 - Environnement dev Capsule House (VS Code + autocompletion Odoo 19)
# Usage (depuis la racine du repo) :
#   powershell -ExecutionPolicy Bypass -File setup-dev.ps1
# Ou : clic droit -> "Executer avec PowerShell"

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

function Step($msg) { Write-Host "==> $msg" -ForegroundColor Cyan }
function Check($what) {
    if ($LASTEXITCODE -ne 0) { throw "Echec : $what (code $LASTEXITCODE)" }
}

# 0. Prerequis
Step "Verification des prerequis..."
foreach ($cmd in @("git", "python")) {
    if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) {
        throw "'$cmd' est introuvable. Installe-le et coche 'Add to PATH', puis relance."
    }
}
$pyVersion = & python -c "import sys; print('%d.%d' % sys.version_info[:2])"
if ([version]$pyVersion -lt [version]"3.10") {
    throw "Python $pyVersion detecte : Odoo 19 demande Python 3.10 ou plus."
}
Write-Host "Python $pyVersion OK" -ForegroundColor Green

# 1. Chemins longs git
Step "Activation des chemins longs git..."
git config --global core.longpaths true
Check "git config"

# 2. Venv + dependances
Step "Creation du venv..."
if (-not (Test-Path ".\venv\Scripts\python.exe")) {
    python -m venv venv
    Check "creation du venv"
} else {
    Write-Host "venv deja present, on saute la creation." -ForegroundColor Green
}
.\venv\Scripts\python.exe -m pip install --upgrade pip
Check "mise a jour de pip"
.\venv\Scripts\python.exe -m pip install reportlab
Check "installation de reportlab"

# 3. Source Odoo 19 (a cote du repo) pour l'autocompletion
$odooSrc = Join-Path (Split-Path $PSScriptRoot -Parent) "odoo-src"
if (-not (Test-Path (Join-Path $odooSrc "odoo\http.py"))) {
    Step "Telechargement du source Odoo 19 (peut prendre quelques minutes)..."
    git clone --depth 1 --branch 19.0 https://github.com/odoo/odoo.git $odooSrc
    Check "clone d'Odoo 19"
} else {
    Write-Host "odoo-src deja present, on saute." -ForegroundColor Green
}

# 4. .vscode/settings.json avec les bons chemins absolus
Step "Ecriture de .vscode/settings.json..."
New-Item -ItemType Directory -Force -Path (Join-Path $PSScriptRoot ".vscode") | Out-Null
$odooSrcAbs = (Resolve-Path $odooSrc).Path -replace '\\', '/'
$settings = @"
{
  "python.analysis.extraPaths": [
    "$odooSrcAbs"
  ],
  "python.defaultInterpreterPath": "`${workspaceFolder}/venv/Scripts/python.exe"
}
"@
$settingsPath = Join-Path $PSScriptRoot ".vscode\settings.json"
[System.IO.File]::WriteAllText($settingsPath, $settings, (New-Object System.Text.UTF8Encoding($false)))

Write-Host ""
Write-Host "==> Termine !" -ForegroundColor Green
Write-Host "Dans VS Code :"
Write-Host "  1. Installer les extensions Python et Pylance (Microsoft)"
Write-Host "  2. Ctrl+Shift+P -> Python: Select Interpreter -> choisir le venv"
Write-Host "  3. Ctrl+Shift+P -> Python: Restart Language Server"
Write-Host "Verification : ouvrir capsule_house_theme/controllers/catalogue_pdf.py (zero warning)."
