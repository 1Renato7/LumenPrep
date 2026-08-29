---
name: browser-acceptance-gate
description: Valida no navegador real do Codex o comportamento observável de uma tarefa em uma aplicação local, incluindo interações, estados, console e rede. Use depois da revisão de código em mudanças de UI ou fluxos ponta a ponta; não use como substituto de testes unitários ou para código sem superfície executável no navegador.
---

# Browser Acceptance Gate

Valide a aplicação em execução, não apenas o código.

1. **Preparação:** siga [test-protocol.md](references/test-protocol.md). Descubra comandos oficiais, dependências, dados/conta de teste, URL e critérios. Inicie ou reutilize servidor sem matar processos alheios.
2. **Plano de cenários:** mapeie cada critério para cenário, precondição, ações, resultado, console/rede e evidência. Priorize fluxo alterado e dependências downstream.
3. **Execução real:** use o navegador local disponível no Codex, clique/digite como usuário e não simule sucesso por leitura de código.
4. **Estados:** cubra happy path, loading, vazio, validação, erro, retry, ação duplicada, refresh/persistência e autorização quando aplicáveis.
5. **Diagnóstico:** inspecione console e rede relevante, correlacione falha com request/response e diferencie bug, dado incorreto, servidor e limitação ambiental.
6. **Experiência:** valide feedback, navegação, foco/teclado básico, responsividade desktop/mobile e acessibilidade observável proporcional à mudança.
7. **Evidência:** preencha [acceptance-matrix.md](references/acceptance-matrix.md) com passos reproduzíveis; screenshots somente quando agregarem prova visual.
8. **Gate:** `PASS`, `PASS WITH LIMITATIONS` ou `FAIL`. Qualquer critério crítico não testado vira limitação bloqueante, não aprovação silenciosa.

Se não existir interface para uma mudança backend, valide API ou integração com a ferramenta apropriada e execute no navegador todo fluxo consumidor disponível. Nunca afirme que o navegador foi testado se não foi operado.
