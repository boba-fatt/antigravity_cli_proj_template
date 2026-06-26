# Living Toolset Index

This directory contains permanent, highly optimized scripts to accomplish tasks without burning LLM context tokens.

## Available Tools

* [build-project.ps1](file:///C:/PROJECTS/SO_Survey_Generator/.agents/toolset/build-project.ps1): A PowerShell script that dynamically detects the project's Python environment and version, extracts import statements, ensures PyInstaller is installed locally or via `uv`, compiles the app while excluding unused dependencies to reduce build size, and outputs a detailed `BUILD_REPORT.md` markdown summary.

### Usage:
Run the compiler from the project root:
```powershell
powershell -ExecutionPolicy Bypass -File .agents/toolset/build-project.ps1
```

