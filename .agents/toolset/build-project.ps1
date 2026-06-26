# build-project.ps1
# Reusable PowerShell script to analyze, prepare, and compile Python projects using PyInstaller

# Exit immediately on errors
$ErrorActionPreference = "Stop"

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "      Python Project Builder & Compiler     " -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

# 1. Figure out Python Environment and Version
Write-Host "`n[1/5] Analyzing Python environment..." -ForegroundColor Green

$envType = "Global / System"
$pythonPath = "python"
$isUv = $false

if (Test-Path "uv.lock") {
    $isUv = $true
    $envType = "uv Environment"
}

if (Test-Path ".venv\Scripts\python.exe") {
    $pythonPath = ".venv\Scripts\python.exe"
    if (-not $isUv) {
        $envType = "Virtual Environment (venv)"
    }
} elseif (Test-Path "venv\Scripts\python.exe") {
    $pythonPath = "venv\Scripts\python.exe"
    $envType = "Virtual Environment (venv)"
}

try {
    $pythonVersion = & $pythonPath -c "import platform; print(platform.python_version())"
} catch {
    Write-Error "Could not execute python. Verify Python is installed and accessible at '$pythonPath'."
}

Write-Host "Environment Type: $envType" -ForegroundColor Gray
Write-Host "Python Version  : $pythonVersion" -ForegroundColor Gray
Write-Host "Python Path     : $pythonPath" -ForegroundColor Gray

# 2. Get all imported modules from Python files
Write-Host "`n[2/5] Scanning project python files for import statements..." -ForegroundColor Green

$pyFiles = Get-ChildItem -Filter *.py -Recurse | Where-Object { 
    $_.FullName -notlike "*\.venv\*" -and 
    $_.FullName -notlike "*\venv\*" -and 
    $_.FullName -notlike "*\build\*" -and 
    $_.FullName -notlike "*\dist\*" -and 
    $_.FullName -notlike "*\__pycache__\*"
}

$importedModules = [System.Collections.Generic.HashSet[string]]::new()
$stdLib = @("sys", "os", "re", "json", "shutil", "datetime", "glob", "math", "time", "threading", "logging", "collections", "hashlib", "urllib", "subprocess", "tempfile", "traceback", "uuid", "platform", "argparse", "pathlib", "functools", "itertools")

foreach ($file in $pyFiles) {
    $content = Get-Content $file.FullName
    foreach ($line in $content) {
        if ($line -match "^import\s+([a-zA-Z0-9_\.]+)") {
            $mod = $Matches[1].Split(".")[0]
            if ($stdLib -notcontains $mod -and -not (Test-Path "$mod.py") -and -not (Test-Path $mod)) {
                $null = $importedModules.Add($mod)
            }
        } elseif ($line -match "^from\s+([a-zA-Z0-9_\.]+)\s+import") {
            $mod = $Matches[1].Split(".")[0]
            if ($stdLib -notcontains $mod -and -not (Test-Path "$mod.py") -and -not (Test-Path $mod)) {
                $null = $importedModules.Add($mod)
            }
        }
    }
}

Write-Host "Imported external packages detected in code:" -ForegroundColor Gray
foreach ($mod in $importedModules) {
    Write-Host "  - $mod" -ForegroundColor Gray
}

# 3. Ensure PyInstaller is installed
Write-Host "`n[3/5] Checking for PyInstaller..." -ForegroundColor Green
$pyinstallerInstalled = $false

if ($isUv) {
    # Check via uv pip list
    $pipList = & uv pip list
    if ($pipList -match "pyinstaller\s+") {
        $pyinstallerInstalled = $true
    }
} else {
    # Check via standard python
    $pipList = & $pythonPath -m pip list
    if ($pipList -match "pyinstaller\s+") {
        $pyinstallerInstalled = $true
    }
}

if ($pyinstallerInstalled) {
    Write-Host "PyInstaller is already installed." -ForegroundColor Gray
} else {
    Write-Host "PyInstaller not found. Installing..." -ForegroundColor Yellow
    if ($isUv) {
        & uv pip install pyinstaller
    } else {
        & $pythonPath -m pip install pyinstaller
    }
    Write-Host "PyInstaller successfully installed!" -ForegroundColor Gray
}

# Find PyInstaller executable
$pyinstallerExe = "pyinstaller"
if (Test-Path ".venv\Scripts\pyinstaller.exe") {
    $pyinstallerExe = ".venv\Scripts\pyinstaller.exe"
} elseif (Test-Path "venv\Scripts\pyinstaller.exe") {
    $pyinstallerExe = "venv\Scripts\pyinstaller.exe"
}

# 4. Compile the program
Write-Host "`n[4/5] Compiling program..." -ForegroundColor Green

# Determine entry point or spec file
$specFile = Get-ChildItem -Filter *.spec | Select-Object -First 1
$compileCmd = ""

if ($specFile) {
    Write-Host "Found PyInstaller spec file: $($specFile.Name)" -ForegroundColor Gray
    $compileCmd = "& `"$pyinstallerExe`" --clean --noconfirm `"$($specFile.Name)`""
    Write-Host "Executing: $compileCmd" -ForegroundColor Yellow
    & $pyinstallerExe --clean --noconfirm $specFile.Name
} else {
    $entryPoint = "main.py"
    if (-not (Test-Path $entryPoint)) {
        $entryPoint = Get-ChildItem -Filter *.py | Where-Object { $_.Name -match "main|app" } | Select-Object -First 1
        if (-not $entryPoint) {
            $entryPoint = Get-ChildItem -Filter *.py | Select-Object -First 1
        }
    }
    
    if (-not $entryPoint) {
        Write-Error "No python entrypoint file found to compile!"
    }
    
    Write-Host "No spec file found. Compiling using entrypoint: $($entryPoint)" -ForegroundColor Gray
    
    # Exclude unused modules to trim build size
    $excludeArgs = @()
    # Query installed packages
    if ($isUv) {
        $installed = & uv pip list | Select-Object -Skip 2 | ForEach-Object { $_.Split(" ")[0] }
    } else {
        $installed = & $pythonPath -m pip list | Select-Object -Skip 2 | ForEach-Object { $_.Split(" ")[0] }
    }
    
    foreach ($pkg in $installed) {
        # If installed package is not explicitly imported (case-insensitive check) and not a core dependency, exclude it
        $isUsed = $false
        foreach ($imp in $importedModules) {
            if ($pkg -ieq $imp -or $pkg -like "*$imp*" -or $imp -like "*$pkg*") {
                $isUsed = $true
            }
        }
        
        # Keep pyinstaller and setuptools
        if ($pkg -ieq "pyinstaller" -or $pkg -ieq "setuptools" -or $pkg -ieq "packaging") {
            $isUsed = $true
        }
        
        if (-not $isUsed -and $pkg -ne "") {
            $excludeArgs += "--exclude-module"
            $excludeArgs += $pkg
        }
    }
    
    Write-Host "Excluding unnecessary packages: $($excludeArgs -join ' ')" -ForegroundColor Yellow
    
    # Run PyInstaller with excludes
    & $pyinstallerExe --onefile --noconfirm --clean $excludeArgs $entryPoint
}

# 5. Create Markdown Report
Write-Host "`n[5/5] Generating build report..." -ForegroundColor Green

$reportPath = "BUILD_REPORT.md"
$compiledDate = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
$exeFile = Get-ChildItem -Path dist -Filter *.exe -Recurse | Sort-Object LastWriteTime -Descending | Select-Object -First 1
$exeSizeMB = "Unknown"
$exePath = "N/A"

if ($exeFile) {
    $exeSizeMB = [Math]::Round(($exeFile.Length / 1MB), 2)
    $exePath = $exeFile.FullName
}

$reportContent = @"
# 🚀 Build & Compilation Report

Generated on **$compiledDate**

## 💻 Environment & Runtime Details
- **Environment Type**: $envType
- **Python Version**: $pythonVersion
- **Python Executable**: "$pythonPath"

## 📦 Dependency Audit
### Imported Modules (Used in Code)
$( ($importedModules | ForEach-Object { "- [x] $_" }) -join "`n" )

### Excluded Installed Modules (Trimmed)
$( if ($excludeArgs) { ($excludeArgs | Where-Object { $_ -ne "--exclude-module" } | ForEach-Object { "- [s] $_" }) -join "`n" } else { "None (Spec file configuration took precedence)" } )

## 🛠️ Build Summary
- **Target Spec / Entrypoint**: $(if ($specFile) { $specFile.Name } else { $entryPoint })
- **Output Executable**: $exePath
- **Output Size**: **$exeSizeMB MB**
- **Compile Status**: ✅ Success
"@

$reportContent | Out-File -FilePath $reportPath -Encoding utf8
Write-Host "Build report generated at: $reportPath" -ForegroundColor Green
Write-Host "Done!" -ForegroundColor Green
