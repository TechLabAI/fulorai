# INT-JRNY-004 -- Integração Elasticsearch (índices fact journey-events + routing-decisions)

## Contexto
Infraestrutura de cliente Elasticsearch (`direct-java-client`) para as projeções fact do JRNY.
Os índices são append-only e reconstruíveis a partir do PostgreSQL.

## Spec de referencia
- elastic-data-contract.md
- integration-contracts.md
- SPEC-10-integrations

## Escopo
- Config do cliente `co.elastic.clients:elasticsearch-java` (`ELASTIC_*` via `${VAR}`).
- Bootstrap/validação dos índices `journey-events` e `routing-decisions` (mapping conforme `elastic-data-contract.md`).
- `JourneyEventIndexPort` consumido por JRNY-011; operações best-effort (não bloqueiam decisão).
- Particionamento/filtro por `empresa_id`.

## Resultado esperado
JRNY indexa transições/decisões nos índices fact; Elastic indisponível não afeta o roteamento.

## Criterios de aceite
- [ ] Cliente Elastic conecta e valida os 2 índices fact.
- [ ] Index best-effort: erro de indexação não propaga ao roteamento.
- [ ] Documentos isolados por `empresa_id`.

## Dependencias
- INT-JRNY-001 (infra)

## Estimativa
M

## Prioridade
P4
