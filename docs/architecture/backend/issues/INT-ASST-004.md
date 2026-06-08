# INT-ASST-004 -- Elasticsearch índice assets (direct java client)

## Contexto
Integração com Elasticsearch para o índice dimension `assets` (busca + Asset Intelligence).

## Spec de referencia
- contracts/integration-contracts.md
- SPEC-10-integrations

## Escopo
- Elastic direct java client (`ELASTIC_URIS`, `ELASTIC_ASSETS_INDEX`); sem Logstash.
- Mapeamento do documento `assets` conforme `elastic-data-contract.md` (inclui `empresaId`).
- Upsert best-effort não bloqueante; reconciliação/reindex a partir do PostgreSQL.

## Resultado esperado
Documentos de asset indexados e consultáveis, isolados por tenant; índice reconciliável.

## Criterios de aceite
- [ ] Upsert na criação/publicação/mudança de tags.
- [ ] Queries filtram por `empresaId`.
- [ ] Elastic down não falha o write path.

## Dependencias
- Elastic stack (existente); ASST-011

## Estimativa
M

## Prioridade
P4
