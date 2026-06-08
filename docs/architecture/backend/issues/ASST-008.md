# ASST-008 -- Persistência JPA + adapters (AssetRepositoryPort)

## Contexto
Adapters de persistência que implementam as portas de saída do domínio, no schema do tenant.

## Spec de referencia
- SPEC-04-data-model-migrations
- SPEC-06-security

## Escopo
- `infrastructure/persistence/entity`: entities JPA (`AssetEntity`, `VersaoAssetEntity`, `AprovacaoEntity`, `TagAssetEntity`).
- `repository`: Spring Data JPA repos.
- `adapter`: `AssetRepositoryAdapter` implementa `AssetRepositoryPort` (mapeia entity↔domain).
- `MultiTenantConnectionProvider` aplica `search_path` do tenant (EmpresaContextHolder).

## Resultado esperado
Persistência funcional respeitando isolamento de schema; sem vazamento de entity para a API.

## Criterios de aceite
- [ ] Round-trip asset/versão/aprovação contra Testcontainers PostgreSQL.
- [ ] Queries operam no schema do tenant corrente (sem `empresa_id`).
- [ ] `:asst-service:architectureCheck` PASS (RULE-05 — infra não depende de api).

## Dependencias
- ASST-007 (precede)

## Estimativa
M

## Prioridade
P3
