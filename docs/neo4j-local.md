# Neo4j local com Docker

## Primeira execução

1. Instale e abra o Docker Desktop.
2. Copie `.env.docker.example` para `.env.docker` e defina uma senha local para `NEO4J_PASSWORD`.
3. Instale o driver opcional no runtime do projeto:

   ```powershell
   uv pip install --python .\.python-runtime\python.exe ".[neo4j]"
   ```

   O runtime criado por `scripts/bootstrap-python.ps1` é o pacote embutido
   oficial do Python e não inclui `pip`. Se você preferir usar uma instalação
   normal de Python que já tenha `pip`, o comando equivalente é
   `python -m pip install ".[neo4j]"`.

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
