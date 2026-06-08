Feature: AI Copilot — respostas fundamentadas via RAG

# Refs: SPEC-02 (Copilot orchestration), ADR-005 (RAG fundamentado), api-contract §1
# Invariantes: INV-2 (fundamentação), INV-3 (sem IA direta), INV-5 (isolamento de tenant)

Background:
  Given uma empresa "acme" provisionada com base de conhecimento
  And um usuário autenticado com a permissão "intl.copilot.use"
  And uma conversa de copiloto aberta

Scenario: Pergunta com evidência suficiente retorna resposta fundamentada
  Given existem nós de conhecimento indexados relevantes à pergunta
  And a TechLab AI está disponível
  When o usuário pergunta "qual copy converteu melhor no último lançamento?"
  Then a resposta tem status "RESPONDIDA"
  And a resposta contém ao menos uma citação com documentoId e indice
  And um evento "journey-os.copilot.resposta.gerada" é publicado
  And um documento é projetado no índice "ai-copilot-events" com o bloco de rastreabilidade

Scenario: Pergunta sem evidência suficiente é marcada nao_fundamentada
  Given não há nós de conhecimento nem facts relevantes à pergunta
  When o usuário pergunta "qual a previsão de churn para o próximo trimestre?"
  Then a resposta tem status "NAO_FUNDAMENTADA"
  And a resposta não apresenta fato como confirmado
  And a resposta não contém citação fundamentadora

Scenario: TechLab AI indisponível degrada para recuperação-apenas
  Given existem nós de conhecimento relevantes à pergunta
  And a TechLab AI está indisponível
  When o usuário pergunta "resumo do funil desta semana"
  Then a resposta tem status "DEGRADADA"
  And a resposta lista a evidência recuperada sem síntese de IA
  And o serviço responde 200 e não propaga erro 5xx
  And o evento publicado registra modelo nulo e custoTokens igual a zero

Scenario: Recuperação é sempre filtrada pela empresa do solicitante
  Given existe um nó de conhecimento da empresa "globex"
  When o usuário da empresa "acme" pergunta algo coberto por aquele nó
  Then nenhuma citação referencia documento da empresa "globex"

Scenario: Custo e latência são registrados na resposta fundamentada
  Given a TechLab AI está disponível e existem nós relevantes
  When o usuário faz uma pergunta fundamentável
  Then a mensagem do copiloto registra modelo, custoTokens e latenciaMs

Scenario: Pergunta em conversa inexistente retorna 404
  When o usuário pergunta em uma conversa que não existe na empresa
  Then o serviço responde 404
