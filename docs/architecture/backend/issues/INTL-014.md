# INTL-014 -- EventPlatformService: projeção idempotente + ledger

## Contexto
Materializar a governança de projeção: idempotência via ledger e roteamento DLQ.

## Spec de referência
- SPEC-03, SPEC-05, ADR-003

## Escopo
`EventPlatformService`: projeta documentos próprios (`ai-copilot-events`, `knowledge-nodes`) via
`IntlIndexPort`; registra `evento_indexado` (PK `evento_id` = doc-id determinístico); reprojeção =
no-op; documento inválido → DLQ (`parse_status=error`). Nenhuma escrita em fact de outro módulo.

## Resultado esperado
Projeções idempotentes e auditáveis; DLQ para inválidos.

## Critérios de aceite
- [ ] Reprojeção do mesmo `evento_id` não duplica documento
- [ ] Ledger reflete `INDEXADO`/`DLQ`
- [ ] Documento sem rastreabilidade → DLQ, não índice de destino
- [ ] INTL não escreve `revenue-events`/`journey-events`/`communication-events`

## Dependências
- INTL-010 (precede)

## Estimativa
M

## Prioridade
P6
