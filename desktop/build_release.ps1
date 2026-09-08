param(
    [string]$PythonPath = "backend\venv\Scripts\python.exe",
    [string]$IsccPath = "C:\Program Files\Inno Setup 7\ISCC.exe"
)

$ErrorActionPreference = "Stop"
$desktopDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $desktopDir

Push-Location $projectRoot
try {
    & npm.cmd --prefix frontend run build
    if ($LASTEXITCODE -ne 0) { throw "Frontend build failed" }

    & (Join-Path $projectRoot $PythonPath) -m PyInstaller --noconfirm --clean `
        --distpath (Join-Path $desktopDir "dist") `
        --workpath (Join-Path $desktopDir "build") `
        (Join-Path $desktopDir "naiwa.spec")
    if ($LASTEXITCODE -ne 0) { throw "PyInstaller build failed" }

    & $IsccPath (Join-Path $desktopDir "installer.iss")
    if ($LASTEXITCODE -ne 0) { throw "Installer build failed" }
} finally {
    Pop-Location
}
