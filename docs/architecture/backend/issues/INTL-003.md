# INTL-003 -- API Copilot (conversa + perguntar)

## Contexto
Expor o AI Copilot conversacional via REST.

## Spec de referência
- SPEC-01, SPEC-02, `contracts/api-contract.md §1`

## Escopo
`CopilotController` + DTOs: abrir conversa, perguntar (`RespostaCopilotoResponse` com status +
citações), histórico. Orquestração RAG plugada em INTL-005.

## Resultado esperado
`/api/v1/copilot/**` operacional retornando os três status (RESPONDIDA/NAO_FUNDAMENTADA/DEGRADADA).

## Critérios de aceite
- [ ] `POST /copilot/conversas` abre conversa `ABERTA`
- [ ] `POST /copilot/conversas/{id}/perguntar` retorna resposta com `status` + `citacoes`
- [ ] Conversa inexistente → `404`
- [ ] Falha de IA não vira `5xx` (degrada)

## Dependências
- INTL-001 (precede)

## Estimativa
M

## Prioridade
P1
