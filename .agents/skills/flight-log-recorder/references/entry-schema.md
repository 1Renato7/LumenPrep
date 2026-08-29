# Schema de uma entrada do Flight Log

## Identidade

Use `FL-YYYYMMDD-LANE-NNN`, em que `LANE` é `TEAM`, `ANDRE`, `ALTOE`, `ROGERIO` ou `RENATO`. Cada lane incrementa sua própria sequência. IDs nunca são reutilizados ou renumerados.

O timestamp usa ISO 8601 com timezone. O título descreve a escolha, não o assunto genérico: `Adotar mock versionado antes das branches consumidoras`, não `Backend`.

## Template completo

```markdown
### FL-YYYYMMDD-LANE-NNN — <decisão em uma frase>

- **Timestamp:** YYYY-MM-DDTHH:MM:SS-03:00
- **Status:** ACCEPTED | EXPERIMENTAL | VALIDATED | INVALIDATED | SUPERSEDED
- **Decision owner:** <pessoa ou Team>
- **Participantes:** <quem contribuiu ou confirmou>
- **Categoria:** product | scope | architecture | contract | data | AI/RAG | payments | security | UX | quality | operations | Git/integration | demo
- **Escopo:** <componentes, fluxo ou tarefa afetada>
- **Links:** <DEC-*, CTR-*, TASK-*, issue Linear, branch, PR, commit, teste ou evidência>
- **Supersedes / superseded by:** <ID ou não aplicável>

#### Contexto e pergunta

<Qual situação concreta exigiu uma escolha? Que restrição, falha, prazo ou desconhecido existia?>

#### Decisão

<O que foi escolhido, com fronteiras e condições suficientes para outra pessoa executar?>

#### Critérios e por que agora

<Quais critérios dominaram e por que a decisão não poderia continuar aberta?>

#### Alternativas consideradas

| Alternativa | Benefícios | Custos/riscos | Evidência ou hipótese | Por que não foi escolhida agora |
| --- | --- | --- | --- | --- |
| ... | ... | ... | FACT / TEST / ASSUMPTION | ... |

#### Evidência, hipóteses e desconhecidos

- **FACT:** <observado no enunciado, código, documentação ou execução>
- **TEST:** <teste executado e resultado; ou NOT RUN>
- **ASSUMPTION:** <hipótese, owner e prazo/gatilho de validação>
- **UNKNOWN:** <lacuna restante e impacto>

#### Trade-offs aceitos

- **Ganhamos:** <benefícios concretos>
- **Abrimos mão de:** <capacidade, flexibilidade, tempo ou qualidade>
- **Dívida/limitação:** <consequência negativa real>
- **Risco residual:** <o que ainda pode falhar e quão observável é>

#### Consequências e propagação

- **Produto/demo:** <impacto>
- **Arquitetura/contratos:** <IDs e versões afetados>
- **Pessoas/branches:** <quem precisa saber ou mudar algo>
- **Plano/Linear:** <artefatos a sincronizar>
- **Testes/observabilidade:** <prova ou sinal requerido>

#### Validação e trial by fire

- **Hipótese verificável:** <o que esperamos observar>
- **Caminho feliz:** <prova ponta a ponta>
- **Caso difícil/adverso:** <mudança que um jurado pode fazer ao vivo>
- **Resultado observado:** <PASS / FAIL / NOT RUN + evidência>
- **Fallback:** <comportamento demonstrável se a dependência falhar>

#### Gatilhos de revisão

<Evidência, prazo, custo, falha ou mudança de requisito que obriga reavaliar.>

#### Adendos

- <timestamp, autor, evidência nova; nunca reescreva silenciosamente a decisão original>
```

## Profundidade proporcional

Use o template inteiro para decisões transversais, irreversíveis, de risco ou relevantes à banca. Em decisões locais materiais, mantenha todas as seções, mas respostas curtas são válidas quando explícitas. `Não aplicável` exige uma razão; campos vazios são lacunas.

Uma boa entrada permite que alguém:

1. diferencie fatos de hipóteses;
2. reproduza o raciocínio sem reunião oral;
3. veja uma alternativa genuinamente rejeitada;
4. encontre a consequência negativa aceita;
5. saiba como provar ou refutar a decisão;
6. localize código, plano, contrato e evidência relacionados.

## Antipadrões

- `Escolhemos Next.js porque é rápido.` — não define rápido, alternativas ou custo.
- `Decidimos usar IA porque o hackathon é de agentes.` — confunde tema com necessidade.
- lista de tecnologias sem pergunta de decisão;
- justificativa escrita retroativamente para parecer inevitável;
- alternativas caricatas que ninguém consideraria;
- afirmar `testado` sem comando, cenário ou evidência;
- esconder risco para tornar a entrada mais convincente;
- medir profundidade por tamanho do texto.

## Atualização posterior

Acrescente adendos para evidência e resultado. Mudança editorial pequena pode ser corrigida com adendo. Mudança da escolha, boundary ou risco aceito exige nova entrada e vínculos bidirecionais `supersedes`/`superseded by`.
