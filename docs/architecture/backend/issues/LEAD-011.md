# LEAD-011 -- Elasticsearch leads index adapter (LeadSearchPort)

## Contexto
Adapter de busca que indexa o lead no índice `leads` (classe *dimension*) e serve a fila priorizada
e a segmentação, com degradação graciosa se o Elastic cair.

## Spec de referencia
- SPEC-10-integrations
- SPEC-01-api-surface

## Escopo
- `infrastructure.search` implementa `LeadSearchPort` (Java client / elastic-client-lib).
- (Re)indexa o documento do lead em `lead.score.atualizado`/`segmento.alterado`.
- Consulta paginada/filtrada (segmento, score, estado) para `GET /leads` e `GET /segments/{id}/leads`.
- Apenas campos controlados (sem PII além do necessário — LGPD).

## Resultado esperado
Fila priorizada por score servida via Elastic; outage degrada leitura, não a escrita transacional.

## Criterios de aceite
- [ ] Mudança de score/segmento (re)indexa o lead.
- [ ] Elastic indisponível → escrita transacional preservada + reindex retried out-of-band.
- [ ] Listagens ordenadas por score desc; sem PII não-controlada no índice.

## Dependencias
- LEAD-009 (persistência)

## Estimativa
M

## Prioridade
P4
