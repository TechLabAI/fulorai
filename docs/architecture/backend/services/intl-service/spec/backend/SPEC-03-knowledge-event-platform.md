# SPEC-03 — Knowledge Base & Event Platform

> Sub-feature crítica. ADR-003 (plataforma de dados descentralizada), ADR-005.
> Ref: `contracts/data-model.md`, `contracts/event-contracts.md`, `contracts/hub-integration.md §5`.

## Objetivo

(a) Gerir a Base de Conhecimento (curadoria + indexação em `knowledge-nodes`); (b) governar a
plataforma de dados Elastic (contrato de rastreabilidade, DLQ, registro de índices/ILM) e projetar
os índices próprios de INTL; (c) prover a leitura analítica cross-index.

## Escopo

**In:** CRUD/curadoria de `no_conhecimento`; ingestão por `asset.versao.publicada`; geração de
embedding (TechLab AI `knowledge`); projeção própria (`ai-copilot-events`, `knowledge-nodes`) com
bloco de rastreabilidade + DLQ; ledger `evento_indexado`; leitura analítica (`/analytics`).
**Out:** reindexação dos *facts* de outros módulos; ingestão de observabilidade
(`app-logs`/`traces`/`metrics`/`integration-logs` — infra/APM); Integration Hub externo (pós-MVP).

## Decisões técnicas

- **Descentralização (ADR-003):** cada produtor escreve seus *facts*; INTL governa o contrato e
  escreve só os próprios; leitura analítica é read-only sobre os índices alheios.
- **Rastreabilidade (D-269):** bloco de 8 campos + `empresa` obrigatório; violação → DLQ.
- **Idempotência:** doc-id determinístico + ledger `evento_indexado`.
- **Governança de índices:** mapeamentos/ILM versionados como config (sem tabela PG no MVP).

## Implementação

- `KnowledgeIngestService` (criar/editar/arquivar nó; consumir `asset.versao.publicada`).
- `EventPlatformService` (projeção com validação de rastreabilidade; roteamento DLQ; ledger).
- `AnalyticsService` (agrega *facts* via `SearchPort`, filtrando `empresa`).
- `TraceabilityValidator` (domain service POJO) valida o bloco de 8 campos antes do `IndexPort`.

## Casos de borda

- Asset reentregue → atualiza nó (não duplica).
- Documento sem rastreabilidade → DLQ (`parse_status=error`), nunca índice de destino.
- Embedding indisponível → nó fica `RASCUNHO`, `503`.

## Critérios de aceite (EARS)

- WHEN um nó é indexado, THE SYSTEM SHALL projetar `knowledge-nodes` com o bloco de rastreabilidade e `embedding` (ou marcador) e marcar o nó `INDEXADO`.
- IF um documento não contém os 8 campos de rastreabilidade + `empresa`, THEN THE SYSTEM SHALL roteá-lo para `journey-os_dlq` e não indexá-lo no destino.
- WHEN a mesma projeção (mesmo doc-id) é reprocessada, THE SYSTEM SHALL tratá-la como no-op (idempotência via `evento_indexado`).
- THE SYSTEM SHALL nunca escrever nos índices de *fact* de outros módulos.
- WHEN uma consulta analítica é feita, THE SYSTEM SHALL agregar apenas documentos da `empresa` do solicitante.
- WHEN `journey-os.asset.versao.publicada` é consumido, THE SYSTEM SHALL criar/atualizar um nó `fonte=ASSET` de forma idempotente por `assetId:versao`.
