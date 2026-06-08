# 05 — Persistence Model — INTL

> Rascunho inicial. SQL/DDL canônico é produzido por `/be-architect-specs` (`contracts/data-model.md`)
> e migrado via **journey-os-migrations (MIG)**. `ddl-auto=validate`.

## 1. Schema Strategy

Modelo **híbrido** (ADR-004):

- **PostgreSQL — `schema-per-tenant` (`emp_<slug>`):** conhecimento e conversas do copiloto.
  Tabelas no schema da `empresa`, **sem** coluna `empresa_id` (o schema isola). Resolvido por
  `EmpresaContextHolder`.
- **PostgreSQL — `journeyos_global` (opcional/governança):** `registro_indice` (metadado de
  governança da plataforma de dados — classe, dono, ILM). Avaliar no specs se vale tabela global
  ou se o registro vive só como configuração/Elastic.
- **Elasticsearch — índice compartilhado + discriminador `empresa`:** projeções `ai-copilot-events`
  (*fact*) e `knowledge-nodes` (*dimension*). Índice por-tenant é rejeitado (explosão de shards).
  Toda query filtra `empresa`.

## 2. Initial Entities (rascunho — refinar em specs)

Schema `emp_<slug>`:

| Tabela | Conteúdo | Notas |
|---|---|---|
| `base_conhecimento` | 1 linha por `empresa` (raiz) | metadados da base; criada no seed. |
| `no_conhecimento` | nó curado | `fonte_tipo`, `fonte_ref`, `titulo`, `conteudo`, `tags`, `embedding` (pgvector, opcional), `status`, `versao`, `atualizado_em`. Indexado em `knowledge-nodes`. |
| `fonte_conhecimento` | catálogo de fontes | `tipo` (MANUAL/ASSET/…), `referencia`. |
| `conversa_copiloto` | sessão de diálogo | `usuario_ref`, `titulo`, `estado`, `criada_em`. |
| `mensagem_copiloto` | turno | `conversa_id` (FK), `papel` (USUARIO/COPILOTO), `conteudo`, `status`, `modelo`, `custo_tokens`, `latencia_ms`, `criada_em`. |
| `citacao` | citação de uma mensagem | `mensagem_id` (FK), `documento_id`, `indice`, `trecho`, `score`. |
| `evento_indexado` | ledger append-only de projeções | `evento_id` (PK), `tipo`, `indice_alvo`, `status` (INDEXADO/DLQ), `indexado_em`. Idempotência/replay/auditoria. |

Schema `journeyos_global` (a confirmar em specs):

| Tabela | Conteúdo |
|---|---|
| `registro_indice` | `nome`, `classe` (dimension/fact), `dono` (módulo), `ilm`, `ativo`. |

## 3. Migration Strategy

- DDL centralizado em **journey-os-migrations** (`V<N>__intl_*.sql`), schema-aware
  (`emp_<slug>` para domínio; `journeyos_global` para `registro_indice`, se aplicável).
- pgVector já habilitado pela V1 global (extensão `vector`).
- `intl-service` usa `ddl-auto=validate`. Mapeamentos/ILM dos índices Elastic versionados como
  artefatos de plataforma (não DDL SQL).

## 4. Data Lifecycle (retention, archival)

- **Conversas:** retenção configurável por `empresa` (LGPD); anonimização/expurgo sob solicitação.
- **Nós de conhecimento:** versionados; `ARQUIVADO` em vez de hard-delete (auditável). Reembedding
  ao mudar o modelo de embedding.
- **`ai-copilot-events` (Elastic *fact*):** ILM rollover hot/warm com retenção configurável.
- **`knowledge-nodes` (Elastic *dimension*):** sem ILM; alerta se exceder volume esperado (D-272).
- **`evento_indexado` (ledger):** retenção alinhada à janela de replay/auditoria.
- **DLQ (`journey-os_dlq`):** retenção curta; inspeção/reprocessamento manual.
