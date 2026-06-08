# 06 — Risks, Gaps & Assumptions — ASST (Asset Hub)

> Itens a validar antes/durante specs e implementação. Cada risco com mitigação.

## 1. Riscos

| # | Risco | Impacto | Mitigação |
|---|---|---|---|
| R1 | **TechLab AI indisponível/lento** degrada o Asset Studio | Médio | Timeout + circuit breaker (Resilience4j) + fallback graceful; CRUD/aprovação independem da IA (`ADR-003`). |
| R2 | **Custo/latência** de `document_composition` em volume | Médio | Composição sob demanda (não em background massivo); cache de brief idêntico; cota por empresa pós-MVP. |
| R3 | **Inconsistência PostgreSQL ↔ Elastic** (`assets`) | Médio | Elastic é projeção; reindex idempotente; reconciliação periódica; PostgreSQL é fonte da verdade. |
| R4 | **Conteúdo gerado por IA impróprio/incorreto** publicado | Alto | State machine obriga aprovação humana (`INFOPRODUTOR`) antes de publicar; Studio nunca publica direto. |
| R5 | **Crescimento de versões imutáveis** infla armazenamento | Baixo | Conteúdo textual/jsonb é leve; binários por URL (não hospedados no MVP); arquivamento/retention por tenant. |
| R6 | **Vazamento cross-empresa** | Alto | `EmpresaContextHolder.require()` + `empresa_id` guard + testes de isolamento; schema-per-tenant. |
| R7 | **Acoplamento de consumidores** (COMM/JRNY/SALE) ao schema interno do asset | Médio | Expor contrato estável via Feign `AssetQueryClient` + evento; nunca expor entity. |

## 2. Gaps Conhecidos

- **Contrato TechLab AI `document_composition` não pinado:** `integrations/techlab-ai/openapi.json` e `techlab-ai-integration.md` ainda são placeholders (P3 bloqueado — aguarda 1º commit upstream). Os endpoints/DTOs exatos do Studio serão fixados quando o SHA for pinado.
- **Modelo de `conteudo` por tipo de asset:** o schema jsonb por `tipo_asset` (campos de uma LANDING_PAGE vs um EMAIL) será detalhado nas specs (`data-model.md` + SPECs).
- **Permissões `asst.*`:** o conjunto canônico (`asst.asset.criar/editar/submeter/aprovar/publicar/ler`) precisa ser confirmado no RBAC global (`shared/rbac/permissoes.md`).
- **Política autor≠aprovador:** se a segregação será obrigatória ou configurável por empresa (MVP: configurável, default permissivo).

## 3. Suposições a Validar

1. Binários (imagens/vídeos) são **referenciados por URL** no MVP — ASST não hospeda upload. (A validar com produto; object storage S3 é pós-MVP.)
2. Aprovação é **single-step** no MVP (um revisor com papel autorizado). Multi-nível é pós-MVP.
3. O índice Elastic `assets` é **dimension** (estado atual), reconstruível do PostgreSQL.
4. TechLab AI expõe `document_composition` adequado a compor conteúdo de marketing/educação em pt-BR.
5. Os tipos de asset do MVP (6 tipos) cobrem o uso inicial; novos tipos são extensão de catálogo.

## 4. Dependências Críticas

| Dependência | Estado | Bloqueia |
|---|---|---|
| **WRKS** (identidade/RBAC/AccessDecision) | vision+specs OK; scaffold pendente | Autorização `asst.*` em runtime (não bloqueia a arquitetura/scaffold de ASST). |
| **MIG** (schema `emp_<slug>`) | scaffold OK | Execução local (`bootRun`) — não bloqueia specs/scaffold. |
| **TechLab AI** (`document_composition`) | P3 bloqueado (placeholder) | Detalhamento fino do contrato do Asset Studio nas specs; geração de DTOs no scaffold. |
| **Elastic** índice `assets` | declarado em `project-context.json` | Asset Intelligence/busca; contrato em `elastic-data-contract.md`. |
| **REG/GWY** | scaffold OK | Discovery/edge em runtime. |

> **Nota para o autopilot:** a dependência de WRKS é de **runtime**, não de arquitetura. A
> pipeline vision→specs→backlog→scaffold de ASST pode prosseguir mesmo com WRKS ainda não
> scaffoldado. O contrato fino da TechLab AI (`document_composition`) permanece como gap até o
> SHA upstream ser pinado — as specs devem modelar o Asset Studio contra a interface esperada e
> marcar o ponto exato de acoplamento.

---

## Referências

- `01-architectural-vision.md` (§5 Out of Scope) · `04-backend-architecture-direction.md`
- `adr/ADR-003-messaging-strategy.md` · `adr/ADR-005-asset-versioning.md`
- `docs/architecture/integrations/techlab-ai-integration.md` (placeholder — P3)
