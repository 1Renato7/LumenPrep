# Formato dos achados

Ordene por severidade e use localização mínima precisa.

- `P0`: perda/corrupção ampla, exposição crítica ou sistema inutilizável; bloqueia imediatamente.
- `P1`: bug grave provável em fluxo principal, contrato ou segurança funcional; bloqueia.
- `P2`: defeito relevante com alcance/precondição limitada; normalmente bloqueia a tarefa afetada.
- `P3`: risco real de baixo impacto ou hardening; não bloqueante quando documentado.

Cada achado contém título, prioridade, arquivo/linha, comportamento esperado, cenário reproduzível, comportamento atual, causa, impacto, evidência/teste e correção segura. Não alegue certeza além da evidência.

Depois dos achados, informe gate, comandos/testes executados, limitações e próximos passos. Se não houver achados, diga explicitamente e ainda registre cobertura/limitações.
