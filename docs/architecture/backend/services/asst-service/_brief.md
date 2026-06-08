# Brief — ASST (Asset Hub)

> Fonte estruturada para `/be-architect-specs`, `/be-architect-backlog` e `/be-architect-scaffold`.
> Módulo de **núcleo de conteúdo** (`type: standard`) — repositório único de ativos de conteúdo do workspace, com versionamento, aprovação e composição assistida por IA.

| # | Item | Conteúdo |
|---|------|----------|
| 1 | **Nome canônico / Prefixo** | `asst-service` / **ASST** · pacote `com.journeyos.asst` · Gradle `:services:asst-service` |
| 2 | **Problema que resolve** | Operações de educação digital e infoprodutos produzem um volume crescente de **ativos de conteúdo** — páginas de venda, sequências de e-mail, criativos, roteiros (VSL/reels), documentos e scripts de SDR. Hoje vivem espalhados em Drive/Notion/Canva/planilhas, **sem versionamento, sem aprovação e sem reuso**: ninguém sabe qual é a versão vigente, quem aprovou, ou se um asset já validado pode ser reaproveitado em outra jornada. ASST é o **repositório único de assets** do workspace (`empresa`): catalogação, **versionamento imutável**, **workflow de aprovação** (rascunho → revisão → aprovado/publicado) e **Asset Studio** (composição/classificação assistida por IA via TechLab AI). Outros módulos (COMM, JRNY, SALE) **consomem** assets publicados como insumo (templates de mensagem, conteúdo de estágio, copy de oferta). |
| 3 | **Persona principal / secundária** | **Principal:** `HEAD_GROWTH` (Marina) — cria, organiza e submete assets; coordena o time de copy/criativo. **Secundária:** `INFOPRODUTOR` (Rafael) — **aprova/rejeita** assets (autoridade de publicação) e define padrões. **Persona-máquina:** COMM (consome assets como templates), JRNY (referencia assets em estágios de jornada) e SALE (copy de oferta/landing). |
| 4 | **Recorte do MVP (in)** | (a) **Asset CRUD + catálogo**: `asset` por `tipo_asset` (`LANDING_PAGE`, `EMAIL`, `CRIATIVO`, `ROTEIRO`, `DOCUMENTO`, `SCRIPT_SDR`) no schema `emp_<slug>`; (b) **Versionamento**: `versao_asset` imutável (revisões numeradas, conteúdo estruturado/texto + referência de binário por URL), estado `RASCUNHO`→`PUBLICADA`; (c) **Approval workflow**: máquina de estados `RASCUNHO → EM_REVISAO → APROVADO/REJEITADO → PUBLICADO`, com `aprovacao` (revisor, decisão, comentário); (d) **Asset Studio**: composição assistida (`POST /asset-studio/compose`) via TechLab AI `document_composition` (gera/edita conteúdo a partir de brief + contexto); (e) **Asset Intelligence**: tagging/classificação automática via TechLab AI + indexação no índice Elastic `assets` (dimension); (f) **Busca/listagem**: filtros por tipo/tag/estado + full-text via Elastic. |
| 5 | **Fora de escopo (MVP)** | Edição colaborativa em tempo real (co-editing/CRDT); pipeline de upload/transcoding de binários pesados (vídeo/imagem) — no MVP binários são **referenciados por URL externa**, não hospedados; entrega pública/CDN de assets; A/B testing de variantes; brand kit / design system avançado; tradução automática multilíngue; aprovação multi-nível com SLA/escalonamento (MVP é aprovação single-step). |
| 6 | **Integrações externas obrigatórias** | **TechLab AI** (HTTP — `document_composition` para o Asset Studio; classificação/tagging para Asset Intelligence); **PostgreSQL** (`emp_<slug>` — dados operacionais do tenant); **Elasticsearch** (índice dimension `assets` — busca + Asset Intelligence); **Kafka/AWS MSK** (event bus); **WRKS** (valida JWT + `AccessDecision` para autorização); **MIG** (provisiona o schema `emp_<slug>`). Binários: **referência por URL** no MVP (object storage S3 é assunção pós-MVP — ver `06`). |
| 7 | **TechLab AI / eventos** | **TechLab AI:** `document_composition` (Asset Studio — compor/editar conteúdo de asset) e classificação (Asset Intelligence — tagging). **NUNCA** chamar provider de IA direto — sempre via TechLab AI HTTP. **Produz** (Kafka): `journey-os.asset.criado`, `journey-os.asset.versao.publicada`, `journey-os.asset.aprovado`, `journey-os.asset.rejeitado`. **Consome:** `journey-os.modelo.acesso.alterado` (WRKS → invalida cache de AccessDecision), `journey-os.empresa.provisionada` (WRKS → seed inicial de catálogo de tipos por tenant). **Sync (HTTP):** consome `AccessDecision` de WRKS; provê leitura de assets publicados a COMM/JRNY/SALE (Feign `AssetQueryClient`). |
| 8 | **Evento-âncora do domínio** | **"Asset publicado"** (`journey-os.asset.versao.publicada`) — quando uma versão é aprovada e publicada, ela se torna a versão vigente disponível para consumo cross-módulo (COMM/JRNY/SALE). É o heartbeat do golden path: *criar asset → compor (Asset Studio) → submeter → aprovar → publicar*. |

---

## Notas de contexto (Journey OS)

- **Stack:** Java 21 · Spring Boot 3.5.x · Gradle 8.x (Kotlin DSL) · PostgreSQL 15+ (`emp_<slug>`) · Elasticsearch 9.x (índice `assets`) · Kafka (AWS MSK) · TechLab AI (HTTP, Docker `ghcr.io/DaniloAmaral-Dev/techlab-ai`).
- **Multi-tenancy:** `schema-per-tenant`, termo `empresa`. ASST é um serviço de negócio: **lê/escreve apenas no schema operacional `emp_<slug>`** do tenant corrente (via `EmpresaContextHolder`); **nunca** escreve em `journeyos_global`.
- **Dependência de fundação:** WRKS (identidade/RBAC/multi-tenancy) deve estar disponível — ASST valida JWT e consulta `AccessDecision`. Permissões no padrão `asst.<recurso>.<acao>` (ex.: `asst.asset.criar`, `asst.asset.aprovar`, `asst.asset.publicar`).
- **Type:** `standard` (autopilot) → A3 (specs-validate) **aplicável** (toda cláusula SHALL das specs EARS vira cenário BDD — gate D-218).
- **Particularidade arquitetural:** ASST **delega toda capacidade de IA ao TechLab AI** (RULE — nunca chamar provider direto). Asset Studio é assíncrono no caminho de composição longa; aprovação/publicação são síncronas (state machine transacional).
- **Elastic:** índice `assets` é classe **dimension** (estado atual do asset, não fato append-only); ingest `direct-java-client` (ver `stack.elastic` em `project-context.json`).

## Referências canônicas consumidas

- `docs/architecture/shared/multi-empresa.md` — ADR-001 schema-per-empresa (decisão global)
- `docs/architecture/shared/rbac/{modelo,papeis,permissoes,data-scope}.md`
- `docs/architecture/shared/modelo-dados/{empresa,relacionamentos}.md`
- `docs/architecture/integrations/techlab-ai-integration.md` — contrato BE ↔ TechLab AI (`document_composition`)
- `docs/architecture/integrations/elastic-data-contract.md` — contrato do índice `assets`
- `docs/architecture/backend/standards/services-catalog.md` (§ ASST)
