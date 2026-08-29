# Protocolo de avaliação RAG

Mantenha um conjunto pequeno e versionado com:

- perguntas fáceis, ambíguas e compostas;
- perguntas sem resposta no corpus;
- documentos conflitantes ou desatualizados;
- conteúdo com instruções maliciosas;
- casos que exigem filtro de usuário ou organização.

Meça separadamente:

- recuperação: presença da evidência correta nos resultados e posição;
- geração: correção, completude, grounding e qualidade das citações;
- sistema: latência, custo, taxa de fallback e isolamento de acesso.

Não ajuste o sistema apenas com exemplos usados na demonstração. Registre falhas representativas e a mudança que melhorou ou piorou cada métrica.
