[CmdletBinding()]
param(
    [switch]$Bootstrap,
    [switch]$Stop
)

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$environmentFile = Join-Path $projectRoot '.env.docker'

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw 'Docker Desktop is not installed or not running. Install Docker Desktop, start it, then rerun this script.'
}

if (-not (Test-Path -LiteralPath $environmentFile)) {
    Copy-Item (Join-Path $projectRoot '.env.docker.example') $environmentFile
    throw 'Created .env.docker. Set a strong NEO4J_PASSWORD in that file, then rerun this script.'
}

$pythonExecutable = $null
if ($Bootstrap) {
    $projectPython = Join-Path $projectRoot '.python-runtime\python.exe'
    if (Test-Path -LiteralPath $projectPython) {
        $pythonExecutable = $projectPython
    }
    else {
        $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
        if (-not $pythonCommand) {
            $pythonCommand = Get-Command py -ErrorAction SilentlyContinue
        }
        if ($pythonCommand) {
            $pythonExecutable = $pythonCommand.Source
        }
    }
    if (-not $pythonExecutable) {
        throw 'Python was not found. Run scripts/bootstrap-python.ps1, then install the driver with: uv pip install --python .\.python-runtime\python.exe -r requirements-neo4j.txt'
    }
    & $pythonExecutable -c 'import neo4j'
    if ($LASTEXITCODE -ne 0) {
        throw 'The Neo4j driver is missing. For the project runtime, run: uv pip install --python .\.python-runtime\python.exe -r requirements-neo4j.txt'
    }
}

Push-Location $projectRoot
try {
    if ($Stop) {
        docker compose --env-file .env.docker -f compose.yaml down
        if ($LASTEXITCODE -ne 0) {
            throw "Docker Compose failed while stopping (exit code $LASTEXITCODE)."
        }
        return
    }

    docker compose --env-file .env.docker -f compose.yaml up -d --wait
    if ($LASTEXITCODE -ne 0) {
        throw "Docker Compose failed while starting (exit code $LASTEXITCODE)."
    }
    Write-Host 'Neo4j is ready at http://localhost:7474 (user: neo4j).'

    if ($Bootstrap) {
        Get-Content $environmentFile | ForEach-Object {
            if ($_ -match '^\s*([^#=\s]+)\s*=\s*(.*?)\s*$') {
                Set-Item -Path ("Env:" + $matches[1]) -Value $matches[2]
            }
        }
        & $pythonExecutable -m app.memory.neo4j_bootstrap
        if ($LASTEXITCODE -ne 0) {
            throw "Neo4j bootstrap failed (exit code $LASTEXITCODE)."
        }
    }
}
finally {
    Pop-Location
}
