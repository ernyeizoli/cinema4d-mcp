@echo off
echo Starting Cinema 4D MCP Server...

REM Try to find Python with the 'mcp' package installed
python -c "import cinema4d_mcp" >nul 2>nul
if %errorlevel% == 0 (
    echo Found cinema4d_mcp in default python.
    python -m cinema4d_mcp
    goto :eof
)

py -c "import cinema4d_mcp" >nul 2>nul
if %errorlevel% == 0 (
    echo Found cinema4d_mcp in py launcher.
    py -m cinema4d_mcp
    goto :eof
)

echo MCP package not found in default Python. Checking other versions...

for %%v in (3.12 3.11 3.10 3.9) do (
    py -%%v -c "import cinema4d_mcp" >nul 2>nul
    if %errorlevel% == 0 (
        echo Found cinema4d_mcp in Python %%v
        py -%%v -m cinema4d_mcp
        goto :eof
    )
)

echo Error: Could not find Python with cinema4d_mcp package installed.
echo Please install the package: pip install -e .
exit /b 1
