# Data Model — intl-service (INTL)

> Schema-per-tenant: todas as tabelas vivem no schema `emp_<slug>` da `empresa` (ADR-004).
> **Sem** coluna `empresa_id` — o schema isola. DDL migrada via **journey-os-migrations (MIG)**;
> `intl-service` roda `ddl-auto=validate`. Blocos ```sql``` extraídos em ordem por
> `be-migration-generator.py` → `V1__create_initial_schema.sql`.
> EARS guide: `docs/architecture/backend/standards/ears-notation.md`.

## 1. Convenções

- **PK:** `uuid` via `gen_random_uuid()` (extensão `pgcrypto`, habilitada na V1 global do MIG).
- **Timestamps:** `timestamptz`, default `now()`; `criado_em`/`atualizado_em`.
- **Enums:** modelados como `varchar` + `CHECK` (não tipos enum nativos — facilita evolução).
- **Embeddings:** coluna `vector` (extensão `pgvector`, habilitada na V1 global). Dimensão
  `1536` é placeholder até o sync TechLab AI (P3) confirmar o modelo de embedding; nullable.
- **Soft-state:** nós usam `status=ARQUIVADO` em vez de hard-delete (auditável).
- **Encoding:** UTF-8; texto livre em `text`.

## 2. Schema-level mapping

| Tabela | Schema | Notas |
|---|---|---|
| `base_conhecimento` | empresa | raiz 1:1 com a `empresa` (criada no seed). |
| `fonte_conhecimento` | empresa | catálogo de fontes de conhecimento. |
| `no_conhecimento` | empresa | nó curado; indexado em Elastic `knowledge-nodes`. |
| `conversa_copiloto` | empresa | sessão de diálogo do copiloto. |
| `mensagem_copiloto` | empresa | turno da conversa. |
| `citacao` | empresa | evidência fundamentadora de uma mensagem. |
| `evento_indexado` | empresa | ledger append-only de projeções Elastic (idempotência/auditoria). |

> **Decisão (registro de índices):** a governança de índices/ILM da plataforma (ADR-003) é
> mantida como **configuração versionada + metadado no Elastic**, **não** como tabela PG no MVP.
> Reavaliar `registro_indice` global se a governança exigir CRUD transacional.

## 3. Entidades

### 3.1 `base_conhecimento` [empresa]

Raiz da Base de Conhecimento da `empresa` (1:1). Criada no seed por `empresa.provisionada`.
Agrupa os nós e guarda metadados da base (ex.: modelo de embedding corrente).

```sql
-- schema: empresa
CREATE TABLE base_conhecimento (
    id              uuid        NOT NULL DEFAULT gen_random_uuid(),
    embedding_modelo varchar(120) NULL,
    total_nos       integer     NOT NULL DEFAULT 0,
    criada_em       timestamptz NOT NULL DEFAULT now(),
    atualizada_em   timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (id)
);

COMMENT ON TABLE base_conhecimento IS 'Raiz da Base de Conhecimento da empresa (1:1); alimenta o RAG do Copilot.';
```

**Invariantes:**
- THE SYSTEM SHALL manter no máximo uma `base_conhecimento` por `empresa` (garantido pelo schema + seed idempotente).

### 3.2 `fonte_conhecimento` [empresa]

Origem de um nó de conhecimento. `tipo` controla a proveniência; `referencia` aponta para o
artefato origem (ex.: `asset_id:versao` quando `tipo=ASSET`).

```sql
-- schema: empresa
CREATE TABLE fonte_conhecimento (
    id          uuid        NOT NULL DEFAULT gen_random_uuid(),
    tipo        varchar(20) NOT NULL,
    referencia  varchar(300) NULL,
    criada_em   timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (id),
    CONSTRAINT ck_fonte_tipo CHECK (tipo IN ('MANUAL','ASSET','IMPORT'))
);

CREATE INDEX ix_fonte_tipo ON fonte_conhecimento (tipo);
COMMENT ON TABLE fonte_conhecimento IS 'Proveniência de um nó de conhecimento (MANUAL/ASSET/IMPORT).';
```

**Invariantes:**
- IF `tipo = 'ASSET'` AND `referencia IS NULL`, THEN THE SYSTEM SHALL reject a criação da fonte (referência do asset é obrigatória).

### 3.3 `no_conhecimento` [empresa]

Unidade curada de conhecimento. Canônico em PostgreSQL; projetado no índice Elastic
`knowledge-nodes` (dimension). `embedding` é opcional (pode viver só no Elastic).

```sql
-- schema: empresa
CREATE TABLE no_conhecimento (
    id              uuid         NOT NULL DEFAULT gen_random_uuid(),
    base_id         uuid         NOT NULL,
    fonte_id        uuid         NOT NULL,
    titulo          varchar(300) NOT NULL,
    conteudo        text         NOT NULL,
    tags            text[]       NOT NULL DEFAULT '{}',
    embedding       vector(1536) NULL,
    embedding_modelo varchar(120) NULL,
    status          varchar(20)  NOT NULL DEFAULT 'RASCUNHO',
    versao          integer      NOT NULL DEFAULT 1,
    criado_em       timestamptz  NOT NULL DEFAULT now(),
    atualizado_em   timestamptz  NOT NULL DEFAULT now(),
    PRIMARY KEY (id),
    CONSTRAINT ck_no_status CHECK (status IN ('RASCUNHO','INDEXADO','ARQUIVADO')),
    CONSTRAINT ck_no_versao CHECK (versao >= 1),
    FOREIGN KEY (base_id) REFERENCES base_conhecimento (id) ON DELETE CASCADE,
    FOREIGN KEY (fonte_id) REFERENCES fonte_conhecimento (id) ON DELETE RESTRICT
);

CREATE INDEX ix_no_status ON no_conhecimento (status);
CREATE INDEX ix_no_base ON no_conhecimento (base_id);
COMMENT ON TABLE no_conhecimento IS 'Nó curado de conhecimento; canônico em PG + indexado em Elastic knowledge-nodes.';
```

**Invariantes:**
- WHEN um nó transiciona para `INDEXADO`, THE SYSTEM SHALL ter projetado o documento correspondente no índice `knowledge-nodes` com o bloco de rastreabilidade.
- IF um nó é editado após `INDEXADO`, THEN THE SYSTEM SHALL incrementar `versao` e reindexar.

### 3.4 `conversa_copiloto` [empresa]

Sessão de diálogo do copiloto, vinculada ao usuário solicitante (`usuario_ref` = id do usuário em WRKS).

```sql
-- schema: empresa
CREATE TABLE conversa_copiloto (
    id            uuid         NOT NULL DEFAULT gen_random_uuid(),
    usuario_ref   uuid         NOT NULL,
    titulo        varchar(300) NULL,
    estado        varchar(20)  NOT NULL DEFAULT 'ABERTA',
    criada_em     timestamptz  NOT NULL DEFAULT now(),
    atualizada_em timestamptz  NOT NULL DEFAULT now(),
    PRIMARY KEY (id),
    CONSTRAINT ck_conversa_estado CHECK (estado IN ('ABERTA','PROCESSANDO','RESPONDIDA','DEGRADADA','ERRO'))
);

CREATE INDEX ix_conversa_usuario ON conversa_copiloto (usuario_ref);
COMMENT ON TABLE conversa_copiloto IS 'Sessão conversacional do AI Copilot (por usuário, dentro da empresa).';
```

### 3.5 `mensagem_copiloto` [empresa]

Turno da conversa. `papel=USUARIO` para a pergunta; `papel=COPILOTO` para a resposta gerada,
com `modelo`/`custo_tokens`/`latencia_ms` preenchidos (ou nulos em modo degradado).

```sql
-- schema: empresa
CREATE TABLE mensagem_copiloto (
    id            uuid         NOT NULL DEFAULT gen_random_uuid(),
    conversa_id   uuid         NOT NULL,
    ordem         integer      NOT NULL,
    papel         varchar(10)  NOT NULL,
    conteudo      text         NOT NULL,
    status        varchar(20)  NOT NULL DEFAULT 'PENDENTE',
    modelo        varchar(120) NULL,
    custo_tokens  integer      NULL,
    latencia_ms   integer      NULL,
    criada_em     timestamptz  NOT NULL DEFAULT now(),
    PRIMARY KEY (id),
    CONSTRAINT ck_msg_papel CHECK (papel IN ('USUARIO','COPILOTO')),
    CONSTRAINT ck_msg_status CHECK (status IN ('PENDENTE','RESPONDIDA','DEGRADADA','NAO_FUNDAMENTADA','ERRO')),
    CONSTRAINT ck_msg_custo CHECK (custo_tokens IS NULL OR custo_tokens >= 0),
    FOREIGN KEY (conversa_id) REFERENCES conversa_copiloto (id) ON DELETE CASCADE,
    UNIQUE (conversa_id, ordem)
);

CREATE INDEX ix_msg_conversa ON mensagem_copiloto (conversa_id);
COMMENT ON TABLE mensagem_copiloto IS 'Turno da conversa do Copilot (USUARIO=pergunta, COPILOTO=resposta).';
```

**Invariantes:**
- THE SYSTEM SHALL atribuir `ordem` sequencial e única por `conversa_id`.
- WHILE a resposta está em modo degradado (`status=DEGRADADA`), THE SYSTEM SHALL gravar `modelo IS NULL` e `custo_tokens = 0`.

### 3.6 `citacao` [empresa]

Evidência fundamentadora de uma mensagem do copiloto: aponta para um documento Elastic recuperado.

```sql
-- schema: empresa
CREATE TABLE citacao (
    id           uuid         NOT NULL DEFAULT gen_random_uuid(),
    mensagem_id  uuid         NOT NULL,
    documento_id varchar(200) NOT NULL,
    indice       varchar(120) NOT NULL,
    trecho       text         NULL,
    score        double precision NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (mensagem_id) REFERENCES mensagem_copiloto (id) ON DELETE CASCADE
);

CREATE INDEX ix_citacao_mensagem ON citacao (mensagem_id);
COMMENT ON TABLE citacao IS 'Citação verificável (documento Elastic) que fundamenta uma resposta do Copilot.';
```

**Invariantes:**
- WHEN uma mensagem `COPILOTO` é marcada `RESPONDIDA`, THE SYSTEM SHALL ter ≥ 1 `citacao` associada; caso contrário, a mensagem SHALL ser marcada `NAO_FUNDAMENTADA`.

### 3.7 `evento_indexado` [empresa]

Ledger append-only das projeções que INTL faz no Elastic (idempotência + auditoria + replay).
Chave natural `evento_id` = doc-id determinístico da projeção.

```sql
-- schema: empresa
CREATE TABLE evento_indexado (
    evento_id    varchar(200) NOT NULL,
    tipo         varchar(80)  NOT NULL,
    indice_alvo  varchar(120) NOT NULL,
    status       varchar(10)  NOT NULL,
    indexado_em  timestamptz  NOT NULL DEFAULT now(),
    PRIMARY KEY (evento_id),
    CONSTRAINT ck_evt_status CHECK (status IN ('INDEXADO','DLQ'))
);

CREATE INDEX ix_evt_indice ON evento_indexado (indice_alvo);
COMMENT ON TABLE evento_indexado IS 'Ledger append-only das projeções Elastic de INTL (idempotência/auditoria/replay).';
```

**Invariantes:**
- IF `evento_id` já existe com `status=INDEXADO`, THEN THE SYSTEM SHALL tratar a reprojeção como no-op (idempotência).

## 4. Relações (ASCII)

```
base_conhecimento 1───* no_conhecimento *───1 fonte_conhecimento
conversa_copiloto 1───* mensagem_copiloto 1───* citacao
evento_indexado (ledger isolado, chaveado por evento_id)
```

## 5. Migration plan

- `V1__intl_create_initial_schema.sql` — 7 tabelas acima (schema `empresa`). Faixa reservada
  `V0001..` para INTL no MIG (sufixo de módulo `intl`).
- Extensões `pgcrypto`/`vector` já criadas pela V1 global do MIG (não repetir).
