# Protocolo de teste no navegador

## Antes de abrir

- leia issue, plano, contrato, diff/revisão e critérios;
- identifique app/porta/comando oficial, serviços, env vars, seed e credenciais de teste;
- confira se processo já existe antes de iniciar outro;
- use dados sintéticos e ambiente local/sandbox;
- registre limitações de integração externa.

## Cenários

Derive um cenário por critério e acrescente riscos observáveis: double click, slow loading, erro de API, resposta vazia, entrada inválida, back/forward, refresh, estado stale, usuário sem permissão e viewport menor. Não force casos irrelevantes.

## Execução

Comece de estado conhecido. Registre URL/conta/fixture sem segredos. Execute ações semanticamente, espere sinais reais de conclusão e verifique resultado na UI e, quando necessário, na rede. Não use sleeps cegos como prova.

Depois de cada mudança material de estado, confirme a evidência mínima antes do próximo passo. Em falha, preserve console/request/status/payload sanitizado e passos de reprodução.

## Regressão e reteste

Teste o fluxo alterado, um consumidor direto e navegação adjacente de alto risco. Depois de correção, repita o cenário original desde estado limpo; não reteste apenas a última tela.

## Fechamento

Pare servidores iniciados apenas se for seguro e não forem necessários ao usuário. Informe processos deixados ativos, cenários, evidências, falhas, limitações e gate.
