# Brief — LEAD (Lead Intelligence & Qualification)

> Fonte estruturada para `/be-architect-specs`, `/be-architect-backlog` e `/be-architect-scaffold`.
> Módulo de **domínio** (`type: standard`) — dono dos leads, do perfil, da segmentação e do **Maturity Score (6D)**.
> **Dependência:** WRKS (multi-tenancy, usuários, AccessDecision/JWT).

| # | Item | Conteúdo |
|---|------|----------|
| 1 | **Nome canônico / Prefixo** | `lead-service` / **LEAD** · pacote `com.journeyos.lead` · Gradle `:services:lead-service` |
| 2 | **Problema que resolve** | A operação de educação digital captura leads de muitas fontes (Meta Ads, Hotmart, formulários, landing pages, listas importadas) e hoje não tem **uma visão única e qualificada** de cada lead. LEAD é dono do **lead** dentro de cada `empresa`: consolida o **perfil** (dados de contato + atributos), aplica **regras de qualificação** determinísticas e calcula o **Maturity Score (6D)** — um índice multidimensional que diz *quão pronto para comprar* um lead está. Também executa **surveys** (questionários que alimentam o perfil) e mantém a **segmentação** dinâmica. O resultado é uma fila priorizada e explicável para growth (Marina) e SDRs (Lucas), e o gatilho de roteamento para JRNY. |
| 3 | **Persona principal / secundária** | **Principal:** `HEAD_GROWTH` (Marina) — desenha regras de qualificação/segmentos, monitora a saúde da base e a distribuição do Maturity Score. **Secundária:** `SDR` (Lucas) — recebe a fila priorizada de leads qualificados e precisa saber *quem priorizar e por quê* (score explicável). **Terciária:** `INFOPRODUTOR` (Rafael) — visão consolidada da qualidade da base. **Persona-máquina:** JRNY (Routing Engine) consome `lead.qualificado` para rotear; SALE consome o lead qualificado para o pipeline; INTL indexa para analytics. |
| 4 | **Recorte do MVP (in)** | (a) **Lead capture**: `POST /api/v1/leads` (ingestão idempotente por `chave_natural` = email/telefone+fonte) + dedup/merge; (b) **Perfil**: `lead` + `perfil_lead` (atributos tipados, origem, consentimento LGPD); (c) **Surveys**: definição de `survey` + `pergunta` + captura de `resposta_survey` → atualiza perfil; (d) **Qualification rules**: `regra_qualificacao` (config-driven, versionada) que mapeia sinais → contribuição por dimensão; (e) **Maturity Score (6D)**: cálculo determinístico das 6 dimensões + score agregado + **explicação** (breakdown), com **assist opcional da TechLab AI** (`qualification`); (f) **Segmentação**: `segmento` dinâmico (predicado sobre perfil+score) com reavaliação; (g) **Fila/consulta**: listagem priorizada por score com filtros por segmento; (h) **Eventos**: emite `lead.capturado`, `lead.qualificado`, `lead.score.atualizado`, `lead.segmento.alterado`. |
| 5 | **Fora de escopo (MVP)** | Roteamento/atribuição a SDR (responsabilidade de **JRNY**); pipeline de vendas/oportunidade (**SALE**); disparo de comunicação/nutrição (**COMM**); deduplicação probabilística por ML (MVP usa `chave_natural` + match exato/normalizado); enriquecimento via provedores externos pagos (Clearbit etc.); scoring preditivo treinado por tenant (MVP usa regras + assist TechLab AI estável); editor visual de regras (MVP via API/config); importação em massa com pipeline assíncrono dedicado (MVP: ingestão unitária + lote pequeno síncrono). |
| 6 | **Integrações externas obrigatórias** | **WRKS** (AccessDecision/JWT + contexto de `empresa`; provisionamento de schema `emp_<slug>` via evento `empresa.provisionada`); **PostgreSQL + pgvector** (schema operacional `emp_<slug>` — LEAD escreve só no schema do tenant); **TechLab AI** (capacidade `qualification`, via HTTP — **nunca** provider de IA direto); **Kafka / AWS MSK** (event bus); **Elasticsearch** (índice `leads`, classe *dimension* — consulta/segmentação/analytics); **journey-os-migrations (MIG)** prepara o schema. |
| 7 | **TechLab AI / eventos** | **TechLab AI: `qualification`** — assist opcional ao Maturity Score (interpreta texto livre de surveys/notas e sugere contribuições por dimensão); LEAD **degrada com graça** para o resultado determinístico das regras se a TechLab AI falhar (timeout/circuit breaker). **Produz** (Kafka/AWS MSK): `journey-os.lead.capturado`, `journey-os.lead.qualificado`, `journey-os.lead.score.atualizado`, `journey-os.lead.segmento.alterado`. **Consome:** `journey-os.empresa.provisionada` (WRKS — seed de regras/segmentos default por tenant), `journey-os.modelo.acesso.alterado` (WRKS — invalida cache de AccessDecision). *(Pós-MVP: consumir sinais de engajamento de COMM/JRNY para a dimensão Engajamento.)* |
| 8 | **Evento-âncora do domínio** | **"Lead qualificado"** (`journey-os.lead.qualificado`) — quando o Maturity Score (6D) é calculado/recalculado e o lead atinge um estado de qualificação. É o heartbeat do golden path (capturar → perfilar → qualificar → segmentar → publicar) e o gatilho cross-módulo para JRNY rotear e SALE priorizar. |

---

## Notas de contexto (Journey OS)

- **Stack:** Java 21 · Spring Boot 3.5.x · Gradle 8.x (Kotlin DSL) · PostgreSQL 15+ com **pgvector** (schema `emp_<slug>`) · Kafka (AWS MSK) · Elasticsearch 9.x (índice `leads`) · TechLab AI (HTTP).
- **Multi-tenancy:** `schema-per-tenant`, schema operacional `emp_<slug>`, termo `empresa`. LEAD **lê** identidade/autorização de WRKS (AccessDecision/JWT) e **escreve** apenas no schema do tenant resolvido por `EmpresaContextHolder`.
- **Maturity Score (6D):** índice multidimensional. Dimensões **propostas** (a validar em specs): `PERFIL` (fit/ICP), `ENGAJAMENTO`, `INTENCAO`, `CAPACIDADE` (orçamento/poder de decisão), `URGENCIA` (timing), `ADERENCIA` (aderência ao conteúdo/conhecimento). Cálculo **determinístico e explicável** (regras versionadas) com assist opcional da TechLab AI; nunca uma "caixa-preta".
- **Type:** `standard` (autopilot) → A3 (specs-validate) **aplicável** (gerar BDD a partir das specs EARS).
- **LGPD:** lead carrega PII (nome, email, telefone) → `base_legal`/consentimento por lead, suporte a anonimização/expurgo (alinhado a `_extensions.compliance.lgpd = true`).
- **Particularidade arquitetural:** scoring é **idempotente** — recalcular o mesmo lead com as mesmas regras/sinais produz o mesmo score (chave de idempotência = `lead_id` + `versao_regra` + hash dos sinais). Ver `ADR-005`.

## Referências canônicas consumidas

- `docs/architecture/shared/multi-empresa.md` — ADR-001 schema-per-empresa (decisão global)
- `docs/architecture/shared/rbac/` — papéis canônicos (`INFOPRODUTOR`/`HEAD_GROWTH`/`SDR`) + permissões `lead.*`
- `docs/architecture/shared/modelo-dados/{empresa,relacionamentos}.md`
- `docs/architecture/backend/services/wrks-service/contracts/` — AccessDecision + eventos `empresa.provisionada` / `modelo.acesso.alterado`
- `docs/architecture/integrations/techlab-ai-integration.md` — contrato TechLab AI (capacidade `qualification`)
- `docs/architecture/backend/standards/services-catalog.md` (§ LEAD)
