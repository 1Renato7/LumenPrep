# Threat model

Construa o modelo antes de procurar vulnerabilidades isoladas.

## Contexto e ativos

- propósito do sistema e fluxo crítico da demo;
- dados públicos, internos, pessoais, financeiros e credenciais;
- ações irreversíveis ou de alto impacto;
- disponibilidade e integridade necessárias;
- terceiros, provedores, modelos, bases vetoriais e webhooks.

## Atores e privilégios

Liste usuário anônimo, usuário autenticado, tenant diferente, operador, administrador, serviço interno, integração externa e conteúdo controlado por atacante. Registre credenciais e capacidades assumidas para cada ator sem revelar valores secretos.

## Trust boundaries e data flows

Para cada fronteira, documente origem, destino, protocolo, autenticação, autorização, validação, dados transportados, persistência, logs e falha esperada. Inclua browser/servidor, API/banco, serviço/terceiro, aplicação/modelo e modelo/ferramenta.

## Abuse cases prioritários

- agir como outro usuário ou tenant;
- elevar privilégio ou contornar aprovação;
- ler, alterar ou apagar dados indevidos;
- duplicar pagamento, replay de webhook ou confundir estado;
- injetar comando, query, HTML, URL, template ou instrução para agente;
- induzir o modelo a revelar contexto ou acionar ferramenta;
- abusar de upload, parser, callback, redirect ou fetch server-side;
- esgotar recursos, cotas ou custos;
- comprometer dependência, pipeline, artefato ou secret.

Para cada caso, registre precondição, caminho, impacto, controle preventivo, controle detectivo e teste seguro. Priorize fronteiras com alto privilégio, dados sensíveis ou entrada não confiável.
