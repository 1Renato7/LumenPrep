# Detecção de decisões materiais

## Regra central

Ative o registro quando o time ou um participante escolher entre alternativas plausíveis e essa escolha alterar produto, comportamento, arquitetura, contrato, escopo, qualidade, risco, prazo, ownership, integração, operação ou defesa técnica.

O registro acontece no momento da decisão. Não espere o fim da tarefa ou do hackathon, pois justificativas reconstruídas perdem contexto, alternativas e incerteza reais.

## Teste de materialidade

Uma escolha é material se responder `sim` a qualquer item de alto impacto ou a pelo menos dois itens comuns.

### Alto impacto — um item basta

- muda contrato, schema, estado, permissão, dinheiro, privacidade ou boundary de confiança;
- afeta outra pessoa, branch, consumidor ou ordem de integração;
- corta ou adiciona parte do MVP ou muda o fluxo da demo;
- aceita risco que pode quebrar o trial by fire, causar perda de dados ou impedir entrega;
- é cara, lenta ou perigosa de reverter;
- substitui ou contradiz decisão registrada anteriormente.

### Sinais comuns — dois itens bastam

- havia pelo menos uma alternativa plausível;
- um critério relevante precisou ser priorizado em detrimento de outro;
- a escolha cria dívida, limitação, fallback ou trabalho futuro;
- a escolha depende de hipótese ainda não totalmente validada;
- alguém poderá perguntar depois “por que fizemos assim?”;
- o resultado muda o próximo trabalho, os testes ou a evidência necessária;
- a escolha resolve uma falha, conflito de merge ou descoberta experimental.

Quando houver dúvida, aplique a pergunta: `um novo participante ou jurado entenderia por que o sistema tomou este rumo sem conversar com quem decidiu?` Se não, registre.

## Gatilhos típicos

- selecionar problema, usuário, fluxo principal, MVP ou não objetivo;
- escolher arquitetura, stack, provider, modelo, protocolo, armazenamento ou estratégia de deploy;
- definir ou alterar API, evento, schema, estados, erros, retry, idempotência ou ownership;
- escolher RAG, chunking, embedding, retrieval, threshold, fallback ou política de citação;
- definir fronteira de autoridade de agente, pagamento, confirmação humana ou reconciliação;
- escolher abordagem de UX, acessibilidade, comportamento de erro ou simplificação do fluxo;
- escolher entre corrigir, contornar, adiar, remover ou aceitar limitação;
- resolver conflito semântico entre branches ou alterar ordem de merge;
- cortar uma feature para aprofundar o caminho ponta a ponta;
- decidir como provar comportamento no navegador, trial by fire ou Q&A técnico.

## O que não registrar

- comandos mecânicos como instalar dependência já decidida, formatar ou renomear variável;
- seguir contrato congelado sem criar escolha nova;
- observação ou ideia ainda não escolhida;
- experimento descartável que não condiciona trabalho nem muda risco;
- detalhe local óbvio, facilmente reversível e sem efeito externo;
- cada microtarefa como se fosse uma decisão.

Se um detalhe aparentemente pequeno revelar consequência relevante — por exemplo, renomear um campo público — ele deixa de ser mecânico e deve ser registrado.

## Estados e autoridade

- `ACCEPTED`: escolha feita pela pessoa ou autoridade responsável.
- `EXPERIMENTAL`: escolha temporária que já condiciona trabalho e possui prazo/gatilho de validação.
- `VALIDATED`: a evidência confirmou os critérios declarados; use como atualização da entrada.
- `INVALIDATED`: a evidência refutou a escolha; preserve a entrada e crie a sucessora quando houver.
- `SUPERSEDED`: outra entrada passou a representar a decisão atual.

Não marque uma hipótese como decisão. Não marque consenso se houve apenas silêncio. Quando a autoridade necessária não estiver presente, deixe a questão `OPEN` no plano e registre somente depois da escolha.

## Momento de captura

1. Identifique a pergunta e as alternativas antes de a memória se perder.
2. Capture a decisão assim que confirmada.
3. Continue o trabalho sem exigir uma cerimônia longa; use fatos disponíveis e declare lacunas.
4. Enriqueça a entrada depois de teste, integração ou feedback.
5. Se a evidência mudar a rota, crie uma decisão sucessora ligada à anterior.
