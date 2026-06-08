Feature: Plataforma de dados & leitura analítica

# Refs: SPEC-03 (event platform), ADR-003 (indexação descentralizada), api-contract §3
# Invariantes: INV-1 (rastreabilidade), INV-6 (descentralização)

Background:
  Given uma empresa "acme" provisionada
  And um usuário autenticado com a permissão "intl.analytics.read"

Scenario: Documento sem bloco de rastreabilidade vai para a DLQ
  Given uma projeção de "ai-copilot-events" sem o bloco de rastreabilidade completo
  When INTL tenta projetar o documento
  Then o documento é roteado para o índice "journey-os_dlq" com parse_status "error"
  And o documento não é indexado no índice de destino

Scenario: Projeção idempotente não duplica documento
  Given uma resposta de copiloto já projetada com doc-id determinístico
  When a mesma projeção é reprocessada
  Then o ledger evento_indexado registra status "INDEXADO" uma única vez
  And não há documento duplicado em "ai-copilot-events"

Scenario: INTL não escreve facts de outros módulos
  When INTL processa a leitura analítica de funil
  Then INTL não escreve nos índices "revenue-events", "journey-events" ou "communication-events"
  And INTL apenas lê esses índices

Scenario: Leitura de funil é filtrada por empresa
  Given existem facts das empresas "acme" e "globex"
  When o usuário da empresa "acme" consulta o funil
  Then o resultado agrega apenas documentos da empresa "acme"

Scenario: Uso do copiloto agrega métricas de custo e fundamentação
  Given respostas de copiloto registradas no período
  When o usuário consulta a analítica de uso do copiloto
  Then o resultado traz totalRespostas, custoTokens, taxaFundamentadas e taxaDegradadas

Scenario: Seed por empresa.provisionada é idempotente
  When o evento "journey-os.empresa.provisionada" para "acme" é consumido duas vezes
  Then existe exatamente uma base de conhecimento para "acme"
