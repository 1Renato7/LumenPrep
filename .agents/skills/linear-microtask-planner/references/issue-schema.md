# Schema das issues

## Container

Quando houver projeto do hackathon, associe todas as issues a ele. Caso use épico geral, descreva objetivo, MVP, demo, divisão do time, links dos planos e critérios finais. Não o use como substituto das issues executáveis.

## Parent issue por objetivo

- ID `OBJ-*`, missão e resultado observável;
- responsável primário;
- contexto da demo;
- componentes/dados sob ownership;
- contratos principais;
- dependências entre objetivos;
- critérios globais e Definition of Done;
- links para plano geral e individual.

## Microtarefa

Use este corpo:

```markdown
## Contexto
Explique por que a tarefa existe, como contribui para o objetivo e onde aparece no plano/demo. Inclua ID e versão do plano.

## Objetivo
Uma frase concreta sobre o que estará verdadeiro ao terminar.

## Escopo
**Incluído:**
- resultado concreto

**Fora de escopo:**
- item e issue/owner onde vive, quando conhecido

## Inputs e output
- Inputs/dependências disponíveis
- Artefato ou comportamento entregue
- Localização proposta/real

## Contratos e decisões
- CMP-*, CTR-*/versão, DEC-* e exemplos necessários

## Passos sugeridos
1. Passo acionável
2. Passo acionável

## Critérios de aceitação
- [ ] Critério binário e verificável

## Dependências
- Bloqueada por: TASK-*/issue real ou Nenhuma
- Bloqueia: TASK-*/issue real ou Nenhuma

## Testes e evidências
- Comandos/cenários
- Evidência esperada
- Navegador quando aplicável

## Handoff
- Consumidor, como localizar e como validar

## Perguntas abertas
> ⚠️ A definir com o time: pergunta, owner e prazo

## Definition of Done
- [ ] Código/artefato concluído
- [ ] Testes relevantes passando
- [ ] Revisão concluída
- [ ] Navegador validado quando aplicável
- [ ] Contratos/planos sincronizados
```

Omita `Perguntas abertas` somente se realmente não houver. Passos são sugestão; resultado, contratos e critérios são obrigatórios.

## Campos do Linear

- título imperativo e específico;
- assignee confirmado;
- parent e projeto/ciclo confirmados;
- labels existentes e relevantes;
- prioridade derivada de caminho crítico/risco;
- estimativa apenas na convenção usada pelo time;
- estado inicial real do time;
- relações reais `blocked by`/`blocks`.
