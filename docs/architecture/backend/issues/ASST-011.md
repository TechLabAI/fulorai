# ASST-011 -- Busca + projeção Elastic (índice assets)

## Contexto
Busca full-text e por filtros de assets via índice Elastic `assets` (dimension), com fallback
para PostgreSQL.

## Spec de referencia
- SPEC-10-integrations
- contracts/integration-contracts.md

## Escopo
- `AssetSearchPort` (out) + `AssetSearchAdapter` (Elastic direct java client).
- `BuscarAssetsService` + `GET /api/v1/assets?q=&tipo=&tag=&estado=`.
- Upsert do documento `assets` na criação/publicação/mudança de tags (best-effort, `empresaId` no doc).
- Fallback: indisponibilidade do Elastic → filtragem via PostgreSQL.

## Resultado esperado
Busca funcional por tipo/tag/estado + full-text; índice reconciliável a partir do PostgreSQL.

## Criterios de aceite
- [ ] `q` resolve via Elastic; com Elastic down, lista cai para PostgreSQL.
- [ ] Documentos filtrados por `empresaId` (sem vazamento cross-tenant).
- [ ] Falha de index não falha o write path.

## Dependencias
- ASST-008 (precede); INT-ASST-004

## Estimativa
M

## Prioridade
P4
