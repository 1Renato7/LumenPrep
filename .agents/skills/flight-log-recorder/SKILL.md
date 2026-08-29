---
name: flight-log-recorder
description: Detecta e registra decisões materiais e trade-offs reais no Flight Log colaborativo do repositório enquanto acontecem. Use automaticamente quando uma escolha de produto, arquitetura, escopo, integração, implementação, qualidade, risco, operação, Git ou demo mudar o trabalho ou rejeitar uma alternativa plausível; não use para passos mecânicos sem decisão.
---

# Flight Log Recorder

Mantenha `docs/flight-log.md` como memória auditável das decisões do time e como evidência para a defesa técnica. Registre o raciocínio contemporâneo à decisão; não reconstrua uma narrativa artificial no fim.

## Fluxo essencial

1. Detecte o ponto de decisão com [decision-detection.md](references/decision-detection.md). Não interrompa o trabalho por escolhas mecânicas.
2. Confirme o que foi decidido, por quem e com qual evidência. Não transforme sugestão, hipótese ou ação ainda não autorizada em decisão aceita.
3. Crie uma entrada imediatamente após a escolha e, quando possível, antes de implementá-la. Use o schema de [entry-schema.md](references/entry-schema.md).
4. Atribua ID único, lane correta e status honesto. Faça append; não reescreva o passado.
5. Propague a decisão às fontes operacionais afetadas — plano geral, contratos, planos individuais e Linear — mantendo links e IDs. O Flight Log preserva o porquê; não substitui a fonte de verdade atual.
6. Depois da validação, acrescente evidência e resultado à mesma entrada. Se a decisão mudar, crie nova entrada com `supersedes`; não apague nem adultere a anterior.

## Modos

- `CAPTURE`: registrar uma decisão que acabou de ser tomada.
- `ENRICH`: acrescentar evidência, resultado de teste ou consequência descoberta sem mudar a decisão original.
- `SUPERSEDE`: registrar uma nova decisão que reverte ou substitui outra.
- `FINALIZE`: construir o índice cronológico e a síntese para a banca seguindo [jury-finalization.md](references/jury-finalization.md), sem mover nem apagar entradas.

Declare o modo somente quando isso ajudar a equipe. O modo padrão é `CAPTURE`.

## Invariantes

- Registre todo trade-off real, incluindo cortes de escopo, alternativas rejeitadas, riscos aceitos, escolhas reversíveis que condicionam outras pessoas e decisões tomadas para recuperar uma falha.
- Uma entrada precisa explicar `por que esta opção neste contexto`, não apenas nomear tecnologia, framework ou feature.
- Separe fato observado, evidência, hipótese e inferência. Não invente benchmarks, testes, opiniões do usuário ou consenso.
- Inclua casos difíceis, custos e consequências negativas. Uma entrada promocional sem trade-off falha.
- Nunca inclua segredos, credenciais, tokens, dados pessoais desnecessários ou detalhes exploráveis sem necessidade.
- Não aceite risco financeiro, de segurança ou de privacidade em nome do usuário. Registre somente uma decisão tomada por autoridade apropriada.
- Preserve timestamps, autores e histórico. Correções factuais devem ser adendos explícitos.
- Use o protocolo de [collaboration-and-git.md](references/collaboration-and-git.md) para evitar que quatro branches destruam ou dupliquem o log.

## Relação com a banca

Use os critérios oficiais como lentes para melhorar a substância, nunca como checklist cosmético:

- profundidade supera dificuldade;
- algo funcionando ao vivo supera algo prometido;
- julgamento e defesa clara superam espetáculo;
- a banca avalia funcionamento ponta a ponta, profundidade e julgamento, aderência ao problema real, originalidade e experiência/clareza;
- quantidade de features, integrações, slides ou linhas de código não constitui evidência de qualidade.

Leia [jury-finalization.md](references/jury-finalization.md) ao preparar apresentação, code freeze ou entrega final.

## Saída

Atualize `docs/flight-log.md` na lane do responsável ou do time. Na resposta, informe o ID criado/atualizado e quais artefatos operacionais precisam ser sincronizados. Se faltar autoridade ou a escolha ainda estiver aberta, não fabrique uma entrada aceita: registre uma pergunta no plano apropriado e aguarde a decisão.
