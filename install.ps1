# Convoviz Installer for Windows
# https://github.com/mohamed-chs/convoviz

$ErrorActionPreference = "Stop"

function Write-Info    { param($msg) Write-Host "[INFO] " -ForegroundColor Blue -NoNewline; Write-Host $msg }
function Write-Success { param($msg) Write-Host "[OK] " -ForegroundColor Green -NoNewline; Write-Host $msg }
function Write-Err     { param($msg) Write-Host "[ERROR] " -ForegroundColor Red -NoNewline; Write-Host $msg; exit 1 }

function Test-Command { param($cmd) $null -ne (Get-Command $cmd -ErrorAction SilentlyContinue) }

Write-Host "`nConvoviz Installer`n" -ForegroundColor White

# Step 1: Install uv if missing
if (Test-Command "uv") {
    Write-Success "uv is already installed"
} else {
    Write-Info "Installing uv..."
    try {
        powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    } catch {
        Write-Err "Failed to install uv: $_"
    }
    
    # Refresh PATH
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + `
                [System.Environment]::GetEnvironmentVariable("Path", "User")
    
    if (Test-Command "uv") {
        Write-Success "uv installed successfully"
    } else {
        Write-Err "uv installation failed. Please restart your terminal and try again."
    }
}

# Step 2: Install convoviz
Write-Info "Installing convoviz..."
try {
    uv tool install --python ">=3.12" "convoviz[viz]"
} catch {
    Write-Err "Failed to install convoviz: $_"
}
Write-Success "convoviz installed successfully"

# Step 3: Download NLTK stopwords
Write-Info "Downloading NLTK stopwords..."
try {
    uv run --with nltk python -c "import nltk; nltk.download('stopwords')"
} catch {
    Write-Warning "Failed to download NLTK stopwords: $_"
}
Write-Success "NLTK stopwords downloaded successfully"

# Done
Write-Host "`nInstallation complete!" -ForegroundColor Green
Write-Host "`nTo start using convoviz, restart your terminal."
Write-Host "Then run 'convoviz' to get started.`n"
