# Backend API Cross-Link — INTL (FE ↔ intl-service)

> O FE INTL consome **somente** o `intl-service` via `@journeyos/shared/access-http-base`.
> Fonte da verdade do contrato: `docs/architecture/backend/services/intl-service/contracts/api-contract.md`.
> Este documento versiona o acoplamento FE↔BE e registra diffs/pendências.

## Endpoints consumidos

| Feature FE | Método + Path | Permissão | Status esperados |
|---|---|---|---|
| copilot | `POST /api/v1/copilot/conversas` | `intl.copilot.use` | 201 |
| copilot | `POST /api/v1/copilot/conversas/{id}/perguntar` | `intl.copilot.use` | 200 (RESPONDIDA\|NAO_FUNDAMENTADA\|DEGRADADA), 404 |
| copilot | `GET /api/v1/copilot/conversas/{id}` | `intl.copilot.read` | 200, 404 |
| knowledge | `GET /api/v1/knowledge/nos` | `intl.knowledge.read` | 200 |
| knowledge | `GET /api/v1/knowledge/nos/{id}` | `intl.knowledge.read` | 200, 404 |
| knowledge | `POST /api/v1/knowledge/nos` | `intl.knowledge.write` | 201 |
| knowledge | `PUT /api/v1/knowledge/nos/{id}` | `intl.knowledge.write` | 200 |
| knowledge | `POST /api/v1/knowledge/nos/{id}/indexar` | `intl.knowledge.write` | 202, 503 |
| knowledge | `DELETE /api/v1/knowledge/nos/{id}` | `intl.knowledge.write` | 200 |
| analytics | `GET /api/v1/analytics/funil` | `intl.analytics.read` | 200 |
| analytics | `GET /api/v1/analytics/copilot` | `intl.analytics.read` | 200 |

## Headers (injetados por interceptors)

- `Authorization: Bearer <jwt>` — `@journeyos/shared/auth-session`.
- `X-Empresa-Id` — `@journeyos/shared/empresa-context` (tenant; BE também valida o claim `empresa`).
- `X-Correlation-Id` — gerado/propagado por `access-http-base`.

## Diffs / pendências conhecidas

- **Shape de `citacoes`** (`{ documentoId, indice, trecho, score }`) pode evoluir quando o sync da
  TechLab AI (`openapi.json`) for concluído (P3). O FE trata `score` como opcional na renderização.
- **Deep-link de citação → documento dono** (LEAD/JRNY/SALE) não tem rota cross-módulo no MVP — o FE
  abre um painel lateral local com `trecho`/metadados (ver `06-risks-gaps-assumptions.md` R3).
- **Degradação:** o FE assume que falha de IA no Copilot **nunca** retorna `5xx` (BE degrada para
  `200/DEGRADADA`, conforme api-contract §1.2). Status desconhecido é tratado como `DEGRADADA` (R6).
- **Streaming:** sem endpoint de streaming no contrato — flag `intl.copilot-streaming` reservada
  (ADR-005).

## Referência

- BE: `docs/architecture/backend/services/intl-service/contracts/api-contract.md`
- BE eventos: `intl-service/contracts/event-contracts.md` (não consumidos diretamente pelo FE)
