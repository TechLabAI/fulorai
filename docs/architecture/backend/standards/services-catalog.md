# Services Catalog (Journey OS Backend)

> Catálogo de referência rápida de todos os microserviços do backend:
> pacote Java canônico, project key Gradle, responsabilidade em uma linha, ports e eventos chave.

Use este arquivo quando:
- Iniciar serviço novo -- encontrar pacote canônico e project key.
- Escrever `applyTo` em CI ou referência cruzada.
- Entender qual serviço é dono de qual fronteira de domínio.

> **Atualização:** este catálogo é atualizado por `/be-architect-vision <MODULE>` quando
> um novo módulo é registrado. Edite manualmente apenas se você adicionar capacidades
> a um serviço existente (eventos, Feign clients).

---

## 1. Service Map

| Componente | Gradle project key | Pacote canônico | Módulo |
|---|---|---|---|
| `wrks-service` | `:services:wrks-service` | `com.journeyos.wrks` | WRKS |
| `lead-service` | `:services:lead-service` | `com.journeyos.lead` | LEAD |
| `jrny-service` | `:services:jrny-service` | `com.journeyos.jrny` | JRNY |
| `asst-service` | `:services:asst-service` | `com.journeyos.asst` | ASST |
| `comm-service` | `:services:comm-service` | `com.journeyos.comm` | COMM |
| `sale-service` | `:services:sale-service` | `com.journeyos.sale` | SALE |
| `intl-service` | `:services:intl-service` | `com.journeyos.intl` | INTL |
| `` | `:services:` | `com.journeyos.gwy` | GWY |
| `` | `:services:` | `com.journeyos.reg` | REG |
| `` | `:services:` | `com.journeyos.mig` | MIG |

---

## 2. Resumo de responsabilidades

### `wrks-service` -- `com.journeyos.wrks` (WRKS)
- Multi-tenancy, business units, teams, users, RBAC, administration
- **Owns:** IAM em `journeyos_global` (usuario, papel, permissao, papel_permissao, usuario_empresa, empresa, business_unit, team, modelo_acesso_versao, evento_auditoria). Emissor do JWT (RS256) + AccessDecision. Orquestra provisionamento de tenant via MIG.
- **API:** `/api/v1/iam/**` (login, refresh, logout, restore, trocar-empresa, access/evaluate, empresa, usuario, papel)
- **Produz:** `journey-os.modelo.acesso.alterado`, `journey-os.usuario.criado`, `journey-os.empresa.provisionada`, `journey-os.sessao.estabelecida`
- **Consome:** todos os `journey-os.*` (auditoria → `evento_auditoria` + índice Elastic `audit-events`)
- **Provê (Feign/HTTP):** AccessDecision + JWKS para GWY e todos os serviços

### `lead-service` -- `com.journeyos.lead` (LEAD)
- Leads, perfil, segmentação, Maturity Score (6D), surveys, qualification rules
- **Owns:** agregado `lead` + satélites (`perfil_lead`, `atributo_perfil`, `survey`, `pergunta`, `resposta_survey`, `regra_qualificacao`, `condicao_regra`, `maturity_score`, `score_dimensao`, `segmento`, `lead_segmento`) no schema `emp_<slug>`. Dono do cálculo do Maturity Score (6D), regras de qualificação versionadas e segmentação dinâmica.
- **API:** `/api/v1/leads/**`, `/api/v1/surveys/**`, `/api/v1/qualification/**`, `/api/v1/segments/**`
- **Produz:** `journey-os.lead.capturado`, `journey-os.lead.qualificado` (âncora), `journey-os.lead.score.atualizado`, `journey-os.lead.segmento.alterado`
- **Consome:** `journey-os.empresa.provisionada` (seed regras/segmentos por tenant), `journey-os.modelo.acesso.alterado` (invalida cache AccessDecision)
- **Depende (Feign/HTTP):** WRKS `AccessEvaluateClient` (autorização `lead.*`); TechLab AI `qualification` (HTTP, assist opcional ao score, com fallback)

### `jrny-service` -- `com.journeyos.jrny` (JRNY)
- Jornadas, estágios, Journey Builder, Routing Engine, decision log
- **Owns:** definição de jornada e roteamento no schema `emp_<slug>` (`jornada`, `estagio`, `regra_roteamento` versionada, `inscricao_jornada`, `decisao_roteamento` imutável). Routing Engine determinístico (regras + assist de IA opcional). Projeções fact nos índices Elastic `journey-events` e `routing-decisions`.
- **API:** `/api/v1/journeys/**` (CRUD jornada/estágio, publish/archive), `/api/v1/routing/**` (regras, consulta de decisão/estado do lead)
- **Produz:** `journey-os.jornada.publicada`, `journey-os.lead.roteado` (âncora), `journey-os.estagio.transicionado`, `journey-os.jornada.concluida`
- **Consome:** `journey-os.lead.qualificado` / `journey-os.lead.score.atualizado` / `journey-os.lead.segmento.alterado` (LEAD → gatilho de roteamento), `journey-os.asset.versao.publicada` (ASST → atualiza referência de conteúdo do estágio), `journey-os.modelo.acesso.alterado` (WRKS → invalida cache AccessDecision), `journey-os.empresa.provisionada` (WRKS → seed de jornadas default)
- **Depende (Feign/HTTP):** WRKS `AccessEvaluateClient` (autorização `jrny.*`); ASST `AssetQueryClient` (conteúdo publicado dos estágios); TechLab AI `orchestration` (HTTP — assist de roteamento, opcional com fallback determinístico); Elasticsearch (`journey-events`, `routing-decisions`)
- **Provê (Feign/HTTP):** `JourneyQueryClient` (leitura do estado de jornada do lead) para COMM/SALE

### `asst-service` -- `com.journeyos.asst` (ASST)
- Assets, Asset Studio, versionamento, approval workflow, Asset Intelligence
- **Owns:** ciclo de vida do asset no schema `emp_<slug>` (`asset`, `versao_asset` imutável, `aprovacao`, `tag_asset`). Máquina de estados de aprovação/publicação. Projeção de busca/Asset Intelligence no índice Elastic `assets` (dimension).
- **API:** `/api/v1/assets/**` (CRUD, submit, approve, publish, busca) + `/api/v1/assets/{id}/studio/compose` (Asset Studio)
- **Produz:** `journey-os.asset.criado`, `journey-os.asset.aprovado`, `journey-os.asset.rejeitado`, `journey-os.asset.versao.publicada` (âncora)
- **Consome:** `journey-os.modelo.acesso.alterado` (WRKS → invalida cache AccessDecision), `journey-os.empresa.provisionada` (WRKS → seed de catálogo)
- **Depende (Feign/HTTP):** WRKS `AccessEvaluateClient` (autorização `asst.*`); TechLab AI `document_composition` (HTTP — Asset Studio, com fallback); Elasticsearch (`assets`)
- **Provê (Feign/HTTP):** `AssetQueryClient` (leitura de assets publicados) para COMM/JRNY/SALE

### `comm-service` -- `com.journeyos.comm` (COMM)
- WhatsApp/Email/Telegram/SMS via integração, templates, message routing
- **Owns:** ciclo de vida da comunicação no schema `emp_<slug>` (`template_mensagem`, `mensagem`, `evento_entrega` append-only, `regra_roteamento`, `config_canal`). Máquina de estados de entrega (`PENDENTE→ENFILEIRADA→ENVIADA→ENTREGUE→LIDA`/`FALHADA`). Abstração de provedor via adapters de canal sob `CanalEnvioPort` (provedor-agnóstico). Projeção do ciclo de vida no índice Elastic `communication-events` (fact).
- **API:** `/api/v1/templates/**` (CRUD + `/studio/compose`), `/api/v1/messages/**` (disparo, status), `/api/v1/routing-rules/**`, `/api/v1/channels/**` (config), `/api/v1/webhooks/{canal}` (callbacks de provedor)
- **Produz:** `journey-os.mensagem.enfileirada`, `journey-os.mensagem.enviada` (âncora), `journey-os.mensagem.entregue`, `journey-os.mensagem.falhada`
- **Consome:** `journey-os.modelo.acesso.alterado` (WRKS → invalida cache AccessDecision), `journey-os.empresa.provisionada` (WRKS → seed de canais/templates), `journey-os.asset.versao.publicada` (ASST → sinaliza template vinculado), `journey-os.lead.segmento.alterado` (LEAD → reavalia roteamento); gatilhos de jornada/oferta: `journey-os.lead.roteado`, `journey-os.estagio.transicionado` (JRNY), `journey-os.oportunidade.estagio.alterado` (SALE)
- **Depende (Feign/HTTP):** WRKS `AccessEvaluateClient` (autorização `comm.*`); ASST `AssetQueryClient` (assets publicados como fonte de template); TechLab AI `document_composition` (HTTP — Template Studio, com fallback); provedores de canal (Meta WABA/SES/SendGrid/Telegram/Twilio/SNS via adapters); Elasticsearch (`communication-events`)

### `sale-service` -- `com.journeyos.sale` (SALE)
- CRM (pipeline/SDR/closer), ofertas, compras, attribution, LTV
- **Owns:** agregados `oportunidade` (+ `historico_estagio`), `oferta` (catálogo versionado), `compra` (+ `item_compra`, idempotente por `id_externo`+`origem`), `modelo_atribuicao` (versionado), `atribuicao`, `campanha` e `ltv` (materializado) no schema `emp_<slug>`. Dono do pipeline de vendas, do reconhecimento de receita, da atribuição de receita determinística (last/first/linear-touch) e do cálculo de LTV. Projeções fact nos índices Elastic `revenue-events` e `campaign-events`. **Não** processa pagamento (gateway externo).
- **API:** `/api/v1/oportunidades/**`, `/api/v1/ofertas/**`, `/api/v1/compras/**` (ingestão idempotente), `/api/v1/atribuicao/**`, `/api/v1/ltv/**`
- **Produz:** `journey-os.oportunidade.criada`, `journey-os.oportunidade.estagio.alterado`, `journey-os.oportunidade.ganha`, `journey-os.oportunidade.perdida`, `journey-os.compra.confirmada` (âncora), `journey-os.receita.atribuida`, `journey-os.ltv.atualizado`
- **Consome:** `journey-os.lead.qualificado` / `journey-os.lead.score.atualizado` (LEAD → cria/prioriza oportunidade), `journey-os.empresa.provisionada` (WRKS → seed de pipeline/ofertas/modelo de atribuição default), `journey-os.modelo.acesso.alterado` (WRKS → invalida cache AccessDecision). *(Pós-MVP: `journey-os.lead.roteado` / `journey-os.estagio.transicionado` / `journey-os.jornada.concluida` de JRNY como touchpoints/responsável.)*
- **Depende (Feign/HTTP):** WRKS `AccessEvaluateClient` (autorização `sale.*`); Elasticsearch (`revenue-events`, `campaign-events`). *(Pós-MVP: JRNY `JourneyQueryClient`; ASST `AssetQueryClient` p/ copy de oferta; TechLab AI `analytics`.)* **Sem TechLab AI no MVP.**

### `intl-service` -- `com.journeyos.intl` (INTL)
- AI Copilot + Knowledge, Event Platform, Integrations, Observabilidade/indexação Elastic
- **Owns:** domínio Copilot/Conhecimento no schema `emp_<slug>` (`base_conhecimento`, `no_conhecimento`, `fonte_conhecimento`, `conversa_copiloto`, `mensagem_copiloto`, `citacao`, `evento_indexado` ledger) + **governança da plataforma de dados Elastic** (contrato de rastreabilidade de 8 campos — D-269, DLQ `journey-os_dlq`, registro de índices/ILM, classes dimension/fact — D-272). Projeta os índices **próprios**: `ai-copilot-events` (fact) e `knowledge-nodes` (dimension). Declara (sem ingerir no MVP) `app-logs`/`traces`/`metrics`/`integration-logs`. **Não** reindexа os *facts* de outros módulos (ADR-003).
- **API:** `/api/v1/copilot/**` (conversa/perguntar — RAG fundamentado, read-only), `/api/v1/knowledge/**` (CRUD/curadoria de nós), `/api/v1/analytics/**` (leitura analítica cross-index, read-only)
- **Produz:** `journey-os.copilot.resposta.gerada` (âncora → `ai-copilot-events`)
- **Consome:** `journey-os.asset.versao.publicada` (ASST → ingere nó de conhecimento), `journey-os.empresa.provisionada` (WRKS → seed base/registro de índices por tenant), `journey-os.modelo.acesso.alterado` (WRKS → invalida cache AccessDecision)
- **Depende (Feign/HTTP):** WRKS `AccessEvaluateClient` (autorização `intl.*`); TechLab AI `knowledge` + `orchestration` (HTTP — RAG + composição, com circuit breaker e fallback recuperação-apenas); Elasticsearch via `elastic-client-lib` (`SearchPort`/`IndexPort`); ASST `AssetQueryClient` (conteúdo de asset publicado como fonte de conhecimento — opcional)
- **Provê (Feign/HTTP):** *(pós-MVP)* `AnalyticsQueryClient`/`KnowledgeQueryClient` para leitura por outros serviços

### `` -- `com.journeyos.gwy` (GWY)
- Spring Cloud Gateway — routing, auth, rate-limit

### `` -- `com.journeyos.reg` (REG)
- Eureka service discovery

### `` -- `com.journeyos.mig` (MIG)
- Centralized Flyway DB migrations

---

## 3. Estrutura interna canônica

Todos os serviços (exceto `journey-os-migrations`) usam o layout hexagonal:

```
com.journeyos.<module>/
├── api/
│   ├── controller/          # @RestController
│   ├── dto/                 # Java records (Request/Response)
│   └── exception/           # @RestControllerAdvice (ProblemDetail)
├── application/
│   ├── service/             # @Service, @Transactional, EmpresaContextHolder.require()
│   └── port/
│       ├── in/              # Use-case interfaces
│       └── out/             # Repository + external service interfaces
├── domain/
│   ├── model/               # Pure POJO -- zero Spring, zero JPA
│   └── service/             # Domain business rules
└── infrastructure/
    ├── clients/             # @FeignClient
    ├── config/              # @Configuration, DomainServiceConfig
    ├── messaging/
    │   ├── producer/        # JmsTemplate publishers
    │   └── consumer/        # @JmsListener consumers
    ├── persistence/
    │   ├── entity/          # @Entity JPA
    │   ├── repository/      # Spring Data JPA @Repository
    │   └── adapter/         # Port.out implementations
    └── security/            # Filters, EmpresaContextHolder, CorrelationIdInterceptor
```

Detalhes em `hexagonal-patterns.md`.

---

## 4. Referência base ArchUnit

Cada `ArchitectureTest.java` usa seu pacote canônico:

```java

// :
@AnalyzeClasses(packages = "com.journeyos.wrks")

// :
@AnalyzeClasses(packages = "com.journeyos.lead")

// :
@AnalyzeClasses(packages = "com.journeyos.jrny")

// ... etc para os outros serviços
```

---

## 5. Comandos Gradle por serviço

```bash
# Substitua <project-key> pela chave do Gradle (Seção 1)
./gradlew :services:<project-key>:architectureCheck    # ArchUnit -- BLOQUEANTE
./gradlew :services:<project-key>:test                 # unit tests (@Tag("unit"))
./gradlew :services:<project-key>:integrationTest      # integration + BDD (Testcontainers)
./gradlew :services:<project-key>:build                # full build + all checks

# Todos os serviços
./gradlew build                               # full monorepo build
./gradlew check                               # lint + test + archUnit
```

---

## 6. Event Catalog (cross-reference)

> Catálogo completo de eventos é mantido em `docs/architecture/shared/contratos/event-catalog.md`.
> A tabela abaixo é um resumo populado por `/be-architect-vision <MODULE>` conforme cada
> módulo declara seus eventos.

| Evento | Producer | Key consumers | Queue name |
|---|---|---|---|

| `journey-os.modelo.acesso.alterado` | WRKS | todos os serviços (invalida cache AccessDecision) | `journey-os.modelo.acesso.alterado` |
| `journey-os.usuario.criado` | WRKS | (auditoria/notificação) | `journey-os.usuario.criado` |
| `journey-os.empresa.provisionada` | WRKS | serviços que dependem de seed por tenant | `journey-os.empresa.provisionada` |
| `journey-os.sessao.estabelecida` | WRKS | (auditoria) | `journey-os.sessao.estabelecida` |
| `journey-os.lead.capturado` | LEAD | INTL (analytics), WRKS (auditoria) | `journey-os.lead.capturado` |
| `journey-os.lead.qualificado` | LEAD | JRNY (roteamento), SALE (priorização), COMM (nutrição) | `journey-os.lead.qualificado` |
| `journey-os.lead.score.atualizado` | LEAD | JRNY, SALE, INTL | `journey-os.lead.score.atualizado` |
| `journey-os.lead.segmento.alterado` | LEAD | COMM, JRNY | `journey-os.lead.segmento.alterado` |
| `journey-os.asset.criado` | ASST | INTL (analytics), WRKS (auditoria) | `journey-os.asset.criado` |
| `journey-os.asset.aprovado` | ASST | (auditoria/notificação) | `journey-os.asset.aprovado` |
| `journey-os.asset.rejeitado` | ASST | (auditoria/notificação ao autor) | `journey-os.asset.rejeitado` |
| `journey-os.asset.versao.publicada` | ASST | COMM (templates), JRNY (conteúdo de estágio), SALE (copy de oferta), INTL | `journey-os.asset.versao.publicada` |
| `journey-os.jornada.publicada` | JRNY | (auditoria/notificação), INTL (analytics) | `journey-os.jornada.publicada` |
| `journey-os.lead.roteado` | JRNY | COMM (ação no estágio), SALE (oportunidade), INTL (analytics) | `journey-os.lead.roteado` |
| `journey-os.estagio.transicionado` | JRNY | COMM, SALE, INTL (journey-events) | `journey-os.estagio.transicionado` |
| `journey-os.jornada.concluida` | JRNY | SALE, INTL (analytics) | `journey-os.jornada.concluida` |
| `journey-os.oportunidade.criada` | SALE | INTL (analytics), JRNY | `journey-os.oportunidade.criada` |
| `journey-os.oportunidade.estagio.alterado` | SALE | INTL (funil), COMM (nutrição por estágio) | `journey-os.oportunidade.estagio.alterado` |
| `journey-os.oportunidade.ganha` | SALE | INTL, COMM, WRKS (auditoria) | `journey-os.oportunidade.ganha` |
| `journey-os.oportunidade.perdida` | SALE | INTL (analytics de perda) | `journey-os.oportunidade.perdida` |
| `journey-os.compra.confirmada` | SALE | INTL (`revenue-events`), WRKS (auditoria), COMM (pós-venda) | `journey-os.compra.confirmada` |
| `journey-os.receita.atribuida` | SALE | INTL (ROI por origem/campanha) | `journey-os.receita.atribuida` |
| `journey-os.ltv.atualizado` | SALE | INTL, LEAD (sinal de valor — pós-MVP) | `journey-os.ltv.atualizado` |
| `journey-os.mensagem.enfileirada` | COMM | INTL (`communication-events`) | `journey-os.mensagem.enfileirada` |
| `journey-os.mensagem.enviada` | COMM | JRNY (avanço de jornada), SALE (toque), INTL (`communication-events`) | `journey-os.mensagem.enviada` |
| `journey-os.mensagem.entregue` | COMM | SALE (atribuição), INTL (`communication-events`) | `journey-os.mensagem.entregue` |
| `journey-os.mensagem.falhada` | COMM | INTL (analytics de falha), WRKS (auditoria) | `journey-os.mensagem.falhada` |
| `journey-os.copilot.resposta.gerada` | INTL | INTL (`ai-copilot-events`), WRKS (auditoria) | `journey-os.copilot.resposta.gerada` |
| `journey-os.*` (todos) | qualquer serviço | **WRKS** (auditoria consolidada) | — |

---

## 7. Feign Client Registry

> Lista populada por `/be-architect-vision <MODULE>` conforme integrações inter-service são identificadas.

| Feign interface | Consumer service | Provider service | `@FeignClient(name = ...)` |
|---|---|---|---|
| `AccessEvaluateClient` | GWY + todos os serviços | WRKS | `@FeignClient(name = "wrks-service")` |
| `TechLabAiClient` (`qualification`) | LEAD | TechLab AI (HTTP, externo) | cliente HTTP em `infrastructure.clients` (não-Feign; DTOs gerados de `openapi.json`) |
| `AssetQueryClient` | COMM, JRNY, SALE | ASST | `@FeignClient(name = "asst-service")` (leitura de assets publicados) |
| `TechLabAiClient` (`document_composition`) | COMM | TechLab AI (HTTP, externo) | cliente HTTP em `infrastructure.clients` (não-Feign; DTOs gerados de `openapi.json`) — Template Studio |
| `CanalEnvioPort` (adapters de canal) | COMM | Meta WABA / SES / SendGrid / Telegram Bot / Twilio / SNS (HTTP, externos) | adapters em `infrastructure.channels` (não-Feign; um por canal/provedor — ver ADR-005) |
| `TechLabAiClient` (`document_composition`) | ASST | TechLab AI (HTTP, externo) | cliente HTTP em `infrastructure.clients` (não-Feign; DTOs gerados de `openapi.json`) — Asset Studio |
| `AssetQueryClient` (consumo) | JRNY | ASST | `@FeignClient(name = "asst-service")` (conteúdo publicado dos estágios) |
| `JourneyQueryClient` | COMM, SALE | JRNY | `@FeignClient(name = "jrny-service")` (leitura do estado de jornada do lead) |
| `TechLabAiClient` (`orchestration`) | JRNY | TechLab AI (HTTP, externo) | cliente HTTP em `infrastructure.clients` (não-Feign; DTOs gerados de `openapi.json`) — assist de roteamento, opcional |
| `TechLabAiClient` (`knowledge` + `orchestration`) | INTL | TechLab AI (HTTP, externo) | cliente HTTP em `infrastructure.clients` (não-Feign; DTOs gerados de `openapi.json`) — AI Copilot RAG, com circuit breaker e fallback recuperação-apenas |
| `AssetQueryClient` (consumo) | INTL | ASST | `@FeignClient(name = "asst-service")` (conteúdo de asset publicado como fonte de conhecimento — opcional) |
| `SearchPort` / `IndexPort` (Elastic) | INTL | Elasticsearch (via `elastic-client-lib`) | portas em `infrastructure.elastic` (não-Feign) — recuperação RAG + analítica cross-index + projeções `ai-copilot-events`/`knowledge-nodes` |

A lista será expandida conforme integrações forem identificadas em SPECs por serviço.

---

## Referências

- `docs/architecture/backend/standards/hexagonal-patterns.md`
- `docs/architecture/backend/standards/java-conventions.md`
- `docs/architecture/backend/standards/platform-patterns.md` (JMS, Feign, Flyway, MDC, Saga)
- `docs/architecture/shared/multi-empresa.md` (ADR-001 schema-per-empresa)
- `docs/architecture/shared/distributed-architecture.md`
