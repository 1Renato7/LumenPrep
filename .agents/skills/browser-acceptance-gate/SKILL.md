---
name: browser-acceptance-gate
description: Valida no navegador real do Codex o comportamento observável de uma tarefa em uma aplicação local, incluindo interações, estados, console e rede. Use depois da revisão de código em mudanças de UI ou fluxos ponta a ponta; não use como substituto de testes unitários ou para código sem superfície executável no navegador.
---

# Browser Acceptance Gate

Valide a aplicação em execução, não apenas o código.

1. Descubra o comando oficial e inicie ou reutilize o servidor local sem matar processos não relacionados.
2. Leia critérios de aceitação e identifique o fluxo mínimo afetado.
3. Use o navegador local disponível no Codex. Teste o happy path e os estados relevantes de loading, vazio, validação e erro.
4. Clique e digite como usuário real; confirme navegação, persistência, feedback, prevenção de ações duplicadas e resultado final.
5. Inspecione console e chamadas de rede relevantes. Diferencie falhas da aplicação de limitações do ambiente.
6. Teste pelo menos um viewport desktop e um mobile quando a interface for responsiva.
7. Registre passos, resultado esperado, resultado observado e evidências. Use [a matriz](references/acceptance-matrix.md).
8. Classifique como `PASS`, `PASS WITH LIMITATIONS` ou `FAIL`.

Se não existir interface para uma mudança backend, valide API ou integração com a ferramenta apropriada e execute no navegador todo fluxo consumidor disponível. Nunca afirme que o navegador foi testado se não foi operado.
