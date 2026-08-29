# Protocolo de descoberta

## Entradas mínimas

Colete enunciado integral, critérios de avaliação, tempo disponível, regras, recursos permitidos, stack existente, dados/APIs disponíveis, restrições de deploy, roteiro esperado e habilidades/preferências de cada participante. Leia o repositório quando já existir. Preserve a redação dos critérios como fatos e separe-a de interpretações estratégicas do time.

Se uma entrada não estiver disponível, marque-a como desconhecida e determine se bloqueia planejamento ou pode virar spike com prazo.

## Leitura individual

Antes da convergência, registre para cada participante:

- interpretação do problema e usuário;
- resultado que considera mais valioso;
- solução ou abordagem sugerida;
- maior risco técnico ou de produto;
- integração externa necessária;
- parte que gostaria ou conseguiria executar melhor;
- dúvida que precisa ser resolvida.

Não atribua uma ideia automaticamente a quem a sugeriu.

## Síntese

Separe em tabelas:

- `FACT`: afirmado pelo enunciado, regra ou evidência inspecionada;
- `ASSUMPTION`: hipótese necessária, com owner, prazo e fallback;
- `OPEN`: pergunta cuja resposta muda arquitetura, escopo ou demo;
- `DECISION`: escolha tomada, alternativas e razão;
- `NON-GOAL`: deliberadamente fora do MVP.

Resolva primeiro dúvidas que alteram contratos ou caminho crítico. Perguntas menores podem virar spikes timeboxed.

Ao confirmar uma `DECISION` material, acione `$flight-log-recorder` imediatamente. Não espere o fechamento da descoberta: decisões sobre interpretação do problema, usuário, MVP, fatia ponta a ponta, não objetivos e critérios dominantes já pertencem ao Flight Log.

## Seleção do MVP

Compare opções por valor demonstrável, aderência ao critério do hackathon, viabilidade no tempo, dependências externas, risco, capacidade do time e facilidade de fallback. Prefira uma fatia vertical completa a muitas telas ou serviços desconectados. Não escolha o desafio mais difícil só pela dificuldade nem aumente features para aparentar abrangência; selecione escopo que possa funcionar cedo e ser aprofundado com casos difíceis.

Defina uma frase de valor, um usuário primário, um fluxo principal da demo, até três capacidades essenciais, não objetivos e fallback para integrações externas.

## Fechamento

A descoberta está pronta quando o time consegue explicar o problema, o resultado, a demo, as maiores hipóteses e o que não será feito. Se duas interpretações incompatíveis ainda produzirem arquiteturas diferentes, pare e peça decisão antes de aprofundar o plano.
