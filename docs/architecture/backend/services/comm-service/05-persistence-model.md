# 05 — Persistence Model — COMM (Communication Hub)

> Rascunho de persistência (refinado em `contracts/data-model.md` + migrations Flyway via MIG).

## 1. Schema Strategy

- **Schema-per-tenant:** COMM escreve **exclusivamente** no schema operacional `emp_<slug>` do
  tenant corrente (resolvido via `EmpresaContextHolder`). **Nunca** escreve em `journeyos_global`.
- `spring.jpa.hibernate.ddl-auto=validate` — DDL é responsabilidade de `journey-os-migrations`
  (MIG), naming `V<N>__comm_<descricao>.sql` no path `db/migration/empresa/`.
- `spring.jpa.open-in-view=false` (RULE-08).

## 2. Initial Entities (rascunho)

> Schema lógico (refinado nas specs). Identificadores canônicos em pt-BR.

### `template_mensagem`
| Coluna | Tipo | Notas |
|---|---|---|
| `id` | uuid PK | |
| `empresa_id` | uuid | tenant guard (redundante ao schema) |
| `nome` | varchar | |
| `canal` | varchar | `WHATSAPP`/`EMAIL`/`TELEGRAM`/`SMS` |
| `tipo_template` | varchar | `TRANSACIONAL`/`MARKETING`/`NOTIFICACAO` |
| `assunto` | varchar | nullable (e-mail) |
| `corpo` | text | texto/HTML com placeholders `{{variavel}}` |
| `variaveis` | jsonb | placeholders declarados |
| `asset_origem_id` | uuid | nullable — referência a asset publicado (ASST) |
| `estado` | varchar | `RASCUNHO`/`ATIVO`/`ARQUIVADO` |
| `versao` | int | incremental |
| `criado_em` / `atualizado_em` | timestamptz | |

### `mensagem`
| Coluna | Tipo | Notas |
|---|---|---|
| `id` | uuid PK | |
| `empresa_id` | uuid | tenant guard |
| `template_id` | uuid FK→`template_mensagem` | nullable (disparo ad-hoc) |
| `canal` | varchar | canal efetivo do disparo |
| `lead_id` | uuid | destinatário (referência ao lead) |
| `destinatario` | jsonb | `ReferenciaDestinatario` (nome, endereço, preferência) |
| `conteudo_renderizado` | text/jsonb | **snapshot imutável** do que foi enviado |
| `estado_entrega` | varchar | `PENDENTE`/`ENFILEIRADA`/`ENVIADA`/`ENTREGUE`/`LIDA`/`FALHADA` |
| `provedor` | varchar | provedor usado (`META_WABA`/`SES`/...) |
| `provedor_message_id` | varchar | nullable — id externo do provedor |
| `tentativas` | int | contador de tentativas de envio |
| `motivo_falha` | text | nullable |
| `chave_idempotencia` | varchar | **unique** `(empresa_id, chave_idempotencia)` |
| `agendado_para` | timestamptz | nullable (envio agendado) |
| `criado_em` / `atualizado_em` | timestamptz | |

### `evento_entrega` *(append-only)*
| Coluna | Tipo | Notas |
|---|---|---|
| `id` | uuid PK | |
| `mensagem_id` | uuid FK→`mensagem` | |
| `tipo` | varchar | `ENFILEIRADA`/`ENVIADA`/`ENTREGUE`/`LIDA`/`FALHADA`/`REJEITADA` |
| `provedor_payload` | jsonb | callback bruto do provedor (nullable p/ transições internas) |
| `ocorrido_em` | timestamptz | |

### `regra_roteamento`
| Coluna | Tipo | Notas |
|---|---|---|
| `id` | uuid PK | |
| `empresa_id` | uuid | tenant guard |
| `nome` | varchar | |
| `prioridade` | int | menor = avaliada primeiro |
| `condicoes` | jsonb | segmento/estágio/preferência/janela |
| `canal_preferido` | varchar | |
| `canais_fallback` | jsonb | lista ordenada de canais de fallback |
| `template_id` | uuid FK→`template_mensagem` | nullable |
| `ativa` | boolean | |
| `criado_em` | timestamptz | |

### `config_canal`
| Coluna | Tipo | Notas |
|---|---|---|
| `id` | uuid PK | |
| `empresa_id` | uuid | tenant guard |
| `canal` | varchar | unique `(empresa_id, canal, provedor)` |
| `provedor` | varchar | `META_WABA`/`SES`/`SENDGRID`/`TELEGRAM_BOT`/`TWILIO`/`SNS` |
| `identidade_remetente` | varchar | número/e-mail/bot de origem |
| `credencial_ref` | varchar | **referência** a secret (`${VAR}` / secret manager) — nunca o segredo |
| `janela_envio` | jsonb | nullable — quiet hours / rate |
| `ativo` | boolean | |

> Índice de analytics **não** vive no PostgreSQL: a projeção do ciclo de vida é mantida no índice
> Elastic `communication-events` (fact, append-only), reconstruível a partir de `evento_entrega`.
> Tabelas compartilhadas `processed_events` (idempotência de consumo) e `outbox_event`
> (publicação transacional / disparo desacoplado) seguem o padrão da plataforma.

## 3. Migration Strategy

- **Centralizada em MIG** (`journey-os-migrations`). COMM não roda Flyway próprio.
- Migrations do tenant em `db/migration/empresa/V<N>__comm_*.sql` (schema-aware).
- `be-migration-generator.py` gera o SQL a partir de `contracts/data-model.md` na fase de specs/scaffold.
- Local dev: `:journey-os-migrations:bootRun` **antes** de `:comm-service:bootRun`.

## 4. Data Lifecycle

- **Mensagens enviadas:** preservadas como trilha (proveniência do que foi enviado/entregue); `conteudo_renderizado` imutável.
- **EventoEntrega:** append-only; nunca atualizado/deletado em operação normal.
- **Arquivamento:** templates passam a `ARQUIVADO` (exclusão lógica); mensagens antigas sujeitas a retenção/expurgo por tenant.
- **LGPD:** mensagens contêm dados pessoais (telefone, e-mail, nome) → política de retenção por tenant; expurgo por **anonimização** do `destinatario`/`conteudo_renderizado` preservando a estrutura de eventos para auditoria. `config_canal.credencial_ref` nunca expõe segredo.
- **Reindex:** índice Elastic `communication-events` é descartável/reconstruível a partir de `evento_entrega` (PostgreSQL é a fonte da verdade).

---

## Referências

- `03-initial-domain-framing.md` · `04-backend-architecture-direction.md`
- `adr/ADR-004-multitenant-strategy.md` · `adr/ADR-005-channel-adapter-pattern.md`
- `docs/architecture/shared/modelo-dados/empresa.md` · `docs/architecture/integrations/elastic-data-contract.md`
