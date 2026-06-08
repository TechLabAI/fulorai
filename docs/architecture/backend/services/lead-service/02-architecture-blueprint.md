# 02 — Architecture Blueprint — LEAD (Lead Intelligence & Qualification)

> Como o LEAD se conecta ao mundo e como se organiza por dentro. Não é código — é fronteira.

## 1. System Boundary

LEAD é um microserviço **standard** (Spring Boot, hexagonal) dono do agregado **Lead** e seus
satélites (perfil, survey, regra de qualificação, score, segmento) dentro do schema operacional
`emp_<slug>` de cada empresa. Expõe API REST sob `/api/v1/leads/**`, `/api/v1/surveys/**`,
`/api/v1/qualification/**` e `/api/v1/segments/**`. Não é dono de identidade (WRKS), roteamento
(JRNY), venda (SALE) nem comunicação (COMM).

```
            ┌─────────────────────────────────────────────────────────┐
            │                      lead-service                        │
   JWT ───▶ │  api  ─▶ application ─▶ domain ◀─ infrastructure         │
 (via GWY)  │                                  │  ├─ persistence (PG)   │
            │                                  │  ├─ messaging (Kafka)  │
            │                                  │  ├─ clients (TechLab)  │
            │                                  │  └─ search (Elastic)   │
            └─────────────────────────────────────────────────────────┘
```

## 2. External Actors and Systems

| Ator / Sistema | Tipo | Interação |
|---|---|---|
| **GWY (API Gateway)** | entrada | Roteia chamadas autenticadas; injeta JWT/contexto. |
| **WRKS** | dependência sync + eventos | `AccessDecision` (Feign) para autorização `lead.*`; consome `empresa.provisionada` (seed) e `modelo.acesso.alterado` (cache). |
| **TechLab AI** | dependência sync (HTTP) | Capacidade `qualification`: interpreta texto livre (surveys/notas) → contribuições sugeridas por dimensão. **Opcional**, com circuit breaker + fallback. |
| **PostgreSQL (`emp_<slug>` + pgvector)** | persistência | Dados operacionais do tenant; embeddings opcionais para similaridade de perfil (pós-MVP). |
| **Kafka / AWS MSK** | mensageria | Publica `lead.*`; consome eventos WRKS. |
| **Elasticsearch (índice `leads`)** | busca/analytics | Indexa leads (dimension) para fila priorizada, filtros e segmentação. |
| **JRNY / SALE / COMM / INTL** | consumidores (eventos) | Reagem a `lead.qualificado` / `lead.score.atualizado`. LEAD não os conhece diretamente. |

## 3. End-to-End Flows

### Golden path — Capturar → Qualificar → Segmentar (anchor: "Lead qualificado")

1. Lead chega via `POST /api/v1/leads` (form, integração, importação) com `chave_natural` + fonte.
2. `application` resolve `EmpresaContextHolder`, aplica **dedup** (chave natural normalizada): cria ou atualiza o `lead` e o `perfil_lead`.
3. Emite `journey-os.lead.capturado`.
4. **Qualificação**: o domínio aplica `regra_qualificacao` (versão ativa) sobre os sinais do perfil → contribuições por dimensão.
5. **Assist opcional TechLab AI** (`qualification`): se houver texto livre relevante, chama a TechLab AI para sugerir contribuições; em falha/timeout, segue só com as regras (fallback).
6. Calcula o **Maturity Score (6D)** agregado + breakdown; persiste com `versao_regra` + hash dos sinais (idempotência).
7. Emite `journey-os.lead.qualificado` (e `lead.score.atualizado` em recálculos).
8. **Segmentação**: reavalia segmentos cujo predicado depende do score/perfil; em mudança, emite `lead.segmento.alterado`.
9. Indexa o lead no Elastic (`leads`) para a fila priorizada.

### Fluxos alternativos

- **Survey respondido**: `resposta_survey` atualiza `perfil_lead` → dispara recálculo de score (passos 4–9).
- **Mudança de regra** (Marina edita `regra_qualificacao`): nova versão ativa → recálculo (lote pequeno síncrono no MVP) dos leads afetados → `lead.score.atualizado`.
- **Dedup/merge**: lead duplicado detectado → merge de perfis (origem preservada) sem criar novo agregado.
- **TechLab AI indisponível**: circuit breaker abre → qualificação 100% determinística; flag `assist_ia=false` no breakdown.
- **`empresa.provisionada` recebido**: seed de regras/segmentos default no novo `emp_<slug>`.

## 4. Internal Boundaries (camadas hexagonais)

```
com.journeyos.lead
├── api/                # controllers REST, DTOs (records), @RestControllerAdvice (ProblemDetail)
├── application/        # use cases (@Service, @Transactional, EmpresaContextHolder.require())
│   └── port/{in,out}   # in: casos de uso; out: repos, TechLabQualificationPort, LeadSearchPort, LeadEventPublisherPort
├── domain/             # Lead, PerfilLead, Survey, RegraQualificacao, MaturityScore (POJO puro)
│   └── service/        # MaturityScoreCalculator, QualificationRuleEngine, SegmentEvaluator (zero Spring)
└── infrastructure/
    ├── clients/        # TechLabAiClient (HTTP, capacidade qualification)
    ├── config/         # DomainServiceConfig (@Bean dos domain services), Resilience4j, Feign
    ├── messaging/      # producer (lead.*), consumer (empresa.provisionada, modelo.acesso.alterado)
    ├── persistence/    # entity/repository/adapter (PostgreSQL emp_<slug>)
    └── search/         # adapter Elastic (índice leads) + security/EmpresaContextHolder
```

Regras de fronteira (ArchUnit): `domain` sem Spring/JPA; `@Transactional` só em `application.service`;
`api` não depende de `infrastructure`; `@FeignClient` só em `infrastructure.clients`. Ver `ADR-001`.

## 5. Cross-cutting Concerns

- **Security / multi-tenancy**: JWT validado (chave de WRKS); `EmpresaContextHolder` resolve o schema `emp_<slug>`; autorização por permissões `lead.<recurso>.<acao>` via `AccessDecision` (cache invalidado por `modelo.acesso.alterado`).
- **LGPD / privacidade**: `base_legal`/consentimento por lead; anonimização e expurgo; PII nunca em logs (MDC sem PII).
- **Observabilidade**: `correlationId` propagado (MDC); métricas de distribuição de score, taxa de fallback TechLab AI, latência de qualificação; `audit-events` emitidos para WRKS via eventos `lead.*`.
- **Resiliência**: Resilience4j (circuit breaker + timeout + retry) na chamada TechLab AI; degradação graciosa para o cálculo determinístico.
- **Idempotência**: ingestão por `chave_natural`; recálculo por (`lead_id` + `versao_regra` + hash dos sinais).

---

## Referências

- `01-architectural-vision.md` · `03-initial-domain-framing.md` · `05-persistence-model.md`
- ADRs: `adr/ADR-001..005`
- `docs/architecture/backend/standards/platform-patterns.md` (Kafka, Feign+Resilience4j, MDC)
- `docs/architecture/integrations/techlab-ai-integration.md`
