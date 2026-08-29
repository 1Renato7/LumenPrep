# Descoberta e mapeamento do Linear

## Conectividade

Faça uma chamada de leitura barata, como listar equipes. Se falhar por autenticação ou conexão, pare e peça ao usuário para conectar o Linear nas configurações. Não contorne com IDs inventados ou dados antigos.

Consulte as ferramentas disponíveis porque nomes/capacidades podem variar. Identifique equivalentes para leitura de equipes, projetos, ciclos, usuários, labels, estados e issues, e para criação/atualização/relações.

## Workspace

Colete antes do preview:

- equipes disponíveis; se mais de uma for plausível, peça escolha;
- projetos e ciclos ativos; confirme destino ou proposta de novo projeto;
- usuários ativos com nome/e-mail para associação;
- labels existentes; proponha nova apenas se necessário;
- estados do time e estado inicial;
- convenção de estimativas, se usada.

Não crie nada nesta fase.

## Seleção do plano

Use caminho explicitamente fornecido. Sem caminho:

1. procure `docs/plans/system-plan.md`;
2. depois `PLANO.md`, `PLAN.md`, `plano*.md`, `plan*.md` e `docs/plano*.md`;
3. se houver mais de um candidato plausível, mostre-os e peça escolha.

Leia o plano inteiro, versão, contexto, prazo, restrições, decisões, objetivos, owners, contratos, dependências, riscos e planos individuais.

## Pessoa → usuário

- nome ou e-mail exato e único: aceite e mostre no preview;
- match parcial, apelido, homônimo ou e-mail divergente: peça confirmação;
- sem match ou usuário inativo: bloqueie as issues dessa pessoa;
- nunca deixe sem assignee silenciosamente nem atribua ao usuário mais parecido.

Pode manter cache local em `.linear-team.json` para reduzir perguntas. Antes de criar/atualizar o arquivo, peça autorização, não registre tokens e mantenha-o ignorado pelo Git. Estrutura recomendada:

```json
{
  "workspaceId": "...",
  "teamId": "...",
  "projectId": "...",
  "members": {
    "Nome no plano": { "userId": "...", "name": "...", "email": "..." }
  },
  "verifiedAt": "ISO-8601"
}
```

Revalide workspace, usuário ativo e correspondência antes de cada escrita; cache não é autoridade.
