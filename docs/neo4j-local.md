# Neo4j local com Docker

## Primeira execução

1. Instale e abra o Docker Desktop.
2. Copie `.env.docker.example` para `.env.docker` e defina uma senha local para `NEO4J_PASSWORD`.
3. Instale o driver opcional:

   ```powershell
   python -m pip install -r requirements-neo4j.txt
   ```

4. Inicialize o banco:

   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   .\scripts\start-neo4j.ps1 -Bootstrap
   ```

O navegador Neo4j fica em http://localhost:7474. O usuário é `neo4j`; a senha é a definida em `.env.docker`.

## Operação

```powershell
# Subir o banco persistente
.\scripts\start-neo4j.ps1

# Reaplicar constraints e seed idempotente
.\scripts\start-neo4j.ps1 -Bootstrap

# Parar sem apagar volumes
.\scripts\start-neo4j.ps1 -Stop
```

Os dados ficam em volumes Docker. Não use `docker compose down -v` salvo quando quiser apagar o banco local.
