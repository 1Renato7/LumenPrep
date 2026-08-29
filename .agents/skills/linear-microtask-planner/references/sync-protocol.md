# Preview, criação e sincronização

## Preview obrigatório

Mostre time, projeto/ciclo, hierarquia, estado inicial, labels novas propostas e total. Inclua:

| ID | Título | Responsável | Prioridade | Estimativa | Bloqueada por | Desbloqueia |
| --- | --- | --- | --- | --- | --- | --- |

Some issues e esforço estimado por pessoa. Sinalize desequilíbrio considerando complexidade, risco e caminho crítico, não apenas quantidade. Liste ambiguidades, usuários não confirmados e perguntas abertas. Peça `criar`, `ajustar` ou `cancelar`.

## Idempotência

Antes de criar, liste issues existentes no projeto/parents. Faça match nesta ordem:

1. ID estável `TASK-*` na descrição;
2. identificador/URL já gravado no plano;
3. parent + assignee + título normalizado como fallback.

Equivalente existe: atualize somente campos necessários, preservando comentários/progresso. Novo: crie. Sumiu do plano: não delete nem cancele; reporte e peça decisão. Título isolado nunca é identidade suficiente quando houver ambiguidade.

## Criação em duas passagens

1. Crie ou confirme projeto/épico autorizado.
2. Crie/atualize parents por objetivo e guarde IDs.
3. Crie/atualize microtarefas na ordem de dependência e guarde ID/identifier/URL.
4. Faça segundo passe para `blocked by`/`blocks`, parents, links e placeholders.
5. Releia cada item e valide contra o preview aprovado.

## Falha parcial

Ao primeiro erro material, pare novas escritas. Não repita cegamente. Informe operação, erro, itens criados/atualizados, itens pendentes e relações ainda não aplicadas. Releia o estado real e apresente opções seguras. Continue somente após direção do usuário.

## Backlinks

Depois da verificação, atualize o plano geral e os planos individuais com identifier/URL ao lado do mesmo `TASK-*`. Não reescreva contexto ou progresso não relacionado. Se o arquivo mudou desde a leitura, compare e preserve alterações antes de editar.

## Fechamento

Devolva links do projeto/parents, issues por pessoa, bloqueadores, perguntas abertas e diferenças entre preview e estado final. Nunca declare sincronização completa sem releitura.
