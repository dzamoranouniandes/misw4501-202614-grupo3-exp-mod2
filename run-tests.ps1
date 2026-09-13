$ErrorActionPreference = 'Stop'
$python = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'

if (-not (Test-Path -LiteralPath $python)) {
    throw "No se encontró el entorno virtual en $python. Cree uno con: py -m venv .venv"
}

$services = @('identity-service', 'liveness-adapter', 'didit-mock')
foreach ($service in $services) {
    Write-Host "`n==> Pruebas: $service" -ForegroundColor Cyan
    Push-Location (Join-Path $PSScriptRoot $service)
    try {
        & $python -m pytest -q
        if ($LASTEXITCODE -ne 0) {
            exit $LASTEXITCODE
        }
    }
    finally {
        Pop-Location
    }
}

Write-Host "`nTodas las pruebas aprobaron." -ForegroundColor Green
