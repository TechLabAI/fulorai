# 05 — Persistence Model — JRNY (Journey & Routing)

> Rascunho de persistência (refinado em `contracts/data-model.md` + migrations Flyway via MIG).

## 1. Schema Strategy

- **Schema-per-tenant:** JRNY escreve **exclusivamente** no schema operacional `emp_<slug>` do
  tenant corrente (resolvido via `EmpresaContextHolder`). **Nunca** escreve em `journeyos_global`.
- `spring.jpa.hibernate.ddl-auto=validate` — DDL é responsabilidade de `journey-os-migrations`
  (MIG), naming `V<N>__jrny_<descricao>.sql` no path `db/migration/empresa/`.
- `spring.jpa.open-in-view=false` (RULE-08).

## 2. Initial Entities (rascunho)

> Schema lógico (refinado nas specs). Identificadores canônicos em pt-BR.

### `jornada`
| Coluna | Tipo | Notas |
|---|---|---|
| `id` | uuid PK | |
| `empresa_id` | uuid | tenant guard (redundante ao schema, usado em validação) |
| `nome` | varchar | |
| `descricao` | text | nullable |
| `estado_jornada` | varchar | `RASCUNHO`/`PUBLICADA`/`ARQUIVADA` |
| `versao` | int | incremental por jornada |
| `criado_por` | uuid | usuário |
| `criado_em` / `atualizado_em` | timestamptz | |

### `estagio`
| Coluna | Tipo | Notas |
|---|---|---|
| `id` | uuid PK | |
| `jornada_id` | uuid FK→`jornada` | |
| `ordem` | int | 1..N (unique `(jornada_id, ordem)`) |
| `tipo_estagio` | varchar | `CAPTURA`/`NUTRICAO`/`QUALIFICACAO`/`OFERTA`/`FECHAMENTO`/`POS_VENDA` |
| `nome` | varchar | |
| `asset_ref_id` | uuid | nullable — asset publicado de ASST |
| `terminal` | boolean | marca estágio final |
| `config` | jsonb | parâmetros do estágio (ações sinalizadas, etc.) |

### `regra_roteamento`
| Coluna | Tipo | Notas |
|---|---|---|
| `id` | uuid PK | |
| `jornada_id` | uuid FK→`jornada` | |
| `estagio_origem_id` | uuid FK→`estagio` | nullable (null = regra de entrada) |
| `estagio_destino_id` | uuid FK→`estagio` | |
| `condicao` | jsonb | predicado sobre score/segmento/atributo do lead |
| `prioridade` | int | desempate (menor = avaliada antes) |
| `versao` | int | versão da regra |
| `ativa` | boolean | |

### `inscricao_jornada`
| Coluna | Tipo | Notas |
|---|---|---|
| `id` | uuid PK | |
| `empresa_id` | uuid | tenant guard |
| `lead_id` | uuid | lead de LEAD (referência lógica cross-módulo) |
| `jornada_id` | uuid FK→`jornada` | |
| `jornada_versao` | int | versão da jornada na matrícula |
| `estagio_corrente_id` | uuid FK→`estagio` | |
| `estado` | varchar | `ATIVA`/`CONCLUIDA`/`ENCERRADA` |
| `entrou_em` / `atualizado_em` | timestamptz | unique parcial `(lead_id, jornada_id) where estado='ATIVA'` |

### `decisao_roteamento` *(imutável — decision log)*
| Coluna | Tipo | Notas |
|---|---|---|
| `id` | uuid PK | |
| `empresa_id` | uuid | tenant guard |
| `lead_id` | uuid | |
| `inscricao_id` | uuid FK→`inscricao_jornada` | nullable |
| `gatilho` | varchar | evento de origem (`lead.qualificado`, etc.) |
| `snapshot_entrada` | jsonb | score/segmento/atributos no instante da decisão |
| `regra_id` | uuid FK→`regra_roteamento` | nullable |
| `assist_ia` | varchar | `USADO`/`IGNORADO`/`INDISPONIVEL` |
| `resultado` | varchar | `ROTEADO`/`SEM_MUDANCA`/`NAO_ROTEADO` |
| `estagio_alvo_id` | uuid FK→`estagio` | nullable |
| `motivo` | text | explicação legível |
| `decidido_em` | timestamptz | |

> A telemetria de jornada (`transicao_estagio`) e o decision log são **projetados** nos índices
> Elastic `journey-events` e `routing-decisions` (fact). A fonte da verdade do estado de jornada
> é o PostgreSQL; os índices são reconstruíveis a partir dele.

## 3. Migration Strategy

- **Centralizada em MIG** (`journey-os-migrations`). JRNY não roda Flyway próprio.
- Migrations do tenant em `db/migration/empresa/V<N>__jrny_*.sql` (schema-aware).
- `be-migration-generator.py` gera o SQL a partir de `contracts/data-model.md` na fase de specs/scaffold.
- Local dev: `:journey-os-migrations:bootRun` **antes** de `:jrny-service:bootRun`.

## 4. Data Lifecycle

- **Decisões imutáveis:** `decisao_roteamento` nunca é deletada em operação normal (auditoria do "por quê"); histórico completo preservado.
- **Inscrições concluídas/encerradas:** mantidas para histórico do lead; arquivamento por tenant pós-MVP.
- **Jornadas:** `estado_jornada=ARQUIVADA` é exclusão lógica; versões anteriores preservadas (inscrições antigas referenciam a versão de entrada).
- **LGPD:** `snapshot_entrada` pode conter atributos pessoais do lead → política de retenção por tenant; expurgo sob solicitação opera por anonimização preservando a estrutura da decisão.
- **Reindex:** índices Elastic `journey-events`/`routing-decisions` são descartáveis/reconstruíveis a partir do PostgreSQL (fonte da verdade).

---

## Referências

- `03-initial-domain-framing.md` · `04-backend-architecture-direction.md`
- `adr/ADR-004-multitenant-strategy.md` · `adr/ADR-005-routing-engine-model.md`
- `docs/architecture/shared/modelo-dados/empresa.md` · `docs/architecture/integrations/elastic-data-contract.md`
