# 05 — Persistence Model — ASST (Asset Hub)

> Rascunho de persistência (refinado em `contracts/data-model.md` + migrations Flyway via MIG).

## 1. Schema Strategy

- **Schema-per-tenant:** ASST escreve **exclusivamente** no schema operacional `emp_<slug>` do
  tenant corrente (resolvido via `EmpresaContextHolder`). **Nunca** escreve em `journeyos_global`.
- `spring.jpa.hibernate.ddl-auto=validate` — DDL é responsabilidade de `journey-os-migrations`
  (MIG), naming `V<N>__asst_<descricao>.sql` no path `db/migration/empresa/`.
- `spring.jpa.open-in-view=false` (RULE-08).

## 2. Initial Entities (rascunho)

> Schema lógico (refinado nas specs). Identificadores canônicos em pt-BR.

### `asset`
| Coluna | Tipo | Notas |
|---|---|---|
| `id` | uuid PK | |
| `empresa_id` | uuid | tenant guard (redundante ao schema, usado em validação) |
| `tipo_asset` | varchar | `LANDING_PAGE`/`EMAIL`/`CRIATIVO`/`ROTEIRO`/`DOCUMENTO`/`SCRIPT_SDR` |
| `titulo` | varchar | |
| `descricao` | text | nullable |
| `estado_asset` | varchar | `RASCUNHO`/`EM_REVISAO`/`APROVADO`/`PUBLICADO`/`REJEITADO`/`ARQUIVADO` |
| `versao_vigente_id` | uuid FK→`versao_asset` | nullable (até a 1ª publicação) |
| `dono_id` | uuid | usuário criador |
| `criado_em` / `atualizado_em` | timestamptz | |

### `versao_asset` *(imutável)*
| Coluna | Tipo | Notas |
|---|---|---|
| `id` | uuid PK | |
| `asset_id` | uuid FK→`asset` | |
| `numero` | int | 1..N incremental por asset (unique `(asset_id, numero)`) |
| `conteudo` | jsonb | conteúdo estruturado/texto |
| `binarios` | jsonb | lista de `ReferenciaBinario` (url, mime, tamanho) |
| `origem` | varchar | `MANUAL`/`ASSET_STUDIO` |
| `brief_composicao` | jsonb | nullable — brief enviado à TechLab AI (proveniência) |
| `estado` | varchar | `RASCUNHO`/`PUBLICADA` |
| `criado_por` | uuid | |
| `criado_em` | timestamptz | |

### `aprovacao`
| Coluna | Tipo | Notas |
|---|---|---|
| `id` | uuid PK | |
| `asset_id` | uuid FK→`asset` | |
| `versao_id` | uuid FK→`versao_asset` | |
| `revisor_id` | uuid | |
| `decisao` | varchar | `APROVADO`/`REJEITADO` |
| `comentario` | text | nullable |
| `decidido_em` | timestamptz | |

### `tag_asset`
| Coluna | Tipo | Notas |
|---|---|---|
| `id` | uuid PK | |
| `asset_id` | uuid FK→`asset` | |
| `valor` | varchar | rótulo |
| `origem` | varchar | `MANUAL`/`IA` (Asset Intelligence) |

> Índice de busca **não** vive no PostgreSQL: a projeção de busca/Asset Intelligence é mantida
> no índice Elastic `assets` (dimension), reconstruível a partir do PostgreSQL.

## 3. Migration Strategy

- **Centralizada em MIG** (`journey-os-migrations`). ASST não roda Flyway próprio.
- Migrations do tenant em `db/migration/empresa/V<N>__asst_*.sql` (schema-aware).
- `be-migration-generator.py` gera o SQL a partir de `contracts/data-model.md` na fase de specs/scaffold.
- Local dev: `:journey-os-migrations:bootRun` **antes** de `:asst-service:bootRun`.

## 4. Data Lifecycle

- **Versões imutáveis:** nunca deletadas em operação normal (proveniência/auditoria); histórico completo de revisões preservado.
- **Arquivamento:** `estado_asset=ARQUIVADO` é exclusão lógica; mantém trilha.
- **LGPD:** assets podem conter dados pessoais (nomes em scripts, e-mails de exemplo) → política de retenção por tenant; expurgo sob solicitação opera por anonimização do conteúdo preservando a estrutura de versões.
- **Reindex:** índice Elastic `assets` é descartável/reconstruível a partir do PostgreSQL (fonte da verdade).

---

## Referências

- `03-initial-domain-framing.md` · `04-backend-architecture-direction.md`
- `adr/ADR-004-multitenant-strategy.md` · `adr/ADR-005-asset-versioning.md`
- `docs/architecture/shared/modelo-dados/empresa.md` · `docs/architecture/integrations/elastic-data-contract.md`
