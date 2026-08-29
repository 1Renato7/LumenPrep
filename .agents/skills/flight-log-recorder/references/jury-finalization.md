# Fechamento do Flight Log para a banca

## Critérios oficiais a preservar

Três princípios orientam a leitura:

1. **Depth over difficulty:** escopo modesto resolvido profundamente vale mais que ambição superficial.
2. **Working beats promised:** a banca avalia o que funciona ao vivo, não promessas nos slides.
3. **Judgment beats spectacle:** a defesa técnica pesa tanto quanto a demo; raciocínio claro supera espetáculo inexplicável.

As cinco lentes são:

1. funciona ponta a ponta e reage corretamente ao trial by fire;
2. possui profundidade arquitetural, decisões explicáveis, alternativas rejeitadas e trade-offs reais;
3. resolve o problema escrito, inclusive casos difíceis, em vez de um produto genérico adjacente;
4. contém insight, abordagem ou mecanismo original;
5. oferece experiência utilizável, pitch claro, demo legível e repositório compreensível para quem não participou.

Não trate quantidade de features, slides, integrações ou linhas de código como pontuação. Nomear um framework não é decisão; explicar por que ele venceu neste contexto é.

## Preparação contínua

Desde o planejamento:

- priorize a menor fatia ponta a ponta executável nas primeiras horas;
- use o restante do tempo para profundidade, casos difíceis, robustez e ensaio do trial by fire;
- associe decisões importantes a evidência executada;
- preserve decisões que falharam e como o time aprendeu; julgamento inclui corrigir rota;
- garanta README, diagrama de arquitetura e Decision/Flight Log como entregáveis coerentes.

## Modo `FINALIZE`

Execute antes do code freeze com tempo para corrigir lacunas. Não invente decisões retroativas.

1. Congele novas reorganizações e sincronize todas as branches.
2. Valide integridade segundo `collaboration-and-git.md`.
3. Liste as decisões por timestamp sem mover as entradas originais.
4. Atualize o índice cronológico do topo com ID, escolha, owner, status e evidência principal.
5. Selecione de três a sete decisões mais consequenciais para a síntese executiva. Cobrir tudo superficialmente é pior que defender profundamente escolhas importantes.
6. Para cada decisão selecionada, confirme contexto, alternativas plausíveis, por que foram rejeitadas, trade-off negativo, evidência ao vivo e caso difícil.
7. Marque honestamente `NOT RUN`, hipótese restante ou risco residual.
8. Verifique coerência com plano atual, diagrama, README, demo e código.
9. Prepare perguntas de Q&A: `por que`, `por que não`, `o que falha`, `como sabem`, `o que mudariam com mais tempo`.
10. Faça uma leitura por alguém que não participou da decisão. Se exigir contexto oral, enriqueça a entrada com fatos reais.

## Síntese executiva

A síntese no topo deve responder em poucos parágrafos:

- qual problema real orientou as escolhas;
- qual foi a menor fatia ponta a ponta e por que;
- quais trade-offs definiram a arquitetura;
- como o time reagiu a evidências e falhas;
- o que funciona ao vivo, quais casos difíceis foram testados e quais limites permanecem.

Não duplique toda a narrativa das entradas. Use links por ID.

## Matriz de prontidão

Para cada lente, registre `READY`, `PARTIAL` ou `NOT READY` e evidência:

| Lente | Pergunta de verificação |
| --- | --- |
| Funciona? | Existe execução ponta a ponta e caso adverso reproduzível? |
| Profundidade e julgamento | As maiores decisões têm alternativas, trade-offs e evidência? |
| Problema real | As decisões citam o enunciado e casos difíceis específicos? |
| Originalidade | O insight original está explicado como mecanismo, não slogan? |
| Experiência e clareza | Um estranho entende repo, demo e raciocínio sem explicação privada? |

Uma lente `PARTIAL` não deve ser mascarada. Transforme-a em ação concreta ou limite assumido.

## Gate final

O Flight Log está `JURY READY` somente se:

- nenhuma decisão material conhecida está ausente;
- as entradas principais contêm alternativas reais e consequências negativas;
- afirmações de funcionamento possuem evidência executada;
- estados atuais e históricos estão distinguíveis;
- decisões revertidas continuam visíveis;
- o arquivo está legível, sem segredos e com links válidos;
- ao menos um caso difícil do problema e um trial by fire estão ligados às decisões relevantes;
- a equipe consegue defender as escolhas sem depender de buzzwords.

Caso contrário, use `JURY LOG BLOCKED` e liste lacunas factuais. Nunca preencha lacunas com justificativas inventadas.
