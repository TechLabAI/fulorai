# JRNY-013 -- Idempotência (processed_events por eventId) + concorrência de inscrição

## Contexto
O roteamento é dirigido por eventos que podem ser reentregues. Reprocessar não pode duplicar
matrícula nem decisão. Garante idempotência por `eventId` e concorrência segura na inscrição ativa.

## Spec de referencia
- SPEC-05-idempotency-concurrency
- event-contracts.md §3

## Escopo
- Tabela/registro `processed_events` (eventId) persistido **antes** dos side effects nos consumers.
- Guard de concorrência via índice parcial `UNIQUE (lead_id, jornada_id) WHERE estado='ATIVA'`
  (segunda matrícula concorrente falha e é tratada como no-op).
- Janela de retenção ≥ 30 dias; DLQ `journey-os.dlq.<evento>` após 3 retries (1s/5s/30s).
- Avaliação determinística do `MotorRoteamento` (mesmo snapshot + versão de regras → mesma decisão).

## Resultado esperado
Reentrega de evento é no-op; nunca há duas inscrições ATIVAS para o mesmo (lead, jornada); decisões não duplicam.

## Criterios de aceite
- [ ] Reprocessar o mesmo `eventId` não gera nova matrícula/decisão.
- [ ] Inserção concorrente de inscrição ATIVA viola o índice parcial e é tratada graciosamente.
- [ ] Falha persistente → DLQ após os retries configurados.

## Dependencias
- JRNY-004 (roteamento)
- JRNY-008 (persistência)

## Estimativa
M

## Prioridade
P5
