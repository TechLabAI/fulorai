# JRNY-011 -- Projeção Elastic (journey-events + routing-decisions, fact, best-effort)

## Contexto
Telemetria/auditoria de jornada projetada em dois índices fact: `journey-events` (transições) e
`routing-decisions` (decision log). Projeção **best-effort** que nunca bloqueia a decisão; o
PostgreSQL é a fonte da verdade, e os índices são reconstruíveis.

## Spec de referencia
- SPEC-07-observability-health
- SPEC-10-integrations
- elastic-data-contract.md

## Escopo
- `JourneyEventIndexPort` → adapter Elastic (`direct-java-client`) para os índices `journey-events`/`routing-decisions`.
- Indexação na transição de estágio (journey-events) e na gravação de decisão (routing-decisions).
- Filtragem por `empresa_id` (sem vazamento na busca/auditoria).
- Index best-effort: falha de indexação loga e segue; reconciliação posterior (não reverte decisão).

## Resultado esperado
Decisões e transições aparecem nos índices fact para analytics/auditoria; queda do Elastic não afeta o roteamento.

## Criterios de aceite
- [ ] Transição → documento em `journey-events`; decisão → documento em `routing-decisions`.
- [ ] Elastic indisponível não reverte/atrasa a decisão (best-effort).
- [ ] Documentos carregam `empresa_id`; consulta não cruza empresa.

## Dependencias
- JRNY-006 (eventos/decisões)
- INT-JRNY-004 (infra Elasticsearch)

## Estimativa
M

## Prioridade
P4
